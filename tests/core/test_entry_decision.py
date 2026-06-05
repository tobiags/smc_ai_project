import pandas as pd

from smc_ai.core.entry_decision import evaluate_entry_decision
from smc_ai.core.poi import PoiZone


def _event(event: str, direction: str) -> pd.Series:
    return pd.Series(
        {
            "Event": event,
            "Direction": direction,
            "BreakType": "close" if event != "SWEEP" else "wick",
            "BrokenStructure": "HH" if direction == "bullish" else "HL",
            "BrokenLevel": 1.12,
        }
    )


def test_evaluate_entry_decision_accepts_aligned_bos_with_confirmed_poi():
    poi = PoiZone("OB", "bullish", top=1.120, bottom=1.100, source_index="m15")

    decision = evaluate_entry_decision(
        symbol="EURUSD",
        timestamp=pd.Timestamp("2026-01-01 08:00:00"),
        bias_direction="bullish",
        session_allowed=True,
        structure_event=_event("BOS", "bullish"),
        confirmed_pois=[poi],
    )

    assert decision.accepted is True
    assert decision.direction == "buy"
    assert decision.schema == "m15_bos_poi_confirmation"
    assert decision.reason == "structure, bias, session, and POI are aligned"
    assert decision.poi == poi


def test_evaluate_entry_decision_rejects_when_session_is_not_allowed():
    poi = PoiZone("OB", "bullish", top=1.120, bottom=1.100, source_index="m15")

    decision = evaluate_entry_decision(
        symbol="EURUSD",
        timestamp=pd.Timestamp("2026-01-01 03:00:00"),
        bias_direction="bullish",
        session_allowed=False,
        structure_event=_event("BOS", "bullish"),
        confirmed_pois=[poi],
    )

    assert decision.accepted is False
    assert decision.reason == "session is not allowed"


def test_evaluate_entry_decision_rejects_sweep_only_break():
    poi = PoiZone("OB", "bullish", top=1.120, bottom=1.100, source_index="m15")

    decision = evaluate_entry_decision(
        symbol="EURUSD",
        timestamp=pd.Timestamp("2026-01-01 08:00:00"),
        bias_direction="bullish",
        session_allowed=True,
        structure_event=_event("SWEEP", "bullish"),
        confirmed_pois=[poi],
    )

    assert decision.accepted is False
    assert decision.reason == "structure event is not a body-close BOS/ChoCh"


def test_evaluate_entry_decision_rejects_bias_mismatch():
    poi = PoiZone("OB", "bullish", top=1.120, bottom=1.100, source_index="m15")

    decision = evaluate_entry_decision(
        symbol="EURUSD",
        timestamp=pd.Timestamp("2026-01-01 08:00:00"),
        bias_direction="bearish",
        session_allowed=True,
        structure_event=_event("BOS", "bullish"),
        confirmed_pois=[poi],
    )

    assert decision.accepted is False
    assert decision.reason == "structure direction conflicts with directional bias"


def test_evaluate_entry_decision_rejects_missing_confirmed_poi():
    decision = evaluate_entry_decision(
        symbol="EURUSD",
        timestamp=pd.Timestamp("2026-01-01 08:00:00"),
        bias_direction="bullish",
        session_allowed=True,
        structure_event=_event("BOS", "bullish"),
        confirmed_pois=[],
    )

    assert decision.accepted is False
    assert decision.reason == "no confirmed POI"


def test_evaluate_entry_decision_rejects_when_idm_not_confirmed():
    poi = PoiZone("OB", "bullish", top=1.120, bottom=1.100, source_index="m15")
    event = pd.Series({
        "Event": "BOS", "Direction": "bullish", "BreakType": "close",
        "BrokenStructure": "HH", "BrokenLevel": 1.12,
    })

    decision = evaluate_entry_decision(
        symbol="EURUSD",
        timestamp=pd.Timestamp("2026-01-01 08:00:00"),
        bias_direction="bullish",
        session_allowed=True,
        structure_event=event,
        confirmed_pois=[poi],
        idm_confirmed=False,
    )

    assert decision.accepted is False
    assert "IDM" in decision.reason
