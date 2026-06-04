import pytest

from smc_ai.core.poi import PoiZone
from smc_ai.core.risk import calculate_trade_levels


def test_calculate_trade_levels_for_buy_uses_poi_bottom_as_stop():
    poi = PoiZone("OB", "bullish", top=1.120, bottom=1.100, source_index="m15")

    levels = calculate_trade_levels(entry=1.125, direction="buy", poi=poi, min_rr=5.0)

    assert levels.stop_loss == 1.100
    assert levels.take_profit == 1.250
    assert levels.rr == 5.0


def test_calculate_trade_levels_for_sell_uses_poi_top_as_stop():
    poi = PoiZone("OB", "bearish", top=1.150, bottom=1.130, source_index="m15")

    levels = calculate_trade_levels(entry=1.125, direction="sell", poi=poi, min_rr=5.0)

    assert levels.stop_loss == 1.150
    assert levels.take_profit == 1.000
    assert levels.rr == 5.0


def test_calculate_trade_levels_applies_stop_buffer():
    poi = PoiZone("OB", "bullish", top=1.120, bottom=1.100, source_index="m15")

    levels = calculate_trade_levels(entry=1.125, direction="buy", poi=poi, min_rr=5.0, buffer=0.001)

    assert levels.stop_loss == 1.099
    assert levels.take_profit == 1.255


@pytest.mark.parametrize(
    ("entry", "direction", "poi"),
    [
        (1.099, "buy", PoiZone("OB", "bullish", top=1.120, bottom=1.100, source_index="m15")),
        (1.151, "sell", PoiZone("OB", "bearish", top=1.150, bottom=1.130, source_index="m15")),
    ],
)
def test_calculate_trade_levels_rejects_invalid_entry_vs_stop(entry, direction, poi):
    with pytest.raises(ValueError, match="entry must be beyond the structural stop"):
        calculate_trade_levels(entry=entry, direction=direction, poi=poi, min_rr=5.0)
