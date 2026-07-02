import numpy as np
import pandas as pd

from smc_ai.core.indicators import calculate_swing_highs_lows
from smc_ai.data.models import validate_ohlcv


BULLISH_STRUCTURE_LABELS = {"HH", "HL"}
BEARISH_STRUCTURE_LABELS = {"LH", "LL"}


def label_market_structure(df: pd.DataFrame, swing_length: int = 5) -> pd.DataFrame:
    swings = calculate_swing_highs_lows(df, swing_length=swing_length).copy()

    high_low_arr = swings["HighLow"].to_numpy()
    level_arr = swings["Level"].to_numpy(dtype=object)
    structure = np.full(len(swings), pd.NA, dtype=object)

    previous_high: float | None = None
    previous_low: float | None = None

    for pos in range(len(swings)):
        high_low = int(high_low_arr[pos])
        if high_low == 0 or pd.isna(level_arr[pos]):
            continue

        level = float(level_arr[pos])
        if high_low == 1:
            label = "H" if previous_high is None else _label_high(level, previous_high)
            previous_high = level
        elif high_low == -1:
            label = "L" if previous_low is None else _label_low(level, previous_low)
            previous_low = level
        else:
            continue

        structure[pos] = label

    swings["Structure"] = structure
    return swings


def detect_structure_events(
    df: pd.DataFrame,
    structure: pd.DataFrame | None = None,
    swing_length: int = 5,
) -> pd.DataFrame:
    normalized = validate_ohlcv(df)
    structure = structure if structure is not None else label_market_structure(normalized, swing_length)
    _validate_structure_frame(normalized, structure)

    n = len(normalized)
    closes = normalized["close"].to_numpy(dtype=float)
    highs = normalized["high"].to_numpy(dtype=float)
    lows = normalized["low"].to_numpy(dtype=float)
    s_high_low = structure["HighLow"].to_numpy()
    s_level = structure["Level"].to_numpy(dtype=object)
    s_structure = structure["Structure"].to_numpy(dtype=object)

    col_event = np.full(n, pd.NA, dtype=object)
    col_direction = np.full(n, pd.NA, dtype=object)
    col_break_type = np.full(n, pd.NA, dtype=object)
    col_broken_structure = np.full(n, pd.NA, dtype=object)
    col_broken_level = np.full(n, pd.NA, dtype=object)

    latest_high: tuple[float, str] | None = None
    latest_low: tuple[float, str] | None = None
    structure_labels: list[str] = []

    for pos in range(n):
        event, is_choch = _detect_break_event(
            closes[pos], highs[pos], lows[pos], latest_high, latest_low, structure_labels
        )
        if event is not None:
            col_event[pos] = event["Event"]
            col_direction[pos] = event["Direction"]
            col_break_type[pos] = event["BreakType"]
            col_broken_structure[pos] = event["BrokenStructure"]
            col_broken_level[pos] = event["BrokenLevel"]
            if is_choch:
                latest_high = None
                latest_low = None
                structure_labels.clear()

        if int(s_high_low[pos]) != 0 and not pd.isna(s_level[pos]) and not pd.isna(s_structure[pos]):
            level = float(s_level[pos])
            label = str(s_structure[pos])
            structure_labels.append(label)
            if int(s_high_low[pos]) == 1:
                latest_high = (level, label)
            elif int(s_high_low[pos]) == -1:
                latest_low = (level, label)

    return pd.DataFrame(
        {
            "Event": col_event,
            "Direction": col_direction,
            "BreakType": col_break_type,
            "BrokenStructure": col_broken_structure,
            "BrokenLevel": col_broken_level,
        },
        index=normalized.index,
    )


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


def _validate_structure_frame(df: pd.DataFrame, structure: pd.DataFrame) -> None:
    required = {"HighLow", "Level", "Structure"}
    missing = required.difference(structure.columns)
    if missing:
        raise ValueError(f"structure is missing columns: {sorted(missing)}")
    if not structure.index.equals(df.index):
        raise ValueError("structure index must match OHLCV index")


def _detect_break_event(
    close: float,
    high: float,
    low: float,
    latest_high: tuple[float, str] | None,
    latest_low: tuple[float, str] | None,
    structure_labels: list[str],
) -> tuple[dict[str, object] | None, bool]:
    """Return (event_dict | None, is_choch)."""
    current_bias = _bias_from_labels(structure_labels)

    if latest_high is not None:
        high_level, high_label = latest_high
        if close > high_level:
            is_choch = current_bias == "bearish"
            return _event("CHOCH" if is_choch else "BOS", "bullish", "close", high_label, high_level), is_choch
        if high > high_level:
            return _event("SWEEP", "bullish", "wick", high_label, high_level), False

    if latest_low is not None:
        low_level, low_label = latest_low
        if close < low_level:
            is_choch = current_bias == "bullish"
            return _event("CHOCH" if is_choch else "BOS", "bearish", "close", low_label, low_level), is_choch
        if low < low_level:
            return _event("SWEEP", "bearish", "wick", low_label, low_level), False

    return None, False


def _bias_from_labels(labels: list[str]) -> str:
    actionable = [label for label in labels if label in BULLISH_STRUCTURE_LABELS | BEARISH_STRUCTURE_LABELS]
    if not actionable:
        return "neutral"
    latest = actionable[-1]
    if latest in BULLISH_STRUCTURE_LABELS:
        return "bullish"
    return "bearish"


def _event(
    event: str,
    direction: str,
    break_type: str,
    broken_structure: str,
    broken_level: float,
) -> dict[str, object]:
    return {
        "Event": event,
        "Direction": direction,
        "BreakType": break_type,
        "BrokenStructure": broken_structure,
        "BrokenLevel": broken_level,
    }
