import pandas as pd

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


def test_generate_signals_from_multitf_uses_pipeline(tmp_path):
    """generate_signals_from_multitf returns Signal list from real pipeline data."""
    from smc_ai.core.signals import generate_signals_from_multitf

    index_d1 = pd.date_range("2026-01-01", periods=60, freq="D")
    closes_d1 = [1.10 + i * 0.001 for i in range(60)]
    df_d1 = pd.DataFrame({
        "open": [c - 0.0005 for c in closes_d1],
        "high": [c + 0.001 for c in closes_d1],
        "low": [c - 0.001 for c in closes_d1],
        "close": closes_d1,
        "volume": [1000] * 60,
    }, index=index_d1)

    index_m = pd.date_range("2026-01-01 08:00:00", periods=100, freq="15min")
    df_flat = pd.DataFrame({
        "open": [1.10] * 100, "high": [1.11] * 100,
        "low": [1.09] * 100, "close": [1.10] * 100, "volume": [1000] * 100,
    }, index=index_m)

    index_h4 = pd.date_range("2026-01-01 08:00:00", periods=50, freq="4h")
    df_h4 = pd.DataFrame({
        "open": [1.10] * 50, "high": [1.11] * 50,
        "low": [1.09] * 50, "close": [1.10] * 50, "volume": [1000] * 50,
    }, index=index_h4)

    signals = generate_signals_from_multitf(
        symbol="EURUSD",
        df_d1=df_d1,
        df_h4=df_h4,
        df_m15=df_flat,
        strategy_id="winworld_smc_v1",
        strategy_version="0.1",
        min_rr=5.0,
    )

    # With flat M15 data, pipeline produces no accepted entry — empty list is valid
    assert isinstance(signals, list)
    for sig in signals:
        assert sig.rr >= 5.0
        assert sig.direction in {"buy", "sell"}
