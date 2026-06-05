from dataclasses import dataclass

import pandas as pd

from smc_ai.core.poi import PoiZone


@dataclass(frozen=True)
class EntryDecision:
    symbol: str
    timestamp: str
    accepted: bool
    direction: str | None
    schema: str | None
    reason: str
    poi: PoiZone | None

    def to_dict(self) -> dict[str, object]:
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "accepted": self.accepted,
            "direction": self.direction,
            "schema": self.schema,
            "reason": self.reason,
            "poi": self.poi.to_dict() if self.poi is not None else None,
        }


def evaluate_entry_decision(
    symbol: str,
    timestamp: pd.Timestamp,
    bias_direction: str,
    session_allowed: bool,
    structure_event: pd.Series,
    confirmed_pois: list[PoiZone],
    idm_confirmed: bool = True,
) -> EntryDecision:
    if not idm_confirmed:
        return _reject(symbol, timestamp, "no confirmed IDM for this leg")

    if not session_allowed:
        return _reject(symbol, timestamp, "session is not allowed")

    event = str(structure_event.get("Event", ""))
    break_type = str(structure_event.get("BreakType", ""))
    event_direction = str(structure_event.get("Direction", ""))

    if event not in {"BOS", "CHOCH"} or break_type != "close":
        return _reject(symbol, timestamp, "structure event is not a body-close BOS/ChoCh")

    if event_direction not in {"bullish", "bearish"}:
        return _reject(symbol, timestamp, "structure direction is missing")

    if bias_direction != event_direction:
        return _reject(symbol, timestamp, "structure direction conflicts with directional bias")

    matching_poi = _first_matching_poi(event_direction, confirmed_pois)
    if matching_poi is None:
        return _reject(symbol, timestamp, "no confirmed POI")

    return EntryDecision(
        symbol=symbol,
        timestamp=timestamp.isoformat(),
        accepted=True,
        direction="buy" if event_direction == "bullish" else "sell",
        schema=f"m15_{event.lower()}_poi_confirmation",
        reason="structure, bias, session, and POI are aligned",
        poi=matching_poi,
    )


def _first_matching_poi(direction: str, pois: list[PoiZone]) -> PoiZone | None:
    return next((poi for poi in pois if poi.direction == direction), None)


def _reject(symbol: str, timestamp: pd.Timestamp, reason: str) -> EntryDecision:
    return EntryDecision(
        symbol=symbol,
        timestamp=timestamp.isoformat(),
        accepted=False,
        direction=None,
        schema=None,
        reason=reason,
        poi=None,
    )
