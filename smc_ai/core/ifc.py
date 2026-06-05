import pandas as pd

from smc_ai.data.models import validate_ohlcv


def detect_ifc(df: pd.DataFrame, body_ratio_threshold: float = 0.4) -> pd.DataFrame:
    """Detect Internal Formation Candles (IFC).

    An IFC is a candle whose body is small relative to its total range.
    WinWorld uses body/range < 0.4 as the IFC threshold.

    Returns a DataFrame with:
        IFC        bool  : True if the candle qualifies as an IFC
        BodyRatio  float : abs(close - open) / abs(high - low) (0.0 for doji)
    Indexed same as df.
    """
    if not 0 < body_ratio_threshold <= 1:
        raise ValueError("body_ratio_threshold must be in (0, 1]")

    normalized = validate_ohlcv(df)
    body_ratios = _compute_body_ratios(normalized)

    result = pd.DataFrame(
        {
            "IFC": body_ratios < body_ratio_threshold,
            "BodyRatio": body_ratios.round(4),
        },
        index=normalized.index,
    )
    return result


def latest_ifc(ifc: pd.DataFrame) -> dict[str, object] | None:
    """Return the most recent IFC candle as a dict, or None if no IFC found."""
    hits = ifc[ifc["IFC"]]
    if hits.empty:
        return None
    row = hits.iloc[-1]
    return {
        "index": hits.index[-1],
        "body_ratio": float(row["BodyRatio"]),
    }


def _compute_body_ratios(df: pd.DataFrame) -> pd.Series:
    candle_range = df["high"] - df["low"]
    body = (df["close"] - df["open"]).abs()
    ratios = pd.Series(0.0, index=df.index)
    nonzero = candle_range > 0
    ratios[nonzero] = body[nonzero] / candle_range[nonzero]
    return ratios
