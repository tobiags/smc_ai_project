from smc_ai.backtest.models import BacktestResult
from smc_ai.backtest.runner import run_sample_backtest


def test_run_sample_backtest_returns_result_with_kpis():
    result = run_sample_backtest(symbol="EURUSD", bars=240)

    assert isinstance(result, BacktestResult)
    assert result.symbol == "EURUSD"
    assert result.run_id.startswith("sample-EURUSD-")
    assert result.kpis["strategy_id"] == "winworld_smc_v1"
    assert result.kpis["strategy_version"] == "0.1"
    assert result.kpis["total_trades"] > 0
    assert "win_rate" in result.kpis
    assert "profit_factor" in result.kpis
    assert "expectancy_r" in result.kpis
    assert result.equity_curve
    assert result.trades


def test_backtest_result_to_dict_is_json_ready():
    result = run_sample_backtest(symbol="EURUSD", bars=160)

    data = result.to_dict()

    assert data["run_id"] == result.run_id
    assert data["symbol"] == "EURUSD"
    assert data["trades"][0]["strategy_id"] == "winworld_smc_v1"
    assert isinstance(data["trades"], list)
    assert isinstance(data["equity_curve"], list)
    assert isinstance(data["analyses"], list)


def test_run_sample_backtest_includes_decision_analysis_log():
    result = run_sample_backtest(symbol="EURUSD", bars=160)

    assert result.analyses
    assert all("decision" in analysis for analysis in result.analyses)
    assert all("rejection_reason" in analysis for analysis in result.analyses)


def test_run_sample_backtest_uses_real_pnl_simulation():
    """Trades must carry real simulate_trade outcome, not hard-coded 100/-20 values."""
    result = run_sample_backtest(symbol="EURUSD", bars=240)

    for trade in result.trades:
        assert "outcome" in trade
        assert trade["outcome"] in {"tp", "sl", "open"}
        assert "pnl_r" in trade
        pnl_r = float(trade["pnl_r"])
        # pnl_r must be a genuine R-unit value: TP≈+RR, SL=-1.0, open=0.0
        assert pnl_r not in {100.0, -20.0}, "found old hard-coded fake PnL"
