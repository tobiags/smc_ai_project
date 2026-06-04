from smc_ai.core.entry_decision import EntryDecision
from smc_ai.core.entry_pipeline import EntryAnalysis
from smc_ai.core.poi import PoiZone
from smc_ai.core.risk import TradeLevels
from smc_ai.core.signals import Signal, detect_initial_signals, signal_from_entry_analysis
from smc_ai.reports.sample_results import make_sample_ohlcv


def test_signal_rr_calculation():
    signal = Signal(
        symbol="EURUSD",
        strategy_id="winworld_smc_v1",
        strategy_version="0.1",
        timestamp="2026-01-01T08:00:00",
        direction="buy",
        schema="sample",
        entry=1.1000,
        stop_loss=1.0990,
        take_profit=1.1050,
        confidence=0.5,
    )

    assert signal.rr == 5.0


def test_signal_to_dict_includes_rr():
    signal = Signal(
        symbol="EURUSD",
        strategy_id="winworld_smc_v1",
        strategy_version="0.1",
        timestamp="2026-01-01T08:00:00",
        direction="sell",
        schema="sample",
        entry=1.1000,
        stop_loss=1.1010,
        take_profit=1.0950,
        confidence=0.5,
    )

    data = signal.to_dict()

    assert data["direction"] == "sell"
    assert data["strategy_id"] == "winworld_smc_v1"
    assert data["rr"] == 5.0


def test_detect_initial_signals_returns_only_min_rr_signals():
    df = make_sample_ohlcv(120)

    signals = detect_initial_signals("EURUSD", df, min_rr=5.0)

    assert signals
    assert all(signal.rr >= 5.0 for signal in signals)
    assert all(signal.strategy_id == "winworld_smc_v1" for signal in signals)


def test_detect_initial_signals_uses_trade_sessions_only():
    df = make_sample_ohlcv(120)

    signals = detect_initial_signals("EURUSD", df, min_rr=5.0)

    assert all("T07:" <= signal.timestamp[10:16] or signal.timestamp[11:13] != "03" for signal in signals)
    assert all(signal.schema == "sample_smc_long" for signal in signals)


def test_signal_from_entry_analysis_converts_accepted_analysis_to_signal():
    poi = PoiZone("OB", "bullish", top=1.120, bottom=1.100, source_index="m15")
    analysis = EntryAnalysis(
        decision=EntryDecision(
            symbol="EURUSD",
            timestamp="2026-01-01T08:00:00",
            accepted=True,
            direction="buy",
            schema="m15_bos_poi_confirmation",
            reason="structure, bias, session, and POI are aligned",
            poi=poi,
        ),
        levels=TradeLevels(entry=1.125, stop_loss=1.100, take_profit=1.250, rr=5.0),
        rejection_reason=None,
    )

    signal = signal_from_entry_analysis(
        analysis,
        strategy_id="winworld_smc_v1",
        strategy_version="0.1",
        confidence=0.75,
    )

    assert signal == Signal(
        symbol="EURUSD",
        strategy_id="winworld_smc_v1",
        strategy_version="0.1",
        timestamp="2026-01-01T08:00:00",
        direction="buy",
        schema="m15_bos_poi_confirmation",
        entry=1.125,
        stop_loss=1.100,
        take_profit=1.250,
        confidence=0.75,
    )


def test_signal_from_entry_analysis_rejects_incomplete_analysis():
    analysis = EntryAnalysis(
        decision=EntryDecision(
            symbol="EURUSD",
            timestamp="2026-01-01T08:00:00",
            accepted=False,
            direction=None,
            schema=None,
            reason="no confirmed POI",
            poi=None,
        ),
        levels=None,
        rejection_reason="no confirmed POI",
    )

    try:
        signal_from_entry_analysis(
            analysis,
            strategy_id="winworld_smc_v1",
            strategy_version="0.1",
        )
    except ValueError as exc:
        assert "accepted analysis with trade levels" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
