from smc_ai.backtest.exporter import read_result
from smc_ai.main import generate_sample_run


def test_generate_sample_run_writes_json(tmp_path):
    path = generate_sample_run(symbol="EURUSD", results_dir=tmp_path)

    assert path.exists()
    assert path.suffix == ".json"

    result = read_result(path)
    assert result.symbol == "EURUSD"
