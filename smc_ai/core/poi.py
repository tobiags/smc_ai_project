from dataclasses import dataclass
from typing import Hashable

import pandas as pd


@dataclass(frozen=True)
class PoiZone:
    kind: str
    direction: str
    top: float
    bottom: float
    source_index: Hashable

    def overlaps(self, other: "PoiZone") -> bool:
        return self.bottom <= other.top and other.bottom <= self.top

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "direction": self.direction,
            "top": self.top,
            "bottom": self.bottom,
            "source_index": str(self.source_index),
        }


def zones_from_order_blocks(order_blocks: pd.DataFrame) -> list[PoiZone]:
    _require_columns(order_blocks, {"OB", "Top", "Bottom"})
    zones: list[PoiZone] = []

    for index, row in order_blocks.iterrows():
        direction = _direction_from_int(row["OB"])
        if direction is None or pd.isna(row["Top"]) or pd.isna(row["Bottom"]):
            continue
        zones.append(
            PoiZone(
                kind="OB",
                direction=direction,
                top=float(row["Top"]),
                bottom=float(row["Bottom"]),
                source_index=index,
            )
        )

    return zones


def zones_from_fvg(fvg: pd.DataFrame) -> list[PoiZone]:
    _require_columns(fvg, {"FVG", "Top", "Bottom"})
    zones: list[PoiZone] = []

    for index, row in fvg.iterrows():
        direction = _direction_from_int(row["FVG"])
        if direction is None or pd.isna(row["Top"]) or pd.isna(row["Bottom"]):
            continue
        zones.append(
            PoiZone(
                kind="FVG",
                direction=direction,
                top=float(row["Top"]),
                bottom=float(row["Bottom"]),
                source_index=index,
            )
        )

    return zones


def filter_zones_by_confluence(
    lower_timeframe_zones: list[PoiZone],
    higher_timeframe_zones: list[PoiZone],
) -> list[PoiZone]:
    return [
        zone
        for zone in lower_timeframe_zones
        if any(
            zone.direction == higher_zone.direction and zone.overlaps(higher_zone)
            for higher_zone in higher_timeframe_zones
        )
    ]


def _require_columns(df: pd.DataFrame, required: set[str]) -> None:
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"POI source is missing columns: {sorted(missing)}")


def _direction_from_int(value: object) -> str | None:
    if pd.isna(value):
        return None
    direction = int(value)
    if direction == 1:
        return "bullish"
    if direction == -1:
        return "bearish"
    return None
