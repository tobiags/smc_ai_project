import pandas as pd
import pytest

from smc_ai.core.pipeline import MultiTFAnalysis, run_multitf_analysis


def _ohlcv_trending_up(n: int = 100) -> pd.DataFrame:
    """Uptrending OHLCV data for testing D1 bullish bias."""
    index = pd.date_range("2026-01-01 08:00:00", periods=n, freq="D")
    base = 1.10
    closes = [base + i * 0.001 for i in range(n)]
    return pd.DataFrame(
        {
            "open": [c - 0.0005 for c in closes],
            "high": [c + 0.001 for c in closes],
            "low": [c - 0.001 for c in closes],
            "close": closes,
            "volume": [1000] * n,
        },
        index=index,
    )


def _ohlcv_flat(n: int = 50, freq: str = "h", base: float = 1.10) -> pd.DataFrame:
    """Flat OHLCV data."""
    index = pd.date_range("2026-01-01 08:00:00", periods=n, freq=freq)
    return pd.DataFrame(
        {
            "open": [base] * n,
            "high": [base + 0.001] * n,
            "low": [base - 0.001] * n,
            "close": [base] * n,
            "volume": [1000] * n,
        },
        index=index,
    )


def test_run_multitf_analysis_returns_multitf_analysis():
    df_d1 = _ohlcv_trending_up(60)
    df_h4 = _ohlcv_flat(100, freq="4h")
    df_m15 = _ohlcv_flat(200, freq="15min")

    result = run_multitf_analysis(
        symbol="EURUSD",
        df_d1=df_d1,
        df_h4=df_h4,
        df_m15=df_m15,
        min_rr=5.0,
    )

    assert isinstance(result, MultiTFAnalysis)
    assert result.symbol == "EURUSD"
    assert result.d1_bias in {"bullish", "bearish", "neutral"}
    assert isinstance(result.h4_zones, list)
    assert isinstance(result.m15_entry, object)


def test_run_multitf_analysis_captures_d1_bias():
    df_d1 = _ohlcv_trending_up(60)
    df_h4 = _ohlcv_flat(100, freq="4h")
    df_m15 = _ohlcv_flat(200, freq="15min")

    result = run_multitf_analysis("EURUSD", df_d1, df_h4, df_m15)

    # Uptrending D1 should produce bullish bias
    assert result.d1_bias == "bullish"


def test_run_multitf_analysis_entry_rejected_without_h4_confluence():
    """Without H4 zones, M15 confirmed_pois will be empty → entry rejected."""
    df_d1 = _ohlcv_flat(60, freq="D")
    df_h4 = _ohlcv_flat(100, freq="4h")     # flat → no OBs/FVGs
    df_m15 = _ohlcv_flat(200, freq="15min")

    result = run_multitf_analysis("EURUSD", df_d1, df_h4, df_m15)

    assert result.m15_entry.decision.accepted is False


def test_multitf_analysis_to_dict_is_serialisable():
    df_d1 = _ohlcv_trending_up(60)
    df_h4 = _ohlcv_flat(100, freq="4h")
    df_m15 = _ohlcv_flat(200, freq="15min")

    result = run_multitf_analysis("EURUSD", df_d1, df_h4, df_m15)
    data = result.to_dict()

    assert "symbol" in data
    assert "d1_bias" in data
    assert "h4_zones" in data
    assert "m15_entry" in data
    assert "idm_confirmed" in data
    assert "m15_ifc" in data       # Phase 5
    assert "b4_entry" in data      # Phase 5


def test_multitf_analysis_exposes_ifc_and_b4():
    df_d1 = _ohlcv_trending_up(60)
    df_h4 = _ohlcv_flat(100, freq="4h")
    df_m15 = _ohlcv_flat(200, freq="15min")

    result = run_multitf_analysis("EURUSD", df_d1, df_h4, df_m15)

    # m15_ifc is None or a dict with body_ratio
    assert result.m15_ifc is None or "body_ratio" in result.m15_ifc
    # b4_entry is None or a dict with schema/direction keys
    assert result.b4_entry is None or result.b4_entry["schema"] == "b4_ifc_sweep_extreme"
