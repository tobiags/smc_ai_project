import numpy as np
import pandas as pd

from smc_ai.data.models import validate_ohlcv


try:
    from smartmoneyconcepts import smc as _smc
except ModuleNotFoundError:
    _smc = None


def calculate_swing_highs_lows(df: pd.DataFrame, swing_length: int = 5) -> pd.DataFrame:
    normalized = validate_ohlcv(df)
    if swing_length < 1:
        raise ValueError("swing_length must be at least 1")

    if _smc is not None:
        return _smc.swing_highs_lows(normalized, swing_length=swing_length)

    return _fallback_swing_highs_lows(normalized, swing_length=swing_length)


def calculate_fvg(
    df: pd.DataFrame,
    join_consecutive: bool = True,
    lookback_period: int | None = None,
    body_multiplier: float = 1.5,
) -> pd.DataFrame:
    normalized = validate_ohlcv(df)
    if lookback_period is not None and lookback_period < 1:
        raise ValueError("lookback_period must be at least 1 when provided")
    if body_multiplier <= 0:
        raise ValueError("body_multiplier must be positive")

    if _smc is not None and lookback_period is None:
        return _smc.fvg(normalized, join_consecutive=join_consecutive)

    return _fallback_fvg(normalized, lookback_period=lookback_period, body_multiplier=body_multiplier)


def _fallback_swing_highs_lows(df: pd.DataFrame, swing_length: int) -> pd.DataFrame:
    n = len(df)
    highs = df["high"].to_numpy(dtype=float)
    lows = df["low"].to_numpy(dtype=float)
    high_low = np.zeros(n, dtype=int)
    level = np.full(n, pd.NA, dtype=object)

    window = 2 * swing_length + 1
    if n >= window:
        from numpy.lib.stride_tricks import sliding_window_view

        win_max = sliding_window_view(highs, window).max(axis=1)
        win_min = sliding_window_view(lows, window).min(axis=1)
        centers = np.arange(swing_length, n - swing_length)
        # A bar is a swing high if its high equals the window max; the elif
        # ordering of the original loop means "high wins ties over low".
        is_high = highs[centers] == win_max
        is_low = (lows[centers] == win_min) & ~is_high

        high_low[centers[is_high]] = 1
        high_low[centers[is_low]] = -1
        for pos in centers[is_high]:
            level[pos] = float(highs[pos])
        for pos in centers[is_low]:
            level[pos] = float(lows[pos])

    result = pd.DataFrame({"HighLow": high_low}, index=df.index)
    result["Level"] = level
    return result


def _fallback_fvg(
    df: pd.DataFrame,
    lookback_period: int | None = None,
    body_multiplier: float = 1.5,
) -> pd.DataFrame:
    n = len(df)
    fvg = np.zeros(n, dtype=int)
    top = np.full(n, pd.NA, dtype=object)
    bottom = np.full(n, pd.NA, dtype=object)

    if n >= 3:
        highs = df["high"].to_numpy(dtype=float)
        lows = df["low"].to_numpy(dtype=float)

        positions = np.arange(2, n)
        bull = lows[2:] > highs[:-2]
        bear = highs[2:] < lows[:-2]

        if lookback_period is not None:
            bodies = np.abs(df["close"].to_numpy(dtype=float) - df["open"].to_numpy(dtype=float))
            significant = np.ones(n - 2, dtype=bool)
            for i, pos in enumerate(range(2, n)):
                start = max(0, pos - 1 - lookback_period)
                previous = bodies[start : pos - 1]
                if previous.size:
                    avg_body = float(previous.mean())
                    avg_body = avg_body if avg_body > 0 else 0.001
                    significant[i] = bodies[pos - 1] > avg_body * body_multiplier
            bull &= significant
            bear &= significant

        for pos in positions[bull]:
            fvg[pos] = 1
            bottom[pos] = float(highs[pos - 2])
            top[pos] = float(lows[pos])
        for pos in positions[bear]:
            fvg[pos] = -1
            bottom[pos] = float(highs[pos])
            top[pos] = float(lows[pos - 2])

    result = pd.DataFrame({"FVG": fvg}, index=df.index)
    result["Top"] = top
    result["Bottom"] = bottom
    result["MitigatedIndex"] = pd.NA
    return result
