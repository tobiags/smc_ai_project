from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """Application settings shared by the core and dashboard."""

    model_config = SettingsConfigDict(env_prefix="SMC_", env_file=".env", extra="ignore")

    pairs: tuple[str, ...] = ("EURUSD", "GBPUSD", "XAUUSD", "USDJPY", "AUDUSD")
    crypto_pairs: tuple[str, ...] = ("BTCUSDT", "ETHUSDT")
    timeframes: tuple[str, ...] = ("D1", "H4", "M15")
    entry_timeframe: str = "M15"
    bias_timeframe: str = "D1"
    confluence_timeframe: str = "H4"
    min_rr: float = 5.0
    results_dir: Path = PROJECT_ROOT / "results"
    data_dir: Path = PROJECT_ROOT / "data"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
