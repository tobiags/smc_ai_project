from dataclasses import dataclass

import pandas as pd

from smc_ai.core.entry_decision import EntryDecision, evaluate_entry_decision
from smc_ai.core.poi import PoiZone
from smc_ai.core.risk import TradeLevels, calculate_trade_levels


@dataclass(frozen=True)
class EntryAnalysis:
    decision: EntryDecision
    levels: TradeLevels | None
    rejection_reason: str | None


def build_entry_analysis(
    symbol: str,
    timestamp: pd.Timestamp,
    entry_price: float,
    bias_direction: str,
    session_allowed: bool,
    structure_event: pd.Series,
    confirmed_pois: list[PoiZone],
    min_rr: float,
    stop_buffer: float = 0.0,
) -> EntryAnalysis:
    decision = evaluate_entry_decision(
        symbol=symbol,
        timestamp=timestamp,
        bias_direction=bias_direction,
        session_allowed=session_allowed,
        structure_event=structure_event,
        confirmed_pois=confirmed_pois,
    )
    if not decision.accepted:
        return EntryAnalysis(decision=decision, levels=None, rejection_reason=decision.reason)

    if decision.direction is None or decision.poi is None:
        return EntryAnalysis(decision=decision, levels=None, rejection_reason="accepted decision is incomplete")

    try:
        levels = calculate_trade_levels(
            entry=entry_price,
            direction=decision.direction,
            poi=decision.poi,
            min_rr=min_rr,
            buffer=stop_buffer,
        )
    except ValueError as exc:
        return EntryAnalysis(decision=decision, levels=None, rejection_reason=str(exc))

    return EntryAnalysis(decision=decision, levels=levels, rejection_reason=None)
