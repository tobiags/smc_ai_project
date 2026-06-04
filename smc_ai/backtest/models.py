from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class BacktestResult:
    run_id: str
    symbol: str
    kpis: dict[str, float | int | str]
    equity_curve: list[dict[str, float | str]]
    trades: list[dict[str, object]]
    analyses: list[dict[str, object]]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
