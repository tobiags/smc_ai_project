from dataclasses import dataclass

import pandas as pd

from smc_ai.core.entry_decision import EntryDecision, evaluate_entry_decision
from smc_ai.core.market_structure import detect_structure_events
from smc_ai.core.poi import PoiZone
from smc_ai.core.risk import TradeLevels, calculate_trade_levels
from smc_ai.core.sessions import is_trade_allowed
from smc_ai.data.models import validate_ohlcv


@dataclass(frozen=True)
class EntryAnalysis:
    decision: EntryDecision
    levels: TradeLevels | None
    rejection_reason: str | None

    def to_dict(self) -> dict[str, object]:
        return {
            "decision": self.decision.to_dict(),
            "levels": self.levels.to_dict() if self.levels is not None else None,
            "rejection_reason": self.rejection_reason,
        }


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
    idm_confirmed: bool = True,
) -> EntryAnalysis:
    decision = evaluate_entry_decision(
        symbol=symbol,
        timestamp=timestamp,
        bias_direction=bias_direction,
        session_allowed=session_allowed,
        structure_event=structure_event,
        confirmed_pois=confirmed_pois,
        idm_confirmed=idm_confirmed,
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


def scan_latest_m15_entry(
    symbol: str,
    df_m15: pd.DataFrame,
    bias_direction: str,
    confirmed_pois: list[PoiZone],
    min_rr: float,
    stop_buffer: float = 0.0,
    structure: pd.DataFrame | None = None,
    idm_confirmed: bool = True,
) -> EntryAnalysis:
    normalized = validate_ohlcv(df_m15)
    events = detect_structure_events(normalized, structure=structure)
    latest_event = _latest_actionable_event(events)
    timestamp = normalized.index[-1]

    if latest_event is None:
        decision = EntryDecision(
            symbol=symbol,
            timestamp=timestamp.isoformat(),
            accepted=False,
            direction=None,
            schema=None,
            reason="no recent structure event",
            poi=None,
        )
        return EntryAnalysis(decision=decision, levels=None, rejection_reason=decision.reason)

    return build_entry_analysis(
        symbol=symbol,
        timestamp=latest_event.name,
        entry_price=float(normalized.loc[latest_event.name, "close"]),
        bias_direction=bias_direction,
        session_allowed=is_trade_allowed(latest_event.name),
        structure_event=latest_event,
        confirmed_pois=confirmed_pois,
        min_rr=min_rr,
        stop_buffer=stop_buffer,
        idm_confirmed=idm_confirmed,
    )


def _latest_actionable_event(events: pd.DataFrame) -> pd.Series | None:
    candidates = events[events["Event"].isin({"BOS", "CHOCH"})]
    if candidates.empty:
        return None
    return candidates.iloc[-1]
