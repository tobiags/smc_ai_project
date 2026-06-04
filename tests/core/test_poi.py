import pandas as pd

from smc_ai.core.poi import (
    PoiZone,
    filter_zones_by_confluence,
    zones_from_fvg,
    zones_from_order_blocks,
)


def test_zones_from_order_blocks_extracts_bullish_zone():
    index = pd.date_range("2026-01-01 07:00:00", periods=2, freq="15min")
    order_blocks = pd.DataFrame(
        {
            "OB": [1, 0],
            "Top": [1.120, pd.NA],
            "Bottom": [1.100, pd.NA],
            "SourceFVGIndex": [index[1], pd.NA],
            "MitigatedIndex": [pd.NA, pd.NA],
        },
        index=index,
    )

    zones = zones_from_order_blocks(order_blocks)

    assert zones == [
        PoiZone(
            kind="OB",
            direction="bullish",
            top=1.120,
            bottom=1.100,
            source_index=index[0],
        )
    ]


def test_zones_from_fvg_extracts_bearish_zone():
    index = pd.date_range("2026-01-01 07:00:00", periods=2, freq="15min")
    fvg = pd.DataFrame(
        {
            "FVG": [0, -1],
            "Top": [pd.NA, 1.150],
            "Bottom": [pd.NA, 1.130],
            "MitigatedIndex": [pd.NA, pd.NA],
        },
        index=index,
    )

    zones = zones_from_fvg(fvg)

    assert zones == [
        PoiZone(
            kind="FVG",
            direction="bearish",
            top=1.150,
            bottom=1.130,
            source_index=index[1],
        )
    ]


def test_filter_zones_by_confluence_keeps_same_direction_overlapping_zone():
    m15_zone = PoiZone("OB", "bullish", top=1.120, bottom=1.100, source_index="m15")
    h4_zone = PoiZone("FVG", "bullish", top=1.130, bottom=1.110, source_index="h4")

    confirmed = filter_zones_by_confluence([m15_zone], [h4_zone])

    assert confirmed == [m15_zone]


def test_filter_zones_by_confluence_rejects_opposite_direction_or_no_overlap():
    m15_zone = PoiZone("OB", "bullish", top=1.120, bottom=1.100, source_index="m15")
    opposite = PoiZone("FVG", "bearish", top=1.130, bottom=1.110, source_index="h4")
    distant = PoiZone("FVG", "bullish", top=1.180, bottom=1.160, source_index="h4")

    confirmed = filter_zones_by_confluence([m15_zone], [opposite, distant])

    assert confirmed == []
