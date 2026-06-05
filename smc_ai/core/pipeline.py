from dataclasses import dataclass

import pandas as pd

from smc_ai.core.entry_pipeline import EntryAnalysis, scan_latest_m15_entry
from smc_ai.core.idm import detect_idm, latest_confirmed_idm
from smc_ai.core.indicators import calculate_fvg
from smc_ai.core.market_structure import (
    detect_structure_events,
    label_market_structure,
    latest_structure_bias,
)
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

    def to_dict(self) -> dict[str, object]:
        return {
            "symbol": self.symbol,
            "d1_bias": self.d1_bias,
            "h4_zones": [z.to_dict() for z in self.h4_zones],
            "m15_entry": self.m15_entry.to_dict(),
            "idm_confirmed": self.idm_confirmed,
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
    """Orchestrate D1 bias → H4 confluence → M15 entry with IDM confirmation."""
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

    # Step 3 — M15 zones filtered by H4 confluence
    m15_fvg = calculate_fvg(m15)
    m15_ob = detect_order_blocks(m15, fvg=m15_fvg)
    m15_zones: list[PoiZone] = zones_from_order_blocks(m15_ob) + zones_from_fvg(m15_fvg)
    confirmed_pois = filter_zones_by_confluence(m15_zones, h4_zones)

    # Step 4 — IDM confirmation on M15
    m15_structure = label_market_structure(m15, swing_length=swing_length)
    m15_events = detect_structure_events(m15, structure=m15_structure)
    idm_result = detect_idm(m15_events, lookahead=20)
    idm_info = latest_confirmed_idm(idm_result)
    idm_confirmed = idm_info is not None and idm_info["direction"] == (
        "bullish" if d1_bias == "bullish" else "bearish"
    )

    # Step 5 — M15 entry scan
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
    )
