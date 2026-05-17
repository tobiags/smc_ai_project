import pandas as pd

from smc_ai.data.models import validate_ohlcv


def test_validate_ohlcv_accepts_valid_adapter_dataframe():
    df = pd.DataFrame(
        {
            "open": [1.1000],
            "high": [1.1010],
            "low": [1.0990],
            "close": [1.1005],
            "volume": [100],
        },
        index=pd.DatetimeIndex(["2026-01-01 07:00:00"]),
    )

    normalized = validate_ohlcv(df)

    assert list(normalized.columns) == ["open", "high", "low", "close", "volume"]
    assert normalized.iloc[0]["close"] == 1.1005


def test_validate_ohlcv_rejects_non_datetime_index():
    df = pd.DataFrame(
        {
            "open": [1.1000],
            "high": [1.1010],
            "low": [1.0990],
            "close": [1.1005],
            "volume": [100],
        },
        index=["2026-01-01 07:00:00"],
    )

    try:
        validate_ohlcv(df)
    except ValueError as exc:
        assert "datetimeindex" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


def test_validate_ohlcv_rejects_duplicate_timestamps():
    df = pd.DataFrame(
        {
            "open": [1.1000, 1.1005],
            "high": [1.1010, 1.1020],
            "low": [1.0990, 1.1000],
            "close": [1.1005, 1.1010],
            "volume": [100, 110],
        },
        index=pd.DatetimeIndex(["2026-01-01 07:00:00", "2026-01-01 07:00:00"]),
    )

    try:
        validate_ohlcv(df)
    except ValueError as exc:
        assert "duplicate timestamps" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


def test_validate_ohlcv_rejects_empty_dataframe_with_ohlcv_columns():
    df = pd.DataFrame(
        columns=["open", "high", "low", "close", "volume"],
        index=pd.DatetimeIndex([]),
    )

    try:
        validate_ohlcv(df)
    except ValueError as exc:
        assert "empty" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


def test_validate_ohlcv_rejects_high_below_open_or_close():
    df = pd.DataFrame(
        {
            "open": [1.1000],
            "high": [1.0990],
            "low": [1.0980],
            "close": [1.1005],
            "volume": [100],
        },
        index=pd.DatetimeIndex(["2026-01-01 07:00:00"]),
    )

    try:
        validate_ohlcv(df)
    except ValueError as exc:
        assert "high" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


def test_validate_ohlcv_rejects_low_above_open_or_close():
    df = pd.DataFrame(
        {
            "open": [1.1000],
            "high": [1.1020],
            "low": [1.1006],
            "close": [1.1005],
            "volume": [100],
        },
        index=pd.DatetimeIndex(["2026-01-01 07:00:00"]),
    )

    try:
        validate_ohlcv(df)
    except ValueError as exc:
        assert "low" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


def test_validate_ohlcv_rejects_positive_infinite_values():
    df = pd.DataFrame(
        {
            "open": [1.1000],
            "high": [float("inf")],
            "low": [1.0990],
            "close": [1.1005],
            "volume": [100],
        },
        index=pd.DatetimeIndex(["2026-01-01 07:00:00"]),
    )

    try:
        validate_ohlcv(df)
    except ValueError as exc:
        assert "finite" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


def test_validate_ohlcv_rejects_negative_infinite_values():
    df = pd.DataFrame(
        {
            "open": [1.1000],
            "high": [1.1010],
            "low": [1.0990],
            "close": [1.1005],
            "volume": [float("-inf")],
        },
        index=pd.DatetimeIndex(["2026-01-01 07:00:00"]),
    )

    try:
        validate_ohlcv(df)
    except ValueError as exc:
        assert "finite" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")
