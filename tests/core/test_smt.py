import pandas as pd

from smc_ai.core.smt import detect_smt


def _structure(high_low: list[int], levels: list) -> pd.DataFrame:
    index = pd.date_range("2026-01-01 07:00:00", periods=len(high_low), freq="15min")
    return pd.DataFrame({
        "HighLow": high_low,
        "Level": [float(l) if l is not None else pd.NA for l in levels],
        "Structure": [pd.NA] * len(high_low),
    }, index=index)


def test_detect_smt_bearish_when_a_makes_hh_b_makes_lh():
    # A: HH (1.10 → 1.12). B: LH (1.20 → 1.19). → bearish SMT
    structure_a = _structure([1, 0, 1], [1.10, None, 1.12])
    structure_b = _structure([1, 0, 1], [1.20, None, 1.19])

    result = detect_smt(structure_a, structure_b)

    assert result is not None
    assert result["type"] == "bearish_smt"
    assert result["level_a"] == 1.12
    assert result["level_b"] == 1.19


def test_detect_smt_bullish_when_a_makes_ll_b_makes_hl():
    # A: LL (1.10 → 1.08). B: HL (1.05 → 1.06). → bullish SMT
    structure_a = _structure([-1, 0, -1], [1.10, None, 1.08])
    structure_b = _structure([-1, 0, -1], [1.05, None, 1.06])

    result = detect_smt(structure_a, structure_b)

    assert result is not None
    assert result["type"] == "bullish_smt"
    assert result["level_a"] == 1.08
    assert result["level_b"] == 1.06


def test_detect_smt_returns_none_when_both_confirm():
    # A: HH (1.10 → 1.12). B: HH (1.20 → 1.22). → both confirm → no SMT
    structure_a = _structure([1, 0, 1], [1.10, None, 1.12])
    structure_b = _structure([1, 0, 1], [1.20, None, 1.22])

    assert detect_smt(structure_a, structure_b) is None


def test_detect_smt_returns_none_when_insufficient_swings():
    # Only 1 swing point each → can't compare
    structure_a = _structure([1, 0, 0], [1.10, None, None])
    structure_b = _structure([1, 0, 0], [1.20, None, None])

    assert detect_smt(structure_a, structure_b) is None


def test_detect_smt_bearish_description_is_informative():
    structure_a = _structure([1, 0, 1], [1.10, None, 1.12])
    structure_b = _structure([1, 0, 1], [1.20, None, 1.18])

    result = detect_smt(structure_a, structure_b)

    assert result is not None
    assert "HH" in result["description"] or "liquidity" in result["description"].lower()
