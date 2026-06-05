import pandas as pd
import pytest

from smc_ai.data.providers.csv_provider import default_fetcher, make_csv_provider
from smc_ai.data.fetcher import DataRequest


def _write_sample_csv(path, symbol: str = "EURUSD", timeframe: str = "M15") -> None:
    index = pd.date_range("2026-01-01 07:00:00", periods=10, freq="15min")
    df = pd.DataFrame({
        "open": [1.10] * 10,
        "high": [1.11] * 10,
        "low": [1.09] * 10,
        "close": [1.105] * 10,
        "volume": [1000] * 10,
    }, index=index)
    df.index.name = "time"
    csv_file = path / f"{symbol}_{timeframe}.csv"
    df.to_csv(csv_file)


def test_make_csv_provider_loads_ohlcv(tmp_path):
    _write_sample_csv(tmp_path)
    provider = make_csv_provider(tmp_path)
    request = DataRequest(symbol="EURUSD", timeframe="M15", bars=10)

    df = provider(request)

    assert list(df.columns) == ["open", "high", "low", "close", "volume"]
    assert len(df) == 10


def test_make_csv_provider_raises_for_missing_file(tmp_path):
    provider = make_csv_provider(tmp_path)
    request = DataRequest(symbol="MISSING", timeframe="M15", bars=10)

    with pytest.raises(FileNotFoundError):
        provider(request)


def test_default_fetcher_is_a_data_fetcher_with_csv_registered(tmp_path):
    _write_sample_csv(tmp_path)
    fetcher = default_fetcher(data_dir=tmp_path)
    request = DataRequest(symbol="EURUSD", timeframe="M15", bars=10)

    df = fetcher.get(request)

    assert len(df) == 10
