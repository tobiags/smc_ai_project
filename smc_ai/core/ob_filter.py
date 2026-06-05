import pandas as pd


def filter_obs_by_leg(
    order_blocks: pd.DataFrame,
    idm: pd.DataFrame,
    events: pd.DataFrame,
) -> pd.DataFrame:
    """Return a copy of order_blocks with Liquidity Trap (LT) OBs cleared.

    WinWorld rule: per leg, only 2 valid OBs exist:
    - OB_IDM     : the last OB candle strictly before the IDM sweep event
    - OB_Extreme : the last OB candle strictly before each ChoCh event

    All other OBs between these anchor points are Liquidity Traps.
    If no IDM or ChoCh events exist, all OBs are kept (no information to filter by).
    """
    ob_mask = order_blocks["OB"] != 0
    ob_rows = order_blocks[ob_mask]

    if ob_rows.empty:
        return order_blocks.copy()

    ob_index_list = list(ob_rows.index)
    valid_ob_indices: set = set()

    # OB_IDM: last OB before each confirmed IDM sweep
    idm_sweeps = idm[idm["IDM"] != 0]
    for sweep_idx in idm_sweeps.index:
        candidates = [i for i in ob_index_list if i < sweep_idx]
        if candidates:
            valid_ob_indices.add(candidates[-1])

    # OB_Extreme: last OB before each ChoCh (structural reversal)
    chochs = events[events["Event"] == "CHOCH"]
    for choch_idx in chochs.index:
        candidates = [i for i in ob_index_list if i < choch_idx]
        if candidates:
            valid_ob_indices.add(candidates[-1])

    # If no anchor events at all, return unchanged (no basis for filtering)
    if not valid_ob_indices and idm_sweeps.empty and chochs.empty:
        return order_blocks.copy()

    result = order_blocks.copy()
    for idx in ob_index_list:
        if idx not in valid_ob_indices:
            result.loc[idx, "OB"] = 0
            result.loc[idx, "Top"] = pd.NA
            result.loc[idx, "Bottom"] = pd.NA
            if "MitigatedIndex" in result.columns:
                result.loc[idx, "MitigatedIndex"] = pd.NA

    return result
