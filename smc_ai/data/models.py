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

    return normalized.sort_index()
