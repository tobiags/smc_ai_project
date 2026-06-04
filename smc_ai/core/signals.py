from dataclasses import asdict, dataclass

import pandas as pd

from smc_ai.core.entry_pipeline import EntryAnalysis
from smc_ai.core.sessions import is_trade_allowed
from smc_ai.core.strategy_profiles import get_strategy_profile


@dataclass(frozen=True)
class Signal:
    symbol: str
    strategy_id: str
    strategy_version: str
    timestamp: str
    direction: str
    schema: str
    entry: float
    stop_loss: float
    take_profit: float
    confidence: float

    @property
    def rr(self) -> float:
        risk = abs(self.entry - self.stop_loss)
        reward = abs(self.take_profit - self.entry)
        return round(reward / risk, 2)

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["rr"] = self.rr
        return data


def detect_initial_signals(symbol: str, df: pd.DataFrame, min_rr: float) -> list[Signal]:
    """Create deterministic sample signals before the full WinWorld engine exists."""

    profile = get_strategy_profile("winworld_smc_v1")
    signals: list[Signal] = []
    for index_position in range(20, len(df), 40):
        timestamp = df.index[index_position]
        if not is_trade_allowed(timestamp):
            continue

        close = float(df.iloc[index_position]["close"])
        stop_loss = close - 0.001
        take_profit = close + (close - stop_loss) * min_rr
        signal = Signal(
            symbol=symbol,
            strategy_id=profile.strategy_id,
            strategy_version=profile.version,
            timestamp=timestamp.isoformat(),
            direction="buy",
            schema="sample_smc_long",
            entry=round(close, 5),
            stop_loss=round(stop_loss, 5),
            take_profit=round(take_profit, 5),
            confidence=0.50,
        )
        if signal.rr >= min_rr:
            signals.append(signal)

    return signals


def signal_from_entry_analysis(
    analysis: EntryAnalysis,
    strategy_id: str,
    strategy_version: str,
    confidence: float = 0.70,
) -> Signal:
    if not analysis.decision.accepted or analysis.levels is None:
        raise ValueError("signal requires an accepted analysis with trade levels")
    if analysis.decision.direction is None or analysis.decision.schema is None:
        raise ValueError("signal requires decision direction and schema")

    return Signal(
        symbol=analysis.decision.symbol,
        strategy_id=strategy_id,
        strategy_version=strategy_version,
        timestamp=analysis.decision.timestamp,
        direction=analysis.decision.direction,
        schema=analysis.decision.schema,
        entry=analysis.levels.entry,
        stop_loss=analysis.levels.stop_loss,
        take_profit=analysis.levels.take_profit,
        confidence=confidence,
    )
