from pathlib import Path

from smc_ai.config import PROJECT_ROOT, Settings, get_settings


def test_default_pairs_and_timeframes():
    settings = Settings()

    assert settings.pairs == ("EURUSD", "GBPUSD", "XAUUSD", "USDJPY", "AUDUSD")
    assert settings.timeframes == ("D1", "H4", "M15")
    assert settings.min_rr == 5.0


def test_results_dir_defaults_to_project_results():
    settings = get_settings()

    assert isinstance(settings.results_dir, Path)
    assert settings.results_dir == PROJECT_ROOT / "results"
