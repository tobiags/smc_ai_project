from dataclasses import dataclass


@dataclass(frozen=True)
class StrategyProfile:
    strategy_id: str
    version: str
    required_timeframes: tuple[str, ...]
    entry_timeframe: str
    allowed_sessions: tuple[str, ...]
    min_rr: float
    setup_rules: tuple[str, ...]
    entry_triggers: tuple[str, ...]
    invalidation_rules: tuple[str, ...]
    signal_labels: tuple[str, ...]


WINWORLD_SMC_V1 = StrategyProfile(
    strategy_id="winworld_smc_v1",
    version="0.1",
    required_timeframes=("D1", "H4", "M15"),
    entry_timeframe="M15",
    allowed_sessions=("london", "ny"),
    min_rr=5.0,
    setup_rules=(
        "liquidity -> IDM -> valid POI -> BOS/ChoCh",
        "D1 bias + previous high/low",
        "H4 institutional OB/FVG confluence",
    ),
    entry_triggers=(
        "M15 schema confirmation",
        "valid session",
        "minimum RR satisfied",
    ),
    invalidation_rules=(
        "sweep-only BOS",
        "missing IDM",
        "invalid OB",
        "RR < 1:5",
    ),
    signal_labels=(
        "sample_smc_long",
        "winworld_entry_schema_pending",
    ),
)

_PROFILES = {
    WINWORLD_SMC_V1.strategy_id: WINWORLD_SMC_V1,
}


def get_strategy_profile(strategy_id: str) -> StrategyProfile:
    try:
        return _PROFILES[strategy_id]
    except KeyError as exc:
        raise KeyError(f"Unknown strategy profile: {strategy_id}") from exc
