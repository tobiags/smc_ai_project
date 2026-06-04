"""Core SMC analysis modules."""

from smc_ai.core.entry_decision import EntryDecision, evaluate_entry_decision
from smc_ai.core.entry_pipeline import EntryAnalysis, build_entry_analysis, scan_latest_m15_entry
from smc_ai.core.indicators import calculate_fvg, calculate_swing_highs_lows
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
from smc_ai.core.risk import TradeLevels, calculate_trade_levels
from smc_ai.core.trading_math import (
    breakeven_win_rate,
    expectancy_r,
    fixed_risk_position_size,
    recovery_gain_required,
)

__all__ = [
    "calculate_fvg",
    "calculate_swing_highs_lows",
    "detect_order_blocks",
    "detect_structure_events",
    "EntryDecision",
    "EntryAnalysis",
    "evaluate_entry_decision",
    "build_entry_analysis",
    "scan_latest_m15_entry",
    "filter_zones_by_confluence",
    "label_market_structure",
    "latest_structure_bias",
    "PoiZone",
    "TradeLevels",
    "calculate_trade_levels",
    "breakeven_win_rate",
    "expectancy_r",
    "fixed_risk_position_size",
    "recovery_gain_required",
    "zones_from_fvg",
    "zones_from_order_blocks",
]
