from typing import Any

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


def detect_b4_entry(
    df: pd.DataFrame,
    ifc: pd.DataFrame,
    structure: pd.DataFrame,
) -> dict[str, Any] | None:
    """Detect schema B4: IFC aggressively sweeps a swing extreme → immediate entry.

    WinWorld B4: an IFC candle whose wick exceeds the most recent swing high or low
    but whose close stays on the opposite side → liquidity sweep complete, enter immediately.

    Args:
        df:        OHLCV data (same index as ifc and structure).
        ifc:       DataFrame from detect_ifc().
        structure: DataFrame from label_market_structure() with HighLow and Level columns.

    Returns dict with keys: schema, direction, entry, stop, ifc_index, swept_level.
    Returns None if no B4 setup is found.
    """
    ifc_hits = ifc[ifc["IFC"]]
    if ifc_hits.empty:
        return None

    ifc_idx = ifc_hits.index[-1]
    ifc_candle = df.loc[ifc_idx]

    # Consider swing points strictly before the IFC candle
    prior = structure.loc[:ifc_idx].iloc[:-1]

    highs = prior[(prior["HighLow"] == 1) & prior["Level"].notna()]
    lows = prior[(prior["HighLow"] == -1) & prior["Level"].notna()]

    if not highs.empty:
        last_high = float(highs.iloc[-1]["Level"])
        # Wick swept above swing high, close returned below → bearish B4
        if float(ifc_candle["high"]) > last_high and float(ifc_candle["close"]) < last_high:
            return {
                "schema": "b4_ifc_sweep_extreme",
                "direction": "sell",
                "entry": float(ifc_candle["close"]),
                "stop": float(ifc_candle["high"]),
                "ifc_index": ifc_idx,
                "swept_level": last_high,
            }

    if not lows.empty:
        last_low = float(lows.iloc[-1]["Level"])
        # Wick swept below swing low, close returned above → bullish B4
        if float(ifc_candle["low"]) < last_low and float(ifc_candle["close"]) > last_low:
            return {
                "schema": "b4_ifc_sweep_extreme",
                "direction": "buy",
                "entry": float(ifc_candle["close"]),
                "stop": float(ifc_candle["low"]),
                "ifc_index": ifc_idx,
                "swept_level": last_low,
            }

    return None


def _compute_body_ratios(df: pd.DataFrame) -> pd.Series:
    candle_range = df["high"] - df["low"]
    body = (df["close"] - df["open"]).abs()
    ratios = pd.Series(0.0, index=df.index)
    nonzero = candle_range > 0
    ratios[nonzero] = body[nonzero] / candle_range[nonzero]
    return ratios
