from smc_ai.core.signals import Signal, detect_initial_signals
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
