import pandas as pd

from smc_ai.core.entry_pipeline import build_entry_analysis, scan_latest_m15_entry
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


def _ohlcv(highs: list[float], lows: list[float], closes: list[float]) -> pd.DataFrame:
    index = pd.date_range("2026-01-01 07:00:00", periods=len(highs), freq="15min")
    return pd.DataFrame(
        {
            "open": closes,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": [100] * len(highs),
        },
        index=index,
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


def test_scan_latest_m15_entry_uses_latest_body_close_structure_event():
    df = _ohlcv(
        highs=[1.10, 1.08, 1.12, 1.10, 1.13],
        lows=[1.06, 1.05, 1.09, 1.08, 1.11],
        closes=[1.08, 1.07, 1.11, 1.09, 1.125],
    )
    structure = pd.DataFrame(
        {
            "HighLow": [1, -1, 1, -1, 0],
            "Level": [1.10, 1.05, 1.12, 1.08, pd.NA],
            "Structure": ["H", "L", "HH", "HL", pd.NA],
        },
        index=df.index,
    )
    poi = PoiZone("OB", "bullish", top=1.120, bottom=1.100, source_index="m15")

    analysis = scan_latest_m15_entry(
        symbol="EURUSD",
        df_m15=df,
        bias_direction="bullish",
        confirmed_pois=[poi],
        min_rr=5.0,
        structure=structure,
    )

    assert analysis.decision.accepted is True
    assert analysis.decision.schema == "m15_bos_poi_confirmation"
    assert analysis.levels is not None
    assert analysis.levels.entry == 1.125


def test_scan_latest_m15_entry_rejects_when_no_structure_event_exists():
    df = _ohlcv(
        highs=[1.10, 1.08, 1.09],
        lows=[1.06, 1.05, 1.07],
        closes=[1.08, 1.07, 1.08],
    )

    analysis = scan_latest_m15_entry(
        symbol="EURUSD",
        df_m15=df,
        bias_direction="bullish",
        confirmed_pois=[PoiZone("OB", "bullish", top=1.120, bottom=1.100, source_index="m15")],
        min_rr=5.0,
    )

    assert analysis.decision.accepted is False
    assert analysis.rejection_reason == "no recent structure event"
