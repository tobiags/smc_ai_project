import pandas as pd

from smc_ai.data.models import validate_ohlcv


try:
    from smartmoneyconcepts import smc as _smc
except ModuleNotFoundError:
    _smc = None


def calculate_swing_highs_lows(df: pd.DataFrame, swing_length: int = 5) -> pd.DataFrame:
    normalized = validate_ohlcv(df)
    if swing_length < 1:
        raise ValueError("swing_length must be at least 1")

    if _smc is not None:
        return _smc.swing_highs_lows(normalized, swing_length=swing_length)

    return _fallback_swing_highs_lows(normalized, swing_length=swing_length)


def calculate_fvg(df: pd.DataFrame, join_consecutive: bool = True) -> pd.DataFrame:
    normalized = validate_ohlcv(df)
    if _smc is not None:
        return _smc.fvg(normalized, join_consecutive=join_consecutive)

    return _fallback_fvg(normalized)


def _fallback_swing_highs_lows(df: pd.DataFrame, swing_length: int) -> pd.DataFrame:
    result = pd.DataFrame(0, index=df.index, columns=["HighLow"], dtype=int)
    result["Level"] = pd.NA

    for position in range(swing_length, len(df) - swing_length):
        window = df.iloc[position - swing_length : position + swing_length + 1]
        current_high = float(df.iloc[position]["high"])
        current_low = float(df.iloc[position]["low"])

        if current_high == float(window["high"].max()):
            result.iloc[position, result.columns.get_loc("HighLow")] = 1
            result.iloc[position, result.columns.get_loc("Level")] = current_high
        elif current_low == float(window["low"].min()):
            result.iloc[position, result.columns.get_loc("HighLow")] = -1
            result.iloc[position, result.columns.get_loc("Level")] = current_low

    return result


def _fallback_fvg(df: pd.DataFrame) -> pd.DataFrame:
    result = pd.DataFrame(0, index=df.index, columns=["FVG"], dtype=int)
    result["Top"] = pd.NA
    result["Bottom"] = pd.NA
    result["MitigatedIndex"] = pd.NA

    for position in range(2, len(df)):
        current = df.iloc[position]
        two_back = df.iloc[position - 2]

        if float(current["low"]) > float(two_back["high"]):
            result.iloc[position, result.columns.get_loc("FVG")] = 1
            result.iloc[position, result.columns.get_loc("Bottom")] = float(two_back["high"])
            result.iloc[position, result.columns.get_loc("Top")] = float(current["low"])
        elif float(current["high"]) < float(two_back["low"]):
            result.iloc[position, result.columns.get_loc("FVG")] = -1
            result.iloc[position, result.columns.get_loc("Bottom")] = float(current["high"])
            result.iloc[position, result.columns.get_loc("Top")] = float(two_back["low"])

    return result
