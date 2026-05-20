from smc_ai.data.fetcher import DataFetcher, DataRequest
from smc_ai.reports.sample_results import make_sample_ohlcv


def test_data_fetcher_uses_registered_provider():
    request = DataRequest(symbol="EURUSD", timeframe="M15", bars=10)
    fetcher = DataFetcher()
    fetcher.register("sample", lambda req: make_sample_ohlcv(req.bars))

    df = fetcher.get(request)

    assert len(df) == 10
    assert {"open", "high", "low", "close", "volume"}.issubset(df.columns)


def test_data_fetcher_raises_when_no_provider_registered():
    request = DataRequest(symbol="EURUSD", timeframe="M15", bars=10)
    fetcher = DataFetcher()

    try:
        fetcher.get(request)
    except RuntimeError as exc:
        assert "No data provider succeeded" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError")


def test_data_fetcher_tries_next_provider_after_failure():
    request = DataRequest(symbol="EURUSD", timeframe="M15", bars=5)
    fetcher = DataFetcher()

    def failing_provider(_request: DataRequest):
        raise ValueError("source unavailable")

    fetcher.register("bad", failing_provider)
    fetcher.register("sample", lambda req: make_sample_ohlcv(req.bars))

    df = fetcher.get(request)

    assert len(df) == 5


def test_data_fetcher_rejects_invalid_provider_output():
    request = DataRequest(symbol="EURUSD", timeframe="M15", bars=10)
    fetcher = DataFetcher()
    fetcher.register("bad", lambda _request: make_sample_ohlcv(0))

    try:
        fetcher.get(request)
    except RuntimeError as exc:
        assert "bad:" in str(exc)
        assert "empty" in str(exc).lower()
    else:
        raise AssertionError("Expected RuntimeError")
