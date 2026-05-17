from typing import Final

import pandas as pd


OHLCV_COLUMNS: Final[tuple[str, ...]] = ("open", "high", "low", "close", "volume")


def validate_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    missing = [column for column in OHLCV_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing OHLCV columns: {missing}")

    normalized = df.loc[:, list(OHLCV_COLUMNS)].copy()
    normalized = normalized.astype(float)

    if not isinstance(normalized.index, pd.DatetimeIndex):
        raise ValueError("OHLCV dataframe index must be a DatetimeIndex")

    if normalized.index.isna().any():
        raise ValueError("OHLCV dataframe contains missing timestamps")

    if normalized.empty:
        raise ValueError("OHLCV dataframe must not be empty")

    if normalized.index.has_duplicates:
        raise ValueError("OHLCV dataframe contains duplicate timestamps")

    if normalized.isna().any().any():
        raise ValueError("OHLCV dataframe contains NaN values")

    if (normalized["volume"] < 0).any():
        raise ValueError("OHLCV dataframe contains negative volume")

    if (normalized["high"] < normalized[["open", "close"]].max(axis=1)).any():
        raise ValueError("OHLCV high must be greater than or equal to open and close")

    if (normalized["low"] > normalized[["open", "close"]].min(axis=1)).any():
        raise ValueError("OHLCV low must be less than or equal to open and close")

    return normalized.sort_index()
