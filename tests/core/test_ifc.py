import pandas as pd
import pytest

from smc_ai.core.ifc import detect_ifc, latest_ifc


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


def test_detect_ifc_zero_range_candle_is_ifc():
    # high == low → range = 0 → ratio treated as 0.0
    df = _ohlcv([(1.100, 1.100, 1.100, 1.100)])
    result = detect_ifc(df)

    assert bool(result.iloc[0]["IFC"]) is True
    assert result.iloc[0]["BodyRatio"] == 0.0


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
