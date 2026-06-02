import pandas as pd

from smc_ai.core.indicators import calculate_fvg, calculate_swing_highs_lows


def _ohlcv(
    highs: list[float],
    lows: list[float],
    closes: list[float] | None = None,
    opens: list[float] | None = None,
) -> pd.DataFrame:
    closes = closes or [(high + low) / 2 for high, low in zip(highs, lows, strict=True)]
    opens = opens or closes
    index = pd.date_range("2026-01-01 07:00:00", periods=len(highs), freq="15min")
    return pd.DataFrame(
        {
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": [100] * len(highs),
        },
        index=index,
    )


def test_calculate_swing_highs_lows_marks_local_extremes():
    df = _ohlcv(
        highs=[1.10, 1.12, 1.15, 1.13, 1.11],
        lows=[1.08, 1.09, 1.10, 1.07, 1.09],
    )

    swings = calculate_swing_highs_lows(df, swing_length=1)

    assert swings.loc[df.index[2], "HighLow"] == 1
    assert swings.loc[df.index[2], "Level"] == 1.15
    assert swings.loc[df.index[3], "HighLow"] == -1
    assert swings.loc[df.index[3], "Level"] == 1.07


def test_calculate_swing_highs_lows_leaves_edges_unmarked():
    df = _ohlcv(
        highs=[1.15, 1.12, 1.10],
        lows=[1.08, 1.09, 1.07],
    )

    swings = calculate_swing_highs_lows(df, swing_length=1)

    assert swings.iloc[0]["HighLow"] == 0
    assert swings.iloc[-1]["HighLow"] == 0


def test_calculate_fvg_detects_bullish_gap():
    df = _ohlcv(
        highs=[1.10, 1.12, 1.18],
        lows=[1.08, 1.09, 1.15],
    )

    fvg = calculate_fvg(df)

    assert fvg.loc[df.index[2], "FVG"] == 1
    assert fvg.loc[df.index[2], "Bottom"] == 1.10
    assert fvg.loc[df.index[2], "Top"] == 1.15


def test_calculate_fvg_detects_bearish_gap():
    df = _ohlcv(
        highs=[1.18, 1.16, 1.10],
        lows=[1.15, 1.14, 1.05],
    )

    fvg = calculate_fvg(df)

    assert fvg.loc[df.index[2], "FVG"] == -1
    assert fvg.loc[df.index[2], "Bottom"] == 1.10
    assert fvg.loc[df.index[2], "Top"] == 1.15


def test_calculate_fvg_returns_zero_when_no_gap():
    df = _ohlcv(
        highs=[1.10, 1.12, 1.11],
        lows=[1.08, 1.09, 1.09],
    )

    fvg = calculate_fvg(df)

    assert fvg["FVG"].sum() == 0


def test_calculate_fvg_can_require_significant_middle_body():
    df = _ohlcv(
        highs=[1.10, 1.18, 1.21],
        lows=[1.08, 1.11, 1.15],
        closes=[1.09, 1.17, 1.19],
        opens=[1.089, 1.11, 1.18],
    )

    fvg = calculate_fvg(df, lookback_period=1, body_multiplier=1.5)

    assert fvg.loc[df.index[2], "FVG"] == 1


def test_calculate_fvg_rejects_gap_when_middle_body_is_too_small():
    df = _ohlcv(
        highs=[1.10, 1.121, 1.21],
        lows=[1.08, 1.119, 1.15],
        closes=[1.09, 1.1205, 1.19],
        opens=[1.089, 1.1195, 1.18],
    )

    fvg = calculate_fvg(df, lookback_period=1, body_multiplier=1.5)

    assert fvg.loc[df.index[2], "FVG"] == 0
