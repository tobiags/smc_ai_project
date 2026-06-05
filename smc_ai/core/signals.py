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


def generate_signals_from_multitf(
    symbol: str,
    df_d1: pd.DataFrame,
    df_h4: pd.DataFrame,
    df_m15: pd.DataFrame,
    strategy_id: str,
    strategy_version: str,
    min_rr: float = 5.0,
    stop_buffer: float = 0.0,
    confidence: float = 0.70,
) -> list[Signal]:
    """Generate real signals using the multi-timeframe WinWorld pipeline."""
    from smc_ai.core.pipeline import run_multitf_analysis

    analysis = run_multitf_analysis(
        symbol=symbol,
        df_d1=df_d1,
        df_h4=df_h4,
        df_m15=df_m15,
        min_rr=min_rr,
        stop_buffer=stop_buffer,
    )

    if not analysis.m15_entry.decision.accepted or analysis.m15_entry.levels is None:
        return []

    return [
        signal_from_entry_analysis(
            analysis=analysis.m15_entry,
            strategy_id=strategy_id,
            strategy_version=strategy_version,
            confidence=confidence,
        )
    ]
