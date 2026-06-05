"""Tests for order_manager — MT5 is mocked."""
import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest


def _make_mt5_mock() -> ModuleType:
    mt5 = MagicMock()
    tick = MagicMock()
    tick.bid = 1.10000
    tick.ask = 1.10010
    mt5.symbol_info_tick.return_value = tick
    mt5.ORDER_TYPE_BUY   = 0
    mt5.ORDER_TYPE_SELL  = 1
    mt5.TRADE_ACTION_DEAL = 1
    mt5.ORDER_TIME_GTC   = 0
    mt5.ORDER_FILLING_IOC = 1
    mt5.TRADE_RETCODE_DONE = 10009

    result = MagicMock()
    result.retcode  = mt5.TRADE_RETCODE_DONE
    result.order    = 987654
    result.comment  = "Request executed"
    mt5.order_send.return_value = result
    return mt5


# ── compute_volume ────────────────────────────────────────────────────────────

def test_compute_volume_standard():
    from smc_ai.bridge.order_manager import compute_volume

    # $10,000 balance, 1% risk, 10 pip SL → $100 risk / ($10 * 10 pips) = 1.0 lot
    vol = compute_volume(
        balance=10_000,
        risk_pct=0.01,
        entry=1.10000,
        stop_loss=1.09900,   # 10 pips
    )
    assert vol == pytest.approx(1.0, abs=0.01)


def test_compute_volume_clamps_to_min():
    from smc_ai.bridge.order_manager import compute_volume

    # risk_amount = 10,000 × 0.000001 = $0.01
    # risk_pips = |1.10 - 1.09| × 10000 = 1000
    # raw_lots = 0.01 / (1000 × 10) = 0.000001 → clamped to min_lot 0.01
    vol = compute_volume(10_000, 0.000001, 1.10, 1.09)
    assert vol == 0.01


def test_compute_volume_zero_distance_returns_min():
    from smc_ai.bridge.order_manager import compute_volume

    vol = compute_volume(10_000, 0.01, 1.10, 1.10)   # entry == SL → degenerate
    assert vol == 0.01


# ── build_order ───────────────────────────────────────────────────────────────

def test_build_order_buy_uses_ask_price():
    mt5_mock = _make_mt5_mock()
    with patch.dict(sys.modules, {"MetaTrader5": mt5_mock}):
        import importlib
        import smc_ai.bridge.order_manager as mod
        importlib.reload(mod)
        req = mod.build_order("EURUSD", "buy", 0.1, 1.095, 1.150, "a1")

    assert req["price"] == 1.10010   # ask
    assert req["type"]  == 0          # ORDER_TYPE_BUY
    assert req["sl"]    == 1.095
    assert req["tp"]    == 1.150
    assert req["volume"] == 0.1


def test_build_order_sell_uses_bid_price():
    mt5_mock = _make_mt5_mock()
    with patch.dict(sys.modules, {"MetaTrader5": mt5_mock}):
        import importlib
        import smc_ai.bridge.order_manager as mod
        importlib.reload(mod)
        req = mod.build_order("EURUSD", "sell", 0.1, 1.115, 1.050, "b4")

    assert req["price"] == 1.10000   # bid
    assert req["type"]  == 1          # ORDER_TYPE_SELL


def test_build_order_invalid_direction_raises():
    mt5_mock = _make_mt5_mock()
    with patch.dict(sys.modules, {"MetaTrader5": mt5_mock}):
        import importlib
        import smc_ai.bridge.order_manager as mod
        importlib.reload(mod)
        with pytest.raises(ValueError, match="direction must be"):
            mod.build_order("EURUSD", "long", 0.1, 1.09, 1.15, "a1")


# ── send_order ────────────────────────────────────────────────────────────────

def test_send_order_success():
    mt5_mock = _make_mt5_mock()
    with patch.dict(sys.modules, {"MetaTrader5": mt5_mock}):
        import importlib
        import smc_ai.bridge.order_manager as mod
        importlib.reload(mod)
        request = {"symbol": "EURUSD", "volume": 0.1}
        result = mod.send_order(request)

    assert result.success is True
    assert result.order_id == 987654


def test_send_order_failure():
    mt5_mock = _make_mt5_mock()
    failed = MagicMock()
    failed.retcode  = 10006   # TRADE_RETCODE_REJECT
    failed.order    = 0
    failed.comment  = "No money"
    mt5_mock.order_send.return_value = failed

    with patch.dict(sys.modules, {"MetaTrader5": mt5_mock}):
        import importlib
        import smc_ai.bridge.order_manager as mod
        importlib.reload(mod)
        result = mod.send_order({})

    assert result.success is False
    assert result.order_id is None
    assert "No money" in result.comment
