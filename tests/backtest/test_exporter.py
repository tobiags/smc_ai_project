from smc_ai.backtest.exporter import list_results, read_result, write_result
from smc_ai.backtest.runner import run_sample_backtest


def test_write_read_and_list_result(tmp_path):
    result = run_sample_backtest("EURUSD", bars=160)

    path = write_result(result, tmp_path)
    loaded = read_result(path)
    listed = list_results(tmp_path)

    assert path.exists()
    assert loaded.run_id == result.run_id
    assert loaded.symbol == "EURUSD"
    assert listed[0].run_id == result.run_id


def test_list_results_returns_empty_for_missing_directory(tmp_path):
    missing_dir = tmp_path / "missing"

    assert list_results(missing_dir) == []


def test_read_result_accepts_legacy_json_without_analyses(tmp_path):
    path = tmp_path / "legacy.json"
    path.write_text(
        """
        {
          "run_id": "legacy",
          "symbol": "EURUSD",
          "kpis": {"total_trades": 0},
          "equity_curve": [],
          "trades": []
        }
        """,
        encoding="utf-8",
    )

    result = read_result(path)

    assert result.run_id == "legacy"
    assert result.analyses == []
