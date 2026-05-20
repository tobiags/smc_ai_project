from pathlib import Path

from smc_ai.backtest.exporter import write_result
from smc_ai.backtest.runner import run_sample_backtest
from smc_ai.config import get_settings


def generate_sample_run(symbol: str = "EURUSD", results_dir: str | Path | None = None) -> Path:
    settings = get_settings()
    target_dir = Path(results_dir) if results_dir is not None else settings.results_dir
    result = run_sample_backtest(symbol=symbol)
    return write_result(result, target_dir)


if __name__ == "__main__":
    output = generate_sample_run()
    print(f"Wrote sample result: {output}")
