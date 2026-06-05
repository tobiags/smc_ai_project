import pandas as pd

from smc_ai.core.indicators import calculate_fvg
from smc_ai.data.models import validate_ohlcv


def detect_order_blocks(df: pd.DataFrame, fvg: pd.DataFrame | None = None) -> pd.DataFrame:
    normalized = validate_ohlcv(df)
    fvg = fvg if fvg is not None else calculate_fvg(normalized)
    _validate_fvg_frame(normalized, fvg)

    result = pd.DataFrame(0, index=normalized.index, columns=["OB"], dtype=int)
    result["Top"] = pd.NA
    result["Bottom"] = pd.NA
    result["SourceFVGIndex"] = pd.NA
    result["MitigatedIndex"] = pd.NA

    for position in range(1, len(normalized) - 2):
        candidate = normalized.iloc[position]
        previous = normalized.iloc[position - 1]
        source_fvg_index = normalized.index[position + 2]
        source_fvg = int(fvg.loc[source_fvg_index, "FVG"])

        if source_fvg == 1 and _takes_sell_side_liquidity(candidate, previous):
            _mark_order_block(result, normalized.index[position], 1, candidate, source_fvg_index)
        elif source_fvg == -1 and _takes_buy_side_liquidity(candidate, previous):
            _mark_order_block(result, normalized.index[position], -1, candidate, source_fvg_index)

    _mark_mitigated_order_blocks(result, normalized)
    return result


def _mark_mitigated_order_blocks(result: pd.DataFrame, df: pd.DataFrame) -> None:
    ob_indices = result.index[result["OB"] != 0]
    for ob_index in ob_indices:
        ob_direction = int(result.loc[ob_index, "OB"])
        ob_top = float(result.loc[ob_index, "Top"])
        ob_bottom = float(result.loc[ob_index, "Bottom"])
        future = df.loc[ob_index:].iloc[1:]
        for fut_index, candle in future.iterrows():
            if ob_direction == 1 and float(candle["low"]) <= ob_bottom:
                result.loc[ob_index, "MitigatedIndex"] = fut_index
                break
            if ob_direction == -1 and float(candle["high"]) >= ob_top:
                result.loc[ob_index, "MitigatedIndex"] = fut_index
                break


def _validate_fvg_frame(df: pd.DataFrame, fvg: pd.DataFrame) -> None:
    if "FVG" not in fvg.columns:
        raise ValueError("fvg must contain an FVG column")
    if not fvg.index.equals(df.index):
        raise ValueError("fvg index must match OHLCV index")


def _takes_sell_side_liquidity(candidate: pd.Series, previous: pd.Series) -> bool:
    return float(candidate["low"]) < float(previous["low"])


def _takes_buy_side_liquidity(candidate: pd.Series, previous: pd.Series) -> bool:
    return float(candidate["high"]) > float(previous["high"])


def _mark_order_block(
    result: pd.DataFrame,
    index: pd.Timestamp,
    direction: int,
    candle: pd.Series,
    source_fvg_index: pd.Timestamp,
) -> None:
    result.loc[index, "OB"] = direction
    result.loc[index, "Top"] = float(candle["high"])
    result.loc[index, "Bottom"] = float(candle["low"])
    result.loc[index, "SourceFVGIndex"] = source_fvg_index
