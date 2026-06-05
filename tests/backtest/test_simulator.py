import pandas as pd
import pytest

from smc_ai.backtest.simulator import SimulatedTrade, simulate_trade


def _ohlcv_with_tp_hit(entry: float, tp: float, sl: float) -> pd.DataFrame:
    """OHLCV where the first candle hits TP."""
    index = pd.date_range("2026-01-01 08:00:00", periods=3, freq="15min")
    return pd.DataFrame({
        "open": [entry, entry, entry],
        "high": [tp + 0.001, entry + 0.0001, entry + 0.0001],
        "low":  [entry - 0.0001, entry - 0.0001, entry - 0.0001],
        "close": [tp, entry, entry],
        "volume": [1000, 1000, 1000],
    }, index=index)


def _ohlcv_with_sl_hit(entry: float, tp: float, sl: float) -> pd.DataFrame:
    """OHLCV where the first candle hits SL."""
    index = pd.date_range("2026-01-01 08:00:00", periods=3, freq="15min")
    return pd.DataFrame({
        "open": [entry, entry, entry],
        "high": [entry + 0.0001, entry + 0.0001, entry + 0.0001],
        "low":  [sl - 0.001, entry - 0.0001, entry - 0.0001],
        "close": [sl, entry, entry],
        "volume": [1000, 1000, 1000],
    }, index=index)


def test_simulate_trade_detects_tp_hit():
    entry, tp, sl = 1.100, 1.125, 1.095
    df = _ohlcv_with_tp_hit(entry, tp, sl)

    trade = simulate_trade(
        df=df,
        entry=entry,
        stop_loss=sl,
        take_profit=tp,
        direction="buy",
        entry_index=df.index[0],
    )

    assert trade.outcome == "tp"
    assert trade.pnl_r == pytest.approx(5.0, abs=0.1)


def test_simulate_trade_detects_sl_hit():
    entry, tp, sl = 1.100, 1.125, 1.095
    df = _ohlcv_with_sl_hit(entry, tp, sl)

    trade = simulate_trade(
        df=df,
        entry=entry,
        stop_loss=sl,
        take_profit=tp,
        direction="buy",
        entry_index=df.index[0],
    )

    assert trade.outcome == "sl"
    assert trade.pnl_r == pytest.approx(-1.0, abs=0.01)


def test_simulate_trade_is_open_when_neither_hit():
    entry, tp, sl = 1.100, 1.125, 1.095
    index = pd.date_range("2026-01-01 08:00:00", periods=2, freq="15min")
    df = pd.DataFrame({
        "open": [entry, entry], "high": [1.105, 1.107],
        "low": [1.098, 1.099], "close": [1.103, 1.104], "volume": [1000, 1000],
    }, index=index)

    trade = simulate_trade(
        df=df, entry=entry, stop_loss=sl, take_profit=tp, direction="buy",
        entry_index=df.index[0],
    )

    assert trade.outcome == "open"
    assert trade.pnl_r == 0.0
