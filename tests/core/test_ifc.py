import pandas as pd
import pytest

from smc_ai.core.ifc import detect_b2_entry, detect_b4_entry, detect_ifc, latest_ifc


def _ohlcv(rows: list[tuple[float, float, float, float]]) -> pd.DataFrame:
    """Build OHLCV from (open, high, low, close) tuples."""
    index = pd.date_range("2026-01-01 07:00:00", periods=len(rows), freq="15min")
    return pd.DataFrame(
        [{"open": o, "high": h, "low": l, "close": c, "volume": 1000} for o, h, l, c in rows],
        index=index,
    )


def test_detect_ifc_flags_small_body_candle():
    # body = |1.105 - 1.100| = 0.005, range = |1.120 - 1.090| = 0.030 → ratio 0.167 < 0.4
    df = _ohlcv([(1.100, 1.120, 1.090, 1.105)])
    result = detect_ifc(df)

    assert bool(result.iloc[0]["IFC"]) is True
    assert abs(result.iloc[0]["BodyRatio"] - 0.1667) < 0.001


def test_detect_ifc_does_not_flag_large_body_candle():
    # body = |1.118 - 1.100| = 0.018, range = |1.120 - 1.098| = 0.022 → ratio 0.818 > 0.4
    df = _ohlcv([(1.100, 1.120, 1.098, 1.118)])
    result = detect_ifc(df)

    assert bool(result.iloc[0]["IFC"]) is False
    assert result.iloc[0]["BodyRatio"] > 0.4


def test_detect_ifc_doji_is_always_ifc():
    # open == close → body = 0 → ratio = 0.0 < 0.4
    df = _ohlcv([(1.100, 1.120, 1.080, 1.100)])
    result = detect_ifc(df)

    assert bool(result.iloc[0]["IFC"]) is True
    assert result.iloc[0]["BodyRatio"] == 0.0


def test_detect_ifc_zero_range_candle_is_not_ifc():
    # high == low → no rejection information → must NOT qualify as IFC
    df = _ohlcv([(1.100, 1.100, 1.100, 1.100)])
    result = detect_ifc(df)

    assert bool(result.iloc[0]["IFC"]) is False
    assert result.iloc[0]["BodyRatio"] == 1.0


def test_detect_ifc_invalid_threshold_raises():
    df = _ohlcv([(1.100, 1.120, 1.090, 1.105)])
    with pytest.raises(ValueError):
        detect_ifc(df, body_ratio_threshold=0.0)


def test_latest_ifc_returns_most_recent():
    df = _ohlcv([
        (1.100, 1.120, 1.090, 1.118),   # large body — NOT IFC
        (1.100, 1.120, 1.090, 1.105),   # small body — IFC
        (1.100, 1.120, 1.090, 1.118),   # large body — NOT IFC
        (1.100, 1.120, 1.090, 1.103),   # small body — IFC (most recent)
    ])
    result = detect_ifc(df)
    info = latest_ifc(result)

    assert info is not None
    assert info["index"] == df.index[3]


def test_latest_ifc_returns_none_when_no_ifc():
    df = _ohlcv([
        (1.100, 1.120, 1.098, 1.118),   # all large body
        (1.100, 1.120, 1.098, 1.117),
    ])
    result = detect_ifc(df)

    assert latest_ifc(result) is None


# ── B4 schema ────────────────────────────────────────────────────────────────

def _structure(high_low: list[int], levels: list) -> pd.DataFrame:
    index = pd.date_range("2026-01-01 07:00:00", periods=len(high_low), freq="15min")
    return pd.DataFrame({
        "HighLow": high_low,
        "Level": [float(l) if l is not None else pd.NA for l in levels],
        "Structure": [pd.NA] * len(high_low),
    }, index=index)


def test_detect_b4_entry_bearish_when_ifc_wick_sweeps_high():
    # Candle 0: swing high at 1.12 (HighLow=1)
    # Candle 1: IFC — wick sweeps above 1.12 (high=1.125), close returns below (close=1.118)
    df = _ohlcv([
        (1.110, 1.120, 1.100, 1.115),   # not IFC (big body)
        (1.115, 1.125, 1.112, 1.118),   # IFC: body=0.003, range=0.013 → ratio≈0.23 < 0.4
    ])
    structure = _structure([1, 0], [1.12, None])
    ifc = detect_ifc(df)

    result = detect_b4_entry(df, ifc, structure)

    assert result is not None
    assert result["schema"] == "b4_ifc_sweep_extreme"
    assert result["direction"] == "sell"
    assert result["entry"] == 1.118
    assert result["stop"] == 1.125
    assert result["swept_level"] == 1.12


