import pandas as pd

from smc_ai.core.ob_filter import filter_obs_by_leg


def _index(n: int) -> pd.DatetimeIndex:
    return pd.date_range("2026-01-01 07:00:00", periods=n, freq="15min")


def _order_blocks(ob_values: list[int], tops: list, bottoms: list) -> pd.DataFrame:
    idx = _index(len(ob_values))
    return pd.DataFrame({
        "OB": ob_values,
        "Top": [float(t) if t is not None else pd.NA for t in tops],
        "Bottom": [float(b) if b is not None else pd.NA for b in bottoms],
        "MitigatedIndex": [pd.NA] * len(ob_values),
    }, index=idx)


def _idm(idm_values: list[int], n: int) -> pd.DataFrame:
    idx = _index(n)
    return pd.DataFrame({
        "IDM": idm_values,
        "SweptLevel": [pd.NA] * n,
        "ConfirmIndex": [pd.NA] * n,
    }, index=idx)


def _events(event_list: list[str | None], n: int) -> pd.DataFrame:
    idx = _index(n)
    return pd.DataFrame({
        "Event": [e if e is not None else pd.NA for e in event_list],
        "Direction": [pd.NA] * n,
    }, index=idx)


def test_filter_obs_by_leg_keeps_ob_idm():
    # OBs at positions 1,3,5. IDM sweep at position 6. OB_IDM = position 5.
    ob = _order_blocks([0, 1, 0, 1, 0, 1, 0], [None, 1.12, None, 1.13, None, 1.14, None],
                       [None, 1.10, None, 1.11, None, 1.12, None])
    idm = _idm([0, 0, 0, 0, 0, 0, -1], 7)   # IDM at position 6
    ev = _events([None] * 7, 7)

    result = filter_obs_by_leg(ob, idm, ev)

    active = result[result["OB"] != 0]
    assert len(active) == 1
    assert active.index[0] == ob.index[5]   # OB at position 5 = last before IDM at 6


def test_filter_obs_by_leg_keeps_ob_extreme():
    # OBs at 1,3,5. ChoCh at position 4. OB_Extreme = position 3.
    ob = _order_blocks([0, 1, 0, 1, 0, 1, 0], [None, 1.12, None, 1.13, None, 1.14, None],
                       [None, 1.10, None, 1.11, None, 1.12, None])
    idm = _idm([0] * 7, 7)
    ev = _events([None, None, None, None, "CHOCH", None, None], 7)

    result = filter_obs_by_leg(ob, idm, ev)

    active = result[result["OB"] != 0]
    assert len(active) == 1
    assert active.index[0] == ob.index[3]   # OB at position 3 = last before ChoCh at 4


def test_filter_obs_by_leg_keeps_both_ob_idm_and_ob_extreme():
    # OBs at 1,3,5. IDM at 6, ChoCh at 4. OB_IDM=5, OB_Extreme=3. OB at 1 = LT.
    ob = _order_blocks([0, 1, 0, 1, 0, 1, 0], [None, 1.12, None, 1.13, None, 1.14, None],
                       [None, 1.10, None, 1.11, None, 1.12, None])
    idm = _idm([0, 0, 0, 0, 0, 0, -1], 7)
    ev = _events([None, None, None, None, "CHOCH", None, None], 7)

    result = filter_obs_by_leg(ob, idm, ev)

    active = result[result["OB"] != 0]
    assert len(active) == 2
    kept_positions = list(active.index)
    assert ob.index[3] in kept_positions   # OB_Extreme
    assert ob.index[5] in kept_positions   # OB_IDM
    assert ob.index[1] not in kept_positions   # LT — cleared


def test_filter_obs_by_leg_no_anchor_events_keeps_all():
    # No IDM, no ChoCh → no basis for filtering → all OBs kept
    ob = _order_blocks([1, 0, 1, 0, 1], [1.12, None, 1.13, None, 1.14],
                       [1.10, None, 1.11, None, 1.12])
    idm = _idm([0] * 5, 5)
    ev = _events([None] * 5, 5)

    result = filter_obs_by_leg(ob, idm, ev)

    assert result[result["OB"] != 0].shape[0] == 3


def test_filter_obs_by_leg_empty_obs_returns_copy():
    ob = _order_blocks([0, 0, 0], [None, None, None], [None, None, None])
    idm = _idm([0, 0, -1], 3)
    ev = _events([None] * 3, 3)

    result = filter_obs_by_leg(ob, idm, ev)

    assert result[result["OB"] != 0].empty
