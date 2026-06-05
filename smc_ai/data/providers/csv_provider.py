from pathlib import Path

import pandas as pd

from smc_ai.data.csv_loader import load_ohlcv_csv
from smc_ai.data.fetcher import DataFetcher, DataProvider, DataRequest


def make_csv_provider(data_dir: Path) -> DataProvider:
    """Return a DataProvider that loads OHLCV from {data_dir}/{symbol}_{timeframe}.csv."""
    data_dir = Path(data_dir)

    def provider(request: DataRequest) -> pd.DataFrame:
        path = data_dir / f"{request.symbol}_{request.timeframe}.csv"
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {path}")
        return load_ohlcv_csv(path)

    return provider


def default_fetcher(data_dir: Path | None = None) -> DataFetcher:
    """Build a DataFetcher with the CSV provider registered."""
    from smc_ai.config import get_settings

    resolved_dir = Path(data_dir) if data_dir is not None else get_settings().data_dir
    fetcher = DataFetcher()
    fetcher.register("csv", make_csv_provider(resolved_dir))
    return fetcher
