from dataclasses import dataclass
from typing import Any

import pandas as pd

from smc_ai.core.entry_pipeline import EntryAnalysis, scan_latest_m15_entry
from smc_ai.core.ifc import detect_b4_entry, detect_ifc, latest_ifc
from smc_ai.core.idm import detect_idm, latest_confirmed_idm
from smc_ai.core.indicators import calculate_fvg
from smc_ai.core.market_structure import (
    detect_structure_events,
    label_market_structure,
    latest_structure_bias,
)
from smc_ai.core.ob_filter import filter_obs_by_leg
from smc_ai.core.order_blocks import detect_order_blocks
from smc_ai.core.poi import (
    PoiZone,
    filter_zones_by_confluence,
    zones_from_fvg,
    zones_from_order_blocks,
)
from smc_ai.data.models import validate_ohlcv


@dataclass(frozen=True)
class MultiTFAnalysis:
    symbol: str
    d1_bias: str
    h4_zones: list[PoiZone]
    m15_entry: EntryAnalysis
    idm_confirmed: bool
    m15_ifc: dict[str, Any] | None
    b4_entry: dict[str, Any] | None

    def to_dict(self) -> dict[str, object]:
        b4 = dict(self.b4_entry) if self.b4_entry is not None else None
        if b4 is not None and "ifc_index" in b4:
            b4["ifc_index"] = str(b4["ifc_index"])
        return {
            "symbol": self.symbol,
            "d1_bias": self.d1_bias,
            "h4_zones": [z.to_dict() for z in self.h4_zones],
            "m15_entry": self.m15_entry.to_dict(),
            "idm_confirmed": self.idm_confirmed,
            "m15_ifc": {**self.m15_ifc, "index": str(self.m15_ifc["index"])} if self.m15_ifc else None,
            "b4_entry": b4,
        }


def run_multitf_analysis(
    symbol: str,
    df_d1: pd.DataFrame,
    df_h4: pd.DataFrame,
    df_m15: pd.DataFrame,
    min_rr: float = 5.0,
    swing_length: int = 5,
    stop_buffer: float = 0.0,
) -> MultiTFAnalysis:
    """Orchestrate D1 bias → H4 confluence → M15 entry with IDM and IFC/B4."""
    d1 = validate_ohlcv(df_d1)
    h4 = validate_ohlcv(df_h4)
    m15 = validate_ohlcv(df_m15)

    # Step 1 — D1 directional bias
    d1_structure = label_market_structure(d1, swing_length=swing_length)
    d1_bias = latest_structure_bias(d1_structure)
    # Fallback: if structure is neutral (e.g. monotonic data), use close trend
    if d1_bias == "neutral" and len(d1) >= 2:
        first_close = float(d1["close"].iloc[0])
        last_close = float(d1["close"].iloc[-1])
        if last_close > first_close:
            d1_bias = "bullish"
        elif last_close < first_close:
            d1_bias = "bearish"

    # Step 2 — H4 institutional zones
    h4_fvg = calculate_fvg(h4)
    h4_ob = detect_order_blocks(h4, fvg=h4_fvg)
    h4_zones: list[PoiZone] = zones_from_order_blocks(h4_ob) + zones_from_fvg(h4_fvg)

    # Step 3 — M15 structure, events, and IDM (needed before OB leg filter)
    m15_fvg = calculate_fvg(m15)
    m15_ob = detect_order_blocks(m15, fvg=m15_fvg)
    m15_structure = label_market_structure(m15, swing_length=swing_length)
    m15_events = detect_structure_events(m15, structure=m15_structure)
    idm_result = detect_idm(m15_events, lookahead=20)

    # Step 4 — Filter M15 OBs by leg (keep OB_IDM + OB_Extreme, discard LT)
    m15_ob_filtered = filter_obs_by_leg(m15_ob, idm_result, m15_events)
    m15_zones: list[PoiZone] = zones_from_order_blocks(m15_ob_filtered) + zones_from_fvg(m15_fvg)
    confirmed_pois = filter_zones_by_confluence(m15_zones, h4_zones)

    # Step 5 — IDM confirmation
    idm_info = latest_confirmed_idm(idm_result)
    idm_confirmed = (
        idm_info is not None
        and d1_bias in {"bullish", "bearish"}
        and idm_info["direction"] == d1_bias
    )

    # Step 6 — IFC detection and B4 schema
    m15_ifc_df = detect_ifc(m15)
    m15_ifc = latest_ifc(m15_ifc_df)
    b4_entry = detect_b4_entry(m15, m15_ifc_df, m15_structure)

    # Step 7 — M15 entry scan (schema A1: BOS/ChoCh + IDM + POI)
    m15_entry = scan_latest_m15_entry(
        symbol=symbol,
        df_m15=m15,
        bias_direction=d1_bias,
        confirmed_pois=confirmed_pois,
        min_rr=min_rr,
        stop_buffer=stop_buffer,
        structure=m15_structure,
        idm_confirmed=idm_confirmed,
    )

    return MultiTFAnalysis(
        symbol=symbol,
        d1_bias=d1_bias,
        h4_zones=h4_zones,
        m15_entry=m15_entry,
        idm_confirmed=idm_confirmed,
        m15_ifc=m15_ifc,
        b4_entry=b4_entry,
    )
