from smc_ai.core.strategy_profiles import StrategyProfile, get_strategy_profile


def test_get_winworld_strategy_profile_contract():
    profile = get_strategy_profile("winworld_smc_v1")

    assert isinstance(profile, StrategyProfile)
    assert profile.strategy_id == "winworld_smc_v1"
    assert profile.version == "0.1"
    assert profile.required_timeframes == ("D1", "H4", "M15")
    assert profile.entry_timeframe == "M15"
    assert profile.allowed_sessions == ("london", "ny")
    assert profile.min_rr == 5.0


def test_winworld_profile_contains_core_rules():
    profile = get_strategy_profile("winworld_smc_v1")

    assert "liquidity -> IDM -> valid POI -> BOS/ChoCh" in profile.setup_rules
    assert "M15 schema confirmation" in profile.entry_triggers
    assert "sweep-only BOS" in profile.invalidation_rules
    assert "missing IDM" in profile.invalidation_rules
    assert "RR < 1:5" in profile.invalidation_rules


def test_unknown_strategy_profile_raises_clear_error():
    try:
        get_strategy_profile("unknown")
    except KeyError as exc:
        assert "Unknown strategy profile" in str(exc)
    else:
        raise AssertionError("Expected KeyError")
