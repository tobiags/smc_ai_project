from pathlib import Path

import pandas as pd

from smc_ai.data.csv_loader import load_ohlcv_csv


def test_load_ohlcv_csv_normalizes_columns(tmp_path: Path):
    csv_path = tmp_path / "EURUSD_M15.csv"
    csv_path.write_text(
        "time,open,high,low,close,volume\n"
        "2026-01-01 07:00:00,1.1000,1.1010,1.0990,1.1005,100\n",
        encoding="utf-8",
    )

    df = load_ohlcv_csv(csv_path)

    assert list(df.columns) == ["open", "high", "low", "close", "volume"]
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.iloc[0]["close"] == 1.1005


def test_load_ohlcv_csv_rejects_missing_columns(tmp_path: Path):
    csv_path = tmp_path / "bad.csv"
    csv_path.write_text("time,open,close\n2026-01-01,1.0,1.1\n", encoding="utf-8")

    try:
        load_ohlcv_csv(csv_path)
    except ValueError as exc:
        assert "Missing OHLCV columns" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_load_ohlcv_csv_normalizes_mixed_case_spaced_headers(tmp_path: Path):
    csv_path = tmp_path / "headers.csv"
    csv_path.write_text(
        " Time , Open , HIGH , low , Close , Volume \n"
        "2026-01-01 07:00:00,1.1000,1.1010,1.0990,1.1005,100\n",
        encoding="utf-8",
    )

    df = load_ohlcv_csv(csv_path)

    assert list(df.columns) == ["open", "high", "low", "close", "volume"]
    assert df.iloc[0]["close"] == 1.1005


def test_load_ohlcv_csv_rejects_duplicate_timestamps(tmp_path: Path):
    csv_path = tmp_path / "duplicate.csv"
    csv_path.write_text(
        "time,open,high,low,close,volume\n"
        "2026-01-01 07:00:00,1.1000,1.1010,1.0990,1.1005,100\n"
        "2026-01-01 07:00:00,1.1005,1.1020,1.1000,1.1010,110\n",
        encoding="utf-8",
    )

    try:
        load_ohlcv_csv(csv_path)
    except ValueError as exc:
        assert "duplicate timestamps" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


def test_load_ohlcv_csv_rejects_invalid_ohlc_geometry(tmp_path: Path):
    csv_path = tmp_path / "invalid_geometry.csv"
    csv_path.write_text(
        "time,open,high,low,close,volume\n"
        "2026-01-01 07:00:00,1.1000,1.0990,1.0980,1.1005,100\n",
        encoding="utf-8",
    )

    try:
        load_ohlcv_csv(csv_path)
    except ValueError as exc:
        assert "high" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


def test_load_ohlcv_csv_rejects_low_above_open_or_close(tmp_path: Path):
    csv_path = tmp_path / "invalid_low.csv"
    csv_path.write_text(
        "time,open,high,low,close,volume\n"
        "2026-01-01 07:00:00,1.1000,1.1020,1.1006,1.1005,100\n",
        encoding="utf-8",
    )

    try:
        load_ohlcv_csv(csv_path)
    except ValueError as exc:
        assert "low" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


def test_load_ohlcv_csv_rejects_negative_volume(tmp_path: Path):
    csv_path = tmp_path / "negative_volume.csv"
    csv_path.write_text(
        "time,open,high,low,close,volume\n"
        "2026-01-01 07:00:00,1.1000,1.1010,1.0990,1.1005,-1\n",
        encoding="utf-8",
    )

    try:
        load_ohlcv_csv(csv_path)
    except ValueError as exc:
        assert "negative volume" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


def test_load_ohlcv_csv_rejects_empty_ohlcv_data(tmp_path: Path):
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("time,open,high,low,close,volume\n", encoding="utf-8")

    try:
        load_ohlcv_csv(csv_path)
    except ValueError as exc:
        assert "empty" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


def test_load_ohlcv_csv_rejects_nan_values(tmp_path: Path):
    csv_path = tmp_path / "nan.csv"
    csv_path.write_text(
        "time,open,high,low,close,volume\n"
        "2026-01-01 07:00:00,1.1000,,1.0990,1.1005,100\n",
        encoding="utf-8",
    )

    try:
        load_ohlcv_csv(csv_path)
    except ValueError as exc:
        assert "nan" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


def test_load_ohlcv_csv_rejects_malformed_time_with_useful_message(tmp_path: Path):
    csv_path = tmp_path / "malformed_time.csv"
    csv_path.write_text(
        "time,open,high,low,close,volume\n"
        "not-a-time,1.1000,1.1010,1.0990,1.1005,100\n",
        encoding="utf-8",
    )

    try:
        load_ohlcv_csv(csv_path)
    except ValueError as exc:
        message = str(exc)
        assert str(csv_path) in message
        assert "time" in message
    else:
        raise AssertionError("Expected ValueError")


def test_load_ohlcv_csv_rejects_missing_time_value(tmp_path: Path):
    csv_path = tmp_path / "missing_time.csv"
    csv_path.write_text(
        "time,open,high,low,close,volume\n"
        ",1.1000,1.1010,1.0990,1.1005,100\n",
        encoding="utf-8",
    )

    try:
        load_ohlcv_csv(csv_path)
    except ValueError as exc:
        message = str(exc).lower()
        assert "timestamp" in message or "time" in message
    else:
        raise AssertionError("Expected ValueError")


def test_load_ohlcv_csv_accepts_broker_gmt_time_format(tmp_path: Path):
    csv_path = tmp_path / "EURUSD_H1.csv"
    csv_path.write_text(
        "Gmt time,Open,High,Low,Close,Volume\n"
        "01.07.2020 00:00:00.000,1.12336,1.12336,1.12275,1.12306,4148.0298\n",
        encoding="utf-8",
    )

    df = load_ohlcv_csv(csv_path)

    assert list(df.columns) == ["open", "high", "low", "close", "volume"]
    assert df.index[0] == pd.Timestamp("2020-07-01 00:00:00")
    assert df.iloc[0]["close"] == 1.12306
