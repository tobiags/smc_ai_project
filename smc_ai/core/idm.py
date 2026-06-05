from typing import Any
import pandas as pd


def detect_idm(events: pd.DataFrame, lookahead: int = 20) -> pd.DataFrame:
    """Detect Inducement (IDM) events.

    An IDM is a SWEEP followed by a confirming BOS/CHOCH in the OPPOSITE
    direction within `lookahead` candles.

    Returns a DataFrame with columns:
        IDM           int  : 0 = none, 1 = bullish IDM, -1 = bearish IDM
        SweptLevel    float: the level swept (from the SWEEP event)
        ConfirmIndex  obj  : Timestamp of the confirming BOS/CHOCH (or pd.NA)
    Indexed same as events.
    """
    if lookahead < 1:
        raise ValueError("lookahead must be at least 1")

    result = pd.DataFrame(
        {"IDM": 0, "SweptLevel": pd.NA, "ConfirmIndex": pd.NA},
        index=events.index,
    )

    sweep_mask = events["Event"] == "SWEEP"
    sweep_indices = events.index[sweep_mask]
    all_indices = list(events.index)

    for sweep_idx in sweep_indices:
        sweep_row = events.loc[sweep_idx]
        sweep_direction = str(sweep_row["Direction"]) if not _is_na(sweep_row["Direction"]) else ""
        swept_level = float(sweep_row["BrokenLevel"]) if not _is_na(sweep_row["BrokenLevel"]) else None

        if sweep_direction == "bullish":
            confirm_direction = "bearish"
            idm_value = -1
        elif sweep_direction == "bearish":
            confirm_direction = "bullish"
            idm_value = 1
        else:
            continue

        pos = all_indices.index(sweep_idx)
        window_end = min(pos + lookahead + 1, len(all_indices))
        future_slice = events.iloc[pos + 1 : window_end]

        confirm_idx = _find_confirming_event(future_slice, confirm_direction)
        if confirm_idx is None:
            continue

        result.loc[sweep_idx, "IDM"] = idm_value
        result.loc[sweep_idx, "SweptLevel"] = swept_level
        result.loc[sweep_idx, "ConfirmIndex"] = confirm_idx

    return result


def latest_confirmed_idm(idm: pd.DataFrame) -> dict[str, Any] | None:
    """Return the most recent confirmed IDM as a dict, or None."""
    confirmed = idm[idm["IDM"] != 0]
    if confirmed.empty:
        return None
    row = confirmed.iloc[-1]
    direction = "bullish" if int(row["IDM"]) == 1 else "bearish"
    return {
        "direction": direction,
        "swept_level": row["SweptLevel"],
        "confirm_index": row["ConfirmIndex"],
        "sweep_index": confirmed.index[-1],
    }


def _find_confirming_event(future: pd.DataFrame, direction: str) -> "pd.Timestamp | None":
    for idx, row in future.iterrows():
        event = str(row["Event"]) if not _is_na(row["Event"]) else ""
        row_direction = str(row["Direction"]) if not _is_na(row["Direction"]) else ""
        break_type = str(row["BreakType"]) if not _is_na(row["BreakType"]) else ""
        if event in {"BOS", "CHOCH"} and row_direction == direction and break_type == "close":
            return idx
    return None


def _is_na(value: object) -> bool:
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False
