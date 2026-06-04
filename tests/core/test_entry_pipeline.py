import pandas as pd

from smc_ai.core.entry_pipeline import build_entry_analysis
from smc_ai.core.poi import PoiZone


def _event(event: str, direction: str) -> pd.Series:
    return pd.Series(
        {
            "Event": event,
            "Direction": direction,
            "BreakType": "close",
            "BrokenStructure": "HH" if direction == "bullish" else "LL",
            "BrokenLevel": 1.12,
        }
    )


def test_build_entry_analysis_returns_trade_levels_when_decision_is_accepted():
    poi = PoiZone("OB", "bullish", top=1.120, bottom=1.100, source_index="m15")

    analysis = build_entry_analysis(
        symbol="EURUSD",
        timestamp=pd.Timestamp("2026-01-01 08:00:00"),
        entry_price=1.125,
        bias_direction="bullish",
        session_allowed=True,
        structure_event=_event("BOS", "bullish"),
        confirmed_pois=[poi],
        min_rr=5.0,
    )

    assert analysis.decision.accepted is True
    assert analysis.levels is not None
    assert analysis.levels.entry == 1.125
    assert analysis.levels.stop_loss == 1.100
    assert analysis.levels.take_profit == 1.250
    assert analysis.rejection_reason is None


def test_build_entry_analysis_returns_rejection_when_decision_is_rejected():
    analysis = build_entry_analysis(
        symbol="EURUSD",
        timestamp=pd.Timestamp("2026-01-01 03:00:00"),
        entry_price=1.125,
        bias_direction="bullish",
        session_allowed=False,
        structure_event=_event("BOS", "bullish"),
        confirmed_pois=[PoiZone("OB", "bullish", top=1.120, bottom=1.100, source_index="m15")],
        min_rr=5.0,
    )

    assert analysis.decision.accepted is False
    assert analysis.levels is None
    assert analysis.rejection_reason == "session is not allowed"


def test_build_entry_analysis_rejects_when_trade_levels_are_invalid():
    analysis = build_entry_analysis(
        symbol="EURUSD",
        timestamp=pd.Timestamp("2026-01-01 08:00:00"),
        entry_price=1.099,
        bias_direction="bullish",
        session_allowed=True,
        structure_event=_event("BOS", "bullish"),
        confirmed_pois=[PoiZone("OB", "bullish", top=1.120, bottom=1.100, source_index="m15")],
        min_rr=5.0,
    )

    assert analysis.decision.accepted is True
    assert analysis.levels is None
    assert analysis.rejection_reason == "entry must be beyond the structural stop"
