from pathlib import Path

import pandas as pd

from smc_ai.data.models import validate_ohlcv


def load_ohlcv_csv(path: str | Path) -> pd.DataFrame:
    csv_path = Path(path)
    df = pd.read_csv(csv_path)

    if "time" not in df.columns:
        raise ValueError("CSV must contain a 'time' column")

    df["time"] = pd.to_datetime(df["time"], utc=False)
    df = df.set_index("time")
    df.columns = [column.strip().lower() for column in df.columns]

    return validate_ohlcv(df)
