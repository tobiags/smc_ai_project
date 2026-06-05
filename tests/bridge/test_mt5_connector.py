"""Tests for MT5 connector — MT5 terminal is mocked throughout."""
import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest


# ── helpers to build a fake MetaTrader5 module ───────────────────────────────

def _make_mt5_mock(rates_ok: bool = True) -> ModuleType:
    mt5 = MagicMock()
    mt5.initialize.return_value = True
    mt5.last_error.return_value = (0, "OK")

    if rates_ok:
        # numpy structured array that MT5 copy_rates_from_pos returns
        dtype = [
            ("time", "i8"), ("open", "f8"), ("high", "f8"),
            ("low", "f8"), ("close", "f8"), ("tick_volume", "i8"),
            ("spread", "i4"), ("real_volume", "i8"),
        ]
        n = 5
        data = np.zeros(n, dtype=dtype)
        base_ts = 1_700_000_000
        for i in range(n):
            data[i]["time"]        = base_ts + i * 900   # 15-min steps
            data[i]["open"]        = 1.10 + i * 0.001
            data[i]["high"]        = 1.11 + i * 0.001
            data[i]["low"]         = 1.09 + i * 0.001
            data[i]["close"]       = 1.105 + i * 0.001
            data[i]["tick_volume"] = 1000
        mt5.copy_rates_from_pos.return_value = data
    else:
        mt5.copy_rates_from_pos.return_value = None

    mt5.TIMEFRAME_M1  = 1
    mt5.TIMEFRAME_M5  = 5
    mt5.TIMEFRAME_M15 = 15
    mt5.TIMEFRAME_M30 = 30
    mt5.TIMEFRAME_H1  = 16385
    mt5.TIMEFRAME_H4  = 16388
    mt5.TIMEFRAME_D1  = 16408
    mt5.TIMEFRAME_W1  = 32769
    return mt5


# ── tests ─────────────────────────────────────────────────────────────────────

def test_connect_calls_initialize():
    mt5_mock = _make_mt5_mock()
    with patch.dict(sys.modules, {"MetaTrader5": mt5_mock}):
        # Re-import to pick up the mock
        import importlib
        import smc_ai.bridge.mt5_connector as mod
        importlib.reload(mod)
        mod.connect()
        mt5_mock.initialize.assert_called_once()


def test_connect_with_credentials():
    mt5_mock = _make_mt5_mock()
    with patch.dict(sys.modules, {"MetaTrader5": mt5_mock}):
        import importlib
        import smc_ai.bridge.mt5_connector as mod
        importlib.reload(mod)
        mod.connect(login=12345, password="secret", server="Demo")
        mt5_mock.initialize.assert_called_once_with(
            login=12345, password="secret", server="Demo"
        )


def test_connect_raises_when_initialize_fails():
    mt5_mock = _make_mt5_mock()
    mt5_mock.initialize.return_value = False
    mt5_mock.last_error.return_value = (5, "No connection")
    with patch.dict(sys.modules, {"MetaTrader5": mt5_mock}):
        import importlib
        import smc_ai.bridge.mt5_connector as mod
        importlib.reload(mod)
        with pytest.raises(RuntimeError, match="MT5 initialize failed"):
            mod.connect()


def test_fetch_ohlcv_returns_dataframe_with_correct_columns():
    mt5_mock = _make_mt5_mock(rates_ok=True)
    with patch.dict(sys.modules, {"MetaTrader5": mt5_mock}):
        import importlib
        import smc_ai.bridge.mt5_connector as mod
        importlib.reload(mod)
        df = mod.fetch_ohlcv("EURUSD", "M15", bars=5)

    assert list(df.columns) == ["open", "high", "low", "close", "volume"]
    assert len(df) == 5
    assert isinstance(df.index, pd.DatetimeIndex)


def test_fetch_ohlcv_raises_when_no_data():
    mt5_mock = _make_mt5_mock(rates_ok=False)
    with patch.dict(sys.modules, {"MetaTrader5": mt5_mock}):
        import importlib
        import smc_ai.bridge.mt5_connector as mod
        importlib.reload(mod)
        with pytest.raises(RuntimeError, match="No data returned"):
            mod.fetch_ohlcv("MISSING", "M15", bars=10)


def test_fetch_ohlcv_raises_for_unknown_timeframe():
    mt5_mock = _make_mt5_mock()
    with patch.dict(sys.modules, {"MetaTrader5": mt5_mock}):
        import importlib
        import smc_ai.bridge.mt5_connector as mod
        importlib.reload(mod)
        with pytest.raises(ValueError, match="Unknown timeframe"):
            mod.fetch_ohlcv("EURUSD", "X99", bars=10)
