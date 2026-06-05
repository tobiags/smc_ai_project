from typing import Any

import pandas as pd


def detect_smt(
    structure_a: pd.DataFrame,
    structure_b: pd.DataFrame,
) -> dict[str, Any] | None:
    """Detect SMT (Smart Money Trap) divergence between two correlated instruments.

    SMT = instrument A makes a new extreme while instrument B fails to confirm,
    signalling the new extreme on A is a liquidity grab (false breakout/breakdown).

    WinWorld:
    - Bearish SMT : A makes HH (higher high), B makes LH (lower high) → expect reversal down
    - Bullish SMT : A makes LL (lower low),  B makes HL (higher low)  → expect reversal up

    Args:
        structure_a: DataFrame from label_market_structure() for instrument A.
        structure_b: DataFrame from label_market_structure() for instrument B.

    Returns dict with keys: type, description, level_a, level_b, or None.
    """
    highs_a = _swing_levels(structure_a, direction=1)
    highs_b = _swing_levels(structure_b, direction=1)
    lows_a = _swing_levels(structure_a, direction=-1)
    lows_b = _swing_levels(structure_b, direction=-1)

    # Bearish SMT: A made HH, B made LH (divergence at the top)
    if len(highs_a) >= 2 and len(highs_b) >= 2:
        last_h_a, prev_h_a = float(highs_a[-1]), float(highs_a[-2])
        last_h_b, prev_h_b = float(highs_b[-1]), float(highs_b[-2])
        if last_h_a > prev_h_a and last_h_b < prev_h_b:
            return {
                "type": "bearish_smt",
                "description": "A made HH while B made LH — buy-side liquidity trap on A",
                "level_a": last_h_a,
                "level_b": last_h_b,
            }

    # Bullish SMT: A made LL, B made HL (divergence at the bottom)
    if len(lows_a) >= 2 and len(lows_b) >= 2:
        last_l_a, prev_l_a = float(lows_a[-1]), float(lows_a[-2])
        last_l_b, prev_l_b = float(lows_b[-1]), float(lows_b[-2])
        if last_l_a < prev_l_a and last_l_b > prev_l_b:
            return {
                "type": "bullish_smt",
                "description": "A made LL while B made HL — sell-side liquidity trap on A",
                "level_a": last_l_a,
                "level_b": last_l_b,
            }

    return None


def _swing_levels(structure: pd.DataFrame, direction: int) -> list[float]:
    """Extract ordered swing levels (highs if direction=1, lows if direction=-1)."""
    mask = (structure["HighLow"] == direction) & structure["Level"].notna()
    return [float(v) for v in structure.loc[mask, "Level"]]