def test_detect_b4_entry_bullish_when_ifc_wick_sweeps_low():
    # Candle 0: swing low at 1.09 (HighLow=-1)
    # Candle 1: IFC — wick dips below 1.09 (low=1.085), close returns above (close=1.092)
    df = _ohlcv([
        (1.100, 1.110, 1.090, 1.095),   # not IFC
        (1.095, 1.098, 1.085, 1.092),   # IFC: body=0.003, range=0.013 → ratio≈0.23 < 0.4
    ])
    structure = _structure([-1, 0], [1.09, None])
    ifc = detect_ifc(df)

    result = detect_b4_entry(df, ifc, structure)

    assert result is not None
    assert result["direction"] == "buy"
    assert result["entry"] == 1.092
    assert result["stop"] == 1.085


def test_detect_b4_entry_returns_none_when_ifc_does_not_sweep():
    # IFC wick stays below swing high
    df = _ohlcv([
        (1.110, 1.120, 1.100, 1.115),
        (1.115, 1.118, 1.112, 1.117),   # IFC, but wick 1.118 < swing high 1.12 → no sweep
    ])
    structure = _structure([1, 0], [1.12, None])
    ifc = detect_ifc(df)

    result = detect_b4_entry(df, ifc, structure)

    assert result is None


def _idm_df(idm_values: list[int], swept_levels: list) -> pd.DataFrame:
    index = pd.date_range("2026-01-01 07:00:00", periods=len(idm_values), freq="15min")
    return pd.DataFrame({
        "IDM": idm_values,
        "SweptLevel": [float(s) if s is not None else pd.NA for s in swept_levels],
        "ConfirmIndex": [pd.NA] * len(idm_values),
    }, index=index)


def test_detect_b2_entry_bearish_when_ifc_sweeps_above_idm_level():
    # IDM swept level = 1.12. IFC wick > 1.12, close < 1.12 → bearish B2
    df = _ohlcv([
        (1.110, 1.118, 1.105, 1.115),  # not IFC (big body)
        (1.115, 1.125, 1.112, 1.118),  # IFC: body=0.003/range=0.013 → 0.23 < 0.4
    ])
    idm = _idm_df([0, -1], [None, 1.12])
    ifc = detect_ifc(df)

    result = detect_b2_entry(df, ifc, idm)

    assert result is not None
    assert result["schema"] == "b2_ifc_sweep_idm"
    assert result["direction"] == "sell"
    assert result["entry_zone_top"] == 1.125
    assert result["swept_idm_level"] == 1.12


def test_detect_b2_entry_bullish_when_ifc_sweeps_below_idm_level():
    # IDM swept level = 1.09. IFC wick < 1.09, close > 1.09 → bullish B2
    df = _ohlcv([
        (1.100, 1.108, 1.093, 1.095),
        (1.095, 1.098, 1.085, 1.092),  # IFC: body=0.003/range=0.013 → 0.23 < 0.4
    ])
    idm = _idm_df([0, 1], [None, 1.09])
    ifc = detect_ifc(df)

    result = detect_b2_entry(df, ifc, idm)

    assert result is not None
    assert result["direction"] == "buy"
    assert result["entry_zone_bottom"] == 1.085
    assert result["swept_idm_level"] == 1.09


def test_detect_b2_entry_returns_none_when_no_confirmed_idm():
    df = _ohlcv([
        (1.110, 1.118, 1.105, 1.115),
        (1.115, 1.125, 1.112, 1.118),
    ])
    idm = _idm_df([0, 0], [None, None])
    ifc = detect_ifc(df)

    assert detect_b2_entry(df, ifc, idm) is None


def test_detect_b4_entry_returns_none_when_no_ifc():
    df = _ohlcv([
        (1.100, 1.120, 1.090, 1.118),   # large body — not IFC
        (1.100, 1.120, 1.090, 1.117),
    ])
    structure = _structure([1, 0], [1.10, None])
    ifc = detect_ifc(df)

    assert detect_b4_entry(df, ifc, structure) is None
