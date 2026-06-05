import numpy as np
import pandas as pd
import pytest

from smc_ai.backtest.models import BacktestResult
from smc_ai.backtest.walkforward import run_walkforward_backtest


def _make_trending(n: int, freq: str, trend: float = 0.001) -> pd.DataFrame:
    index = pd.date_range("2024-01-01 08:00:00", periods=n, freq=freq)
    closes = [1.10 + i * trend for i in range(n)]
    wave = [np.sin(i / 10) * 0.002 for i in range(n)]
    c = [closes[i] + wave[i] for i in range(n)]
    return pd.DataFrame({
        "open": [v - 0.0003 for v in c],
        "high": [v + 0.0008 for v in c],
        "low": [v - 0.0008 for v in c],
        "close": c,
        "volume": [1000] * n,
    }, index=index)


def test_run_walkforward_backtest_returns_backtest_result():
    df_d1 = _make_trending(300, "D")
    df_h4 = _make_trending(600, "4h")
    df_m15 = _make_trending(1200, "15min")

    result = run_walkforward_backtest(
        symbol="EURUSD",
        df_d1=df_d1,
        df_h4=df_h4,
        df_m15=df_m15,
        scan_step=40,
        m15_lookback=200,
        d1_lookback=60,
        h4_lookback=100,
        sim_horizon=100,
    )

    assert isinstance(result, BacktestResult)
    assert result.symbol == "EURUSD"
    assert result.run_id.startswith("wf-EURUSD-")
    assert "total_trades" in result.kpis
    assert "win_rate" in result.kpis
    assert "profit_factor" in result.kpis


def test_run_walkforward_backtest_trades_have_outcome_and_pnl_r():
    df_d1 = _make_trending(300, "D")
    df_h4 = _make_trending(600, "4h")
    df_m15 = _make_trending(1200, "15min")

    result = run_walkforward_backtest(
        symbol="EURUSD",
        df_d1=df_d1,
        df_h4=df_h4,
        df_m15=df_m15,
        scan_step=40,
        m15_lookback=200,
        d1_lookback=60,
        h4_lookback=100,
        sim_horizon=100,
    )

    for trade in result.trades:
        assert "outcome" in trade
        assert trade["outcome"] in {"tp", "sl", "open"}
        assert "pnl_r" in trade
        assert "rr" in trade


def test_run_walkforward_backtest_no_lookahead_no_exception():
    """Walk-forward must not raise even with minimal data at boundaries."""
    df_d1 = _make_trending(100, "D")
    df_h4 = _make_trending(200, "4h")
    df_m15 = _make_trending(500, "15min")

    result = run_walkforward_backtest(
        symbol="EURUSD",
        df_d1=df_d1,
        df_h4=df_h4,
        df_m15=df_m15,
        scan_step=40,
        m15_lookback=200,
        d1_lookback=50,
        h4_lookback=80,
        sim_horizon=50,
    )

    assert isinstance(result, BacktestResult)
    assert result.kpis["total_trades"] >= 0
