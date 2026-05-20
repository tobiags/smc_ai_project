import json
from pathlib import Path

from smc_ai.backtest.models import BacktestResult


def write_result(result: BacktestResult, results_dir: str | Path) -> Path:
    directory = Path(results_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{result.run_id}.json"
    path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    return path


def read_result(path: str | Path) -> BacktestResult:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return BacktestResult(
        run_id=data["run_id"],
        symbol=data["symbol"],
        kpis=data["kpis"],
        equity_curve=data["equity_curve"],
        trades=data["trades"],
    )


def list_results(results_dir: str | Path) -> list[BacktestResult]:
    directory = Path(results_dir)
    if not directory.exists():
        return []

    return [read_result(path) for path in sorted(directory.glob("*.json"), reverse=True)]
