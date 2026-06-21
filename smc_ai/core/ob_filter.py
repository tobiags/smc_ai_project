import pandas as pd


def filter_obs_by_leg(
    order_blocks: pd.DataFrame,
    idm: pd.DataFrame,
    events: pd.DataFrame,
) -> pd.DataFrame:
    """Return a copy of order_blocks with Liquidity Trap (LT) OBs cleared.

    WinWorld rule: per leg, only 2 valid OBs exist:
    - OB_IDM     : the last OB strictly before the MOST RECENT IDM sweep
    - OB_Extreme : the last OB strictly before the MOST RECENT ChoCh

    All other OBs between these anchor points are Liquidity Traps.

    Critical: only the MOST RECENT structural anchor is used, not all historical
    ones. Using all historical IDM/ChoCh would keep dozens of stale OBs,
    defeating the purpose of the filter entirely.

    If no IDM and no ChoCh exist, all OBs are kept (no basis to filter).
    """
    ob_mask = order_blocks["OB"] != 0
    ob_rows = order_blocks[ob_mask]

    if ob_rows.empty:
        return order_blocks.copy()

    ob_index_list = sorted(ob_rows.index)
    valid_ob_indices: set = set()

    # OB_IDM: last OB strictly before the MOST RECENT IDM sweep
    idm_sweeps = idm[idm["IDM"] != 0]
    if not idm_sweeps.empty:
        most_recent_sweep = idm_sweeps.index[-1]
        candidates = [i for i in ob_index_list if i < most_recent_sweep]
        if candidates:
            valid_ob_indices.add(candidates[-1])

    # OB_Extreme: last OB strictly before the MOST RECENT ChoCh
    chochs = events[events["Event"] == "CHOCH"]
    if not chochs.empty:
        most_recent_choch = chochs.index[-1]
        candidates = [i for i in ob_index_list if i < most_recent_choch]
        if candidates:
            valid_ob_indices.add(candidates[-1])

    # No anchors at all → no basis for filtering, keep everything
    if not valid_ob_indices and idm_sweeps.empty and chochs.empty:
        return order_blocks.copy()

    # Clear all OBs that are not OB_IDM or OB_Extreme (= Liquidity Traps)
    result = order_blocks.copy()
    for idx in ob_index_list:
        if idx not in valid_ob_indices:
            result.loc[idx, "OB"] = 0
            result.loc[idx, "Top"] = pd.NA
            result.loc[idx, "Bottom"] = pd.NA
            if "MitigatedIndex" in result.columns:
                result.loc[idx, "MitigatedIndex"] = pd.NA

    return result
