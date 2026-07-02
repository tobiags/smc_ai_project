import numpy as np
import pandas as pd

from smc_ai.core.indicators import calculate_fvg
from smc_ai.data.models import validate_ohlcv


def detect_order_blocks(df: pd.DataFrame, fvg: pd.DataFrame | None = None) -> pd.DataFrame:
    normalized = validate_ohlcv(df)
    fvg = fvg if fvg is not None else calculate_fvg(normalized)
    _validate_fvg_frame(normalized, fvg)

    n = len(normalized)
    index = normalized.index
    highs = normalized["high"].to_numpy(dtype=float)
    lows = normalized["low"].to_numpy(dtype=float)
    fvg_values = fvg["FVG"].to_numpy(dtype=int)

    ob = np.zeros(n, dtype=int)
    top = np.full(n, pd.NA, dtype=object)
    bottom = np.full(n, pd.NA, dtype=object)
    source = np.full(n, pd.NA, dtype=object)
    mitigated = np.full(n, pd.NA, dtype=object)

    for pos in range(1, n - 2):
        source_fvg = int(fvg_values[pos + 2])
        # Bullish OB takes sell-side liquidity (low below previous low);
        # bearish OB takes buy-side liquidity (high above previous high).
        if source_fvg == 1 and lows[pos] < lows[pos - 1]:
            direction = 1
        elif source_fvg == -1 and highs[pos] > highs[pos - 1]:
            direction = -1
        else:
            continue
        ob[pos] = direction
        top[pos] = float(highs[pos])
        bottom[pos] = float(lows[pos])
        source[pos] = index[pos + 2]

    # Mitigation: first future bar whose wick trades back into the OB.
    for pos in np.nonzero(ob)[0]:
        if ob[pos] == 1:
            hits = np.nonzero(lows[pos + 1 :] <= float(bottom[pos]))[0]
        else:
            hits = np.nonzero(highs[pos + 1 :] >= float(top[pos]))[0]
        if hits.size:
            mitigated[pos] = index[pos + 1 + int(hits[0])]

    result = pd.DataFrame({"OB": ob}, index=index)
    result["Top"] = top
    result["Bottom"] = bottom
    result["SourceFVGIndex"] = source
    result["MitigatedIndex"] = mitigated
    return result


def _validate_fvg_frame(df: pd.DataFrame, fvg: pd.DataFrame) -> None:
    if "FVG" not in fvg.columns:
        raise ValueError("fvg must contain an FVG column")
    if not fvg.index.equals(df.index):
        raise ValueError("fvg index must match OHLCV index")
