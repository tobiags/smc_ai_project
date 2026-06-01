import pandas as pd
import pytest

from smc_ai.core.bias import BiasSnapshot, calculate_directional_bias, previous_high_low


def _daily_df(closes: list[float]) -> pd.DataFrame:
    index = pd.date_range("2026-01-01", periods=len(closes), freq="1D")
    return pd.DataFrame(
        {
            "open": closes,
            "high": [close + 0.01 for close in closes],
            "low": [close - 0.01 for close in closes],
            "close": closes,
            "volume": [100] * len(closes),
        },
        index=index,
    )


def test_previous_high_low_uses_previous_completed_candle():
    df = _daily_df([1.10, 1.12, 1.11])

    levels = previous_high_low(df)

    assert levels.high == pytest.approx(1.13)
    assert levels.low == pytest.approx(1.11)
    assert levels.timestamp == pd.Timestamp("2026-01-02")


def test_calculate_directional_bias_detects_bullish_context():
    df = _daily_df([1.10, 1.11, 1.12, 1.13, 1.14])

    bias = calculate_directional_bias(df, lookback=5)

    assert isinstance(bias, BiasSnapshot)
    assert bias.direction == "bullish"
    assert bias.previous_high == pytest.approx(1.14)
    assert bias.previous_low == pytest.approx(1.12)


def test_calculate_directional_bias_detects_bearish_context():
    df = _daily_df([1.14, 1.13, 1.12, 1.11, 1.10])

    bias = calculate_directional_bias(df, lookback=5)

    assert bias.direction == "bearish"


def test_calculate_directional_bias_detects_neutral_context():
    df = _daily_df([1.10, 1.10, 1.10, 1.10, 1.10])

    bias = calculate_directional_bias(df, lookback=5)

    assert bias.direction == "neutral"


def test_previous_high_low_requires_two_candles():
    df = _daily_df([1.10])

    try:
        previous_high_low(df)
    except ValueError as exc:
        assert "at least two candles" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
