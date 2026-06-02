from pathlib import Path

import pandas as pd

from smc_ai.data.models import validate_ohlcv


TIME_COLUMNS = ("time", "gmt time", "datetime", "date")
TIME_FORMATS = ("%d.%m.%Y %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d")


def load_ohlcv_csv(path: str | Path) -> pd.DataFrame:
    csv_path = Path(path)
    df = pd.read_csv(csv_path)
    df.columns = [column.strip().lower() for column in df.columns]

    time_column = next((column for column in TIME_COLUMNS if column in df.columns), None)
    if time_column is None:
        raise ValueError("CSV must contain a time column")

    df["time"] = _parse_time_column(df[time_column], csv_path)
    if time_column != "time":
        df = df.drop(columns=[time_column])

    df = df.set_index("time")

    return validate_ohlcv(df)


def _parse_time_column(series: pd.Series, csv_path: Path) -> pd.Series:
    for time_format in TIME_FORMATS:
        try:
            return pd.to_datetime(series, format=time_format, utc=False)
        except (TypeError, ValueError):
            continue

    try:
        return pd.to_datetime(series, utc=False)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Failed to parse time column in CSV {csv_path}") from exc
