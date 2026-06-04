import pandas as pd
import pytest

from smc_ai.core.market_structure import (
    detect_structure_events,
    label_market_structure,
    latest_structure_bias,
)


def _ohlcv(highs: list[float], lows: list[float]) -> pd.DataFrame:
    index = pd.date_range("2026-01-01 07:00:00", periods=len(highs), freq="15min")
    closes = [(high + low) / 2 for high, low in zip(highs, lows, strict=True)]
    return pd.DataFrame(
        {
            "open": closes,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": [100] * len(highs),
        },
        index=index,
    )


def _structure(index: pd.DatetimeIndex, rows: dict[int, tuple[int, float, str]]) -> pd.DataFrame:
    structure = pd.DataFrame(
        {
            "HighLow": [0] * len(index),
            "Level": [pd.NA] * len(index),
            "Structure": [pd.NA] * len(index),
        },
        index=index,
    )
    for position, (high_low, level, label) in rows.items():
        structure.iloc[position, structure.columns.get_loc("HighLow")] = high_low
        structure.iloc[position, structure.columns.get_loc("Level")] = level
        structure.iloc[position, structure.columns.get_loc("Structure")] = label
    return structure


def test_label_market_structure_marks_higher_highs_and_higher_lows():
    df = _ohlcv(
        highs=[1.10, 1.12, 1.11, 1.15, 1.13, 1.16, 1.14],
        lows=[1.08, 1.09, 1.07, 1.10, 1.09, 1.11, 1.10],
    )

    structure = label_market_structure(df, swing_length=1)

    assert structure.loc[df.index[1], "Structure"] == "H"
    assert structure.loc[df.index[2], "Structure"] == "L"
    assert structure.loc[df.index[3], "Structure"] == "HH"
    assert structure.loc[df.index[4], "Structure"] == "HL"
    assert structure.loc[df.index[5], "Structure"] == "HH"


def test_label_market_structure_marks_lower_highs_and_lower_lows():
    df = _ohlcv(
        highs=[1.14, 1.16, 1.13, 1.15, 1.12, 1.14, 1.11],
        lows=[1.10, 1.12, 1.09, 1.11, 1.08, 1.10, 1.07],
    )

    structure = label_market_structure(df, swing_length=1)

    assert structure.loc[df.index[1], "Structure"] == "H"
    assert structure.loc[df.index[2], "Structure"] == "L"
    assert structure.loc[df.index[3], "Structure"] == "LH"
    assert structure.loc[df.index[4], "Structure"] == "LL"
    assert structure.loc[df.index[5], "Structure"] == "LH"


@pytest.mark.parametrize(
    ("labels", "expected"),
    [
        (["H", "L", "HH", "HL"], "bullish"),
        (["H", "L", "LH", "LL"], "bearish"),
        (["H", "L"], "neutral"),
        ([], "neutral"),
    ],
)
def test_latest_structure_bias_uses_latest_actionable_structure(labels, expected):
    structure = pd.DataFrame({"Structure": labels})

    assert latest_structure_bias(structure) == expected


def test_detect_structure_events_marks_bullish_bos_on_close_above_structure_high():
    df = _ohlcv(
        highs=[1.10, 1.08, 1.12, 1.10, 1.13],
        lows=[1.06, 1.05, 1.09, 1.08, 1.11],
    )
    df.loc[df.index[-1], "close"] = 1.125
    structure = _structure(
        df.index,
        {
            0: (1, 1.10, "H"),
            1: (-1, 1.05, "L"),
            2: (1, 1.12, "HH"),
            3: (-1, 1.08, "HL"),
        },
    )

    events = detect_structure_events(df, structure)

    assert events.loc[df.index[-1], "Event"] == "BOS"
    assert events.loc[df.index[-1], "Direction"] == "bullish"
    assert events.loc[df.index[-1], "BreakType"] == "close"
    assert events.loc[df.index[-1], "BrokenStructure"] == "HH"
    assert events.loc[df.index[-1], "BrokenLevel"] == 1.12


def test_detect_structure_events_marks_sweep_when_only_wick_breaks_structure():
    df = _ohlcv(
        highs=[1.10, 1.08, 1.12, 1.10, 1.13],
        lows=[1.06, 1.05, 1.09, 1.08, 1.11],
    )
    df.loc[df.index[-1], "close"] = 1.119
    structure = _structure(
        df.index,
        {
            0: (1, 1.10, "H"),
            1: (-1, 1.05, "L"),
            2: (1, 1.12, "HH"),
            3: (-1, 1.08, "HL"),
        },
    )

    events = detect_structure_events(df, structure)

    assert events.loc[df.index[-1], "Event"] == "SWEEP"
    assert events.loc[df.index[-1], "Direction"] == "bullish"
    assert events.loc[df.index[-1], "BreakType"] == "wick"
    assert events.loc[df.index[-1], "BrokenStructure"] == "HH"


def test_detect_structure_events_marks_bearish_choch_on_close_below_higher_low():
    df = _ohlcv(
        highs=[1.10, 1.08, 1.12, 1.10, 1.09],
        lows=[1.06, 1.05, 1.09, 1.08, 1.07],
    )
    df.loc[df.index[-1], "close"] = 1.075
    structure = _structure(
        df.index,
        {
            0: (1, 1.10, "H"),
            1: (-1, 1.05, "L"),
            2: (1, 1.12, "HH"),
            3: (-1, 1.08, "HL"),
        },
    )

    events = detect_structure_events(df, structure)

    assert events.loc[df.index[-1], "Event"] == "CHOCH"
    assert events.loc[df.index[-1], "Direction"] == "bearish"
    assert events.loc[df.index[-1], "BreakType"] == "close"
    assert events.loc[df.index[-1], "BrokenStructure"] == "HL"
