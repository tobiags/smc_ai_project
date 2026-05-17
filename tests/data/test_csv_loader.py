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
