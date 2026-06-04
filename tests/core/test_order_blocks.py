import pandas as pd

from smc_ai.core.order_blocks import detect_order_blocks


def _ohlcv(
    highs: list[float],
    lows: list[float],
    opens: list[float],
    closes: list[float],
) -> pd.DataFrame:
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


def test_detect_order_blocks_marks_bullish_ob_when_liquidity_take_is_followed_by_fvg():
    df = _ohlcv(
        highs=[1.105, 1.100, 1.120, 1.160],
        lows=[1.090, 1.080, 1.100, 1.130],
        opens=[1.100, 1.095, 1.105, 1.135],
        closes=[1.095, 1.085, 1.115, 1.150],
    )

    order_blocks = detect_order_blocks(df)

    assert order_blocks.loc[df.index[1], "OB"] == 1
    assert order_blocks.loc[df.index[1], "Top"] == 1.100
    assert order_blocks.loc[df.index[1], "Bottom"] == 1.080
    assert order_blocks.loc[df.index[1], "SourceFVGIndex"] == df.index[3]


def test_detect_order_blocks_marks_bearish_ob_when_liquidity_take_is_followed_by_fvg():
    df = _ohlcv(
        highs=[1.150, 1.165, 1.145, 1.120],
        lows=[1.135, 1.140, 1.125, 1.090],
        opens=[1.140, 1.160, 1.140, 1.115],
        closes=[1.145, 1.150, 1.130, 1.095],
    )

    order_blocks = detect_order_blocks(df)

    assert order_blocks.loc[df.index[1], "OB"] == -1
    assert order_blocks.loc[df.index[1], "Top"] == 1.165
    assert order_blocks.loc[df.index[1], "Bottom"] == 1.140
    assert order_blocks.loc[df.index[1], "SourceFVGIndex"] == df.index[3]


def test_detect_order_blocks_rejects_candle_without_liquidity_take():
    df = _ohlcv(
        highs=[1.105, 1.100, 1.120, 1.160],
        lows=[1.080, 1.090, 1.100, 1.130],
        opens=[1.100, 1.095, 1.105, 1.135],
        closes=[1.095, 1.092, 1.115, 1.150],
    )

    order_blocks = detect_order_blocks(df)

    assert order_blocks["OB"].sum() == 0


def test_detect_order_blocks_rejects_liquidity_take_without_following_fvg():
    df = _ohlcv(
        highs=[1.105, 1.100, 1.120, 1.125],
        lows=[1.090, 1.080, 1.095, 1.099],
        opens=[1.100, 1.095, 1.105, 1.115],
        closes=[1.095, 1.085, 1.115, 1.110],
    )

    order_blocks = detect_order_blocks(df)

    assert order_blocks["OB"].sum() == 0
