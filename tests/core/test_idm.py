import pandas as pd
import pytest

from smc_ai.core.idm import detect_idm, latest_confirmed_idm


def _events(rows: list[tuple[str, str, str]]) -> pd.DataFrame:
    """Build a minimal events DataFrame from (Event, Direction, BreakType) tuples."""
    index = pd.date_range("2026-01-01 07:00:00", periods=len(rows), freq="15min")
    return pd.DataFrame(
        [
            {"Event": e, "Direction": d, "BreakType": bt, "BrokenStructure": "H", "BrokenLevel": 1.10}
            for e, d, bt in rows
        ],
        index=index,
    )


def test_detect_idm_bullish_sweep_then_bearish_bos():
    events = _events([
        (pd.NA, pd.NA, pd.NA),
        ("SWEEP", "bullish", "wick"),
        (pd.NA, pd.NA, pd.NA),
        ("CHOCH", "bearish", "close"),
    ])

    result = detect_idm(events, lookahead=5)

    assert result.loc[events.index[1], "IDM"] == -1      # bearish IDM at sweep candle
    assert result.loc[events.index[1], "ConfirmIndex"] == events.index[3]


def test_detect_idm_bearish_sweep_then_bullish_bos():
    events = _events([
        (pd.NA, pd.NA, pd.NA),
        ("SWEEP", "bearish", "wick"),
        (pd.NA, pd.NA, pd.NA),
        ("BOS", "bullish", "close"),
    ])

    result = detect_idm(events, lookahead=5)

    assert result.loc[events.index[1], "IDM"] == 1       # bullish IDM at sweep candle
    assert result.loc[events.index[1], "ConfirmIndex"] == events.index[3]


def test_detect_idm_no_idm_when_confirm_is_same_direction():
    events = _events([
        (pd.NA, pd.NA, pd.NA),
        ("SWEEP", "bullish", "wick"),
        (pd.NA, pd.NA, pd.NA),
        ("BOS", "bullish", "close"),  # same direction — NOT an IDM
    ])

    result = detect_idm(events, lookahead=5)

    assert result["IDM"].eq(0).all()


def test_detect_idm_no_idm_when_confirm_is_outside_lookahead():
    events = _events([
        (pd.NA, pd.NA, pd.NA),
        ("SWEEP", "bearish", "wick"),
        (pd.NA, pd.NA, pd.NA),
        (pd.NA, pd.NA, pd.NA),
        (pd.NA, pd.NA, pd.NA),
        ("BOS", "bullish", "close"),  # candle 5 = distance 4 from candle 1
    ])

    result = detect_idm(events, lookahead=3)   # window too small

    assert result["IDM"].eq(0).all()


def test_latest_confirmed_idm_returns_most_recent():
    events = _events([
        (pd.NA, pd.NA, pd.NA),
        ("SWEEP", "bearish", "wick"),
        (pd.NA, pd.NA, pd.NA),
        ("BOS", "bullish", "close"),
        ("SWEEP", "bullish", "wick"),
        ("CHOCH", "bearish", "close"),
    ])

    idm = detect_idm(events, lookahead=5)
    latest = latest_confirmed_idm(idm)

    assert latest is not None
    assert latest["direction"] == "bearish"   # most recent IDM


def test_latest_confirmed_idm_returns_none_when_no_idm():
    events = _events([
        (pd.NA, pd.NA, pd.NA),
        (pd.NA, pd.NA, pd.NA),
    ])

    idm = detect_idm(events, lookahead=5)

    assert latest_confirmed_idm(idm) is None
