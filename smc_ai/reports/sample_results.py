import numpy as np
import pandas as pd


def make_sample_ohlcv(bars: int = 200) -> pd.DataFrame:
    index = pd.date_range("2026-01-01 07:00:00", periods=bars, freq="15min")
    base = 1.10 + np.linspace(0, 0.01, bars)
    wave = np.sin(np.linspace(0, 8, bars)) * 0.002
    close = base + wave
    open_ = close - 0.0003
    high = np.maximum(open_, close) + 0.0008
    low = np.minimum(open_, close) - 0.0008
    volume = np.linspace(100, 200, bars)

    return pd.DataFrame(
        {
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        },
        index=index,
    )
