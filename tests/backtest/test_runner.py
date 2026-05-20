from smc_ai.backtest.models import BacktestResult
from smc_ai.backtest.runner import run_sample_backtest


def test_run_sample_backtest_returns_result_with_kpis():
    result = run_sample_backtest(symbol="EURUSD", bars=240)

    assert isinstance(result, BacktestResult)
    assert result.symbol == "EURUSD"
    assert result.run_id.startswith("sample-EURUSD-")
    assert result.kpis["total_trades"] > 0
    assert "win_rate" in result.kpis
    assert "profit_factor" in result.kpis
    assert result.equity_curve
    assert result.trades


def test_backtest_result_to_dict_is_json_ready():
    result = run_sample_backtest(symbol="EURUSD", bars=160)

    data = result.to_dict()

    assert data["run_id"] == result.run_id
    assert data["symbol"] == "EURUSD"
    assert isinstance(data["trades"], list)
    assert isinstance(data["equity_curve"], list)
