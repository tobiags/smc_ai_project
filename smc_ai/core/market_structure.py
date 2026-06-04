import pandas as pd

from smc_ai.core.indicators import calculate_swing_highs_lows


BULLISH_STRUCTURE_LABELS = {"HH", "HL"}
BEARISH_STRUCTURE_LABELS = {"LH", "LL"}


def label_market_structure(df: pd.DataFrame, swing_length: int = 5) -> pd.DataFrame:
    swings = calculate_swing_highs_lows(df, swing_length=swing_length).copy()
    swings["Structure"] = pd.NA

    previous_high: float | None = None
    previous_low: float | None = None

    for index, row in swings.iterrows():
        high_low = int(row["HighLow"])
        if high_low == 0 or pd.isna(row["Level"]):
            continue

        level = float(row["Level"])
        if high_low == 1:
            label = "H" if previous_high is None else _label_high(level, previous_high)
            previous_high = level
        elif high_low == -1:
            label = "L" if previous_low is None else _label_low(level, previous_low)
            previous_low = level
        else:
            continue

        swings.at[index, "Structure"] = label

    return swings


def latest_structure_bias(structure: pd.DataFrame) -> str:
    if "Structure" not in structure.columns:
        raise ValueError("structure must contain a Structure column")

    labels = structure["Structure"].dropna()
    labels = labels[labels.astype(str).str.len() > 0]
    if labels.empty:
        return "neutral"

    latest = str(labels.iloc[-1])
    if latest in BULLISH_STRUCTURE_LABELS:
        return "bullish"
    if latest in BEARISH_STRUCTURE_LABELS:
        return "bearish"
    return "neutral"


def _label_high(level: float, previous_high: float) -> str:
    return "HH" if level > previous_high else "LH"


def _label_low(level: float, previous_low: float) -> str:
    return "HL" if level > previous_low else "LL"
