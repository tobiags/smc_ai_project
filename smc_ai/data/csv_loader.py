from pathlib import Path

import pandas as pd

from smc_ai.data.models import validate_ohlcv


def load_ohlcv_csv(path: str | Path) -> pd.DataFrame:
    csv_path = Path(path)
    df = pd.read_csv(csv_path)
    df.columns = [column.strip().lower() for column in df.columns]

    if "time" not in df.columns:
        raise ValueError("CSV must contain a 'time' column")

    try:
        df["time"] = pd.to_datetime(df["time"], utc=False)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Failed to parse 'time' column in CSV {csv_path}") from exc

    df = df.set_index("time")

    return validate_ohlcv(df)
