from dataclasses import dataclass

import pandas as pd

from smc_ai.data.models import validate_ohlcv


@dataclass(frozen=True)
class PreviousHighLow:
    timestamp: pd.Timestamp
    high: float
    low: float


@dataclass(frozen=True)
class BiasSnapshot:
    direction: str
    lookback: int
    first_close: float
    last_close: float
    previous_high: float
    previous_low: float


def previous_high_low(df: pd.DataFrame) -> PreviousHighLow:
    normalized = validate_ohlcv(df)
    if len(normalized) < 2:
        raise ValueError("Previous high/low requires at least two candles")

    previous = normalized.iloc[-2]
    return PreviousHighLow(
        timestamp=normalized.index[-2],
        high=float(previous["high"]),
        low=float(previous["low"]),
    )


def calculate_directional_bias(df: pd.DataFrame, lookback: int = 20) -> BiasSnapshot:
    normalized = validate_ohlcv(df)
    if lookback < 2:
        raise ValueError("Bias lookback must be at least 2")
    if len(normalized) < lookback:
        raise ValueError(f"Bias calculation requires at least {lookback} candles")

    window = normalized.tail(lookback)
    first_close = float(window.iloc[0]["close"])
    last_close = float(window.iloc[-1]["close"])
    if last_close > first_close:
        direction = "bullish"
    elif last_close < first_close:
        direction = "bearish"
    else:
        direction = "neutral"

    levels = previous_high_low(normalized)
    return BiasSnapshot(
        direction=direction,
        lookback=lookback,
        first_close=first_close,
        last_close=last_close,
        previous_high=levels.high,
        previous_low=levels.low,
    )
