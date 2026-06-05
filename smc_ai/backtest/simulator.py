from dataclasses import dataclass

import pandas as pd

from smc_ai.data.models import validate_ohlcv


@dataclass(frozen=True)
class SimulatedTrade:
    entry_index: pd.Timestamp
    exit_index: pd.Timestamp | None
    direction: str
    entry: float
    stop_loss: float
    take_profit: float
    outcome: str   # "tp" | "sl" | "open"
    pnl_r: float   # profit in R units: +RR for TP, -1 for SL, 0 for open

    def to_dict(self) -> dict[str, object]:
        return {
            "entry_index": str(self.entry_index),
            "exit_index": str(self.exit_index) if self.exit_index is not None else None,
            "direction": self.direction,
            "entry": self.entry,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "outcome": self.outcome,
            "pnl_r": self.pnl_r,
        }


def simulate_trade(
    df: pd.DataFrame,
    entry: float,
    stop_loss: float,
    take_profit: float,
    direction: str,
    entry_index: pd.Timestamp,
) -> SimulatedTrade:
    """Simulate a trade against OHLCV candles from entry_index onward.

    Scans candles in order. For a buy: SL hit if low <= stop_loss, TP hit if high >= take_profit.
    Returns SimulatedTrade with outcome "tp", "sl", or "open" (no exit found).
    pnl_r is in R units: positive = multiple of risk, negative = loss.
    """
    df = validate_ohlcv(df)
    risk = abs(entry - stop_loss)
    rr = abs(take_profit - entry) / risk if risk > 0 else 0.0

    future = df.loc[entry_index:]

    for idx, candle in future.iterrows():
        if direction == "buy":
            if float(candle["low"]) <= stop_loss:
                return SimulatedTrade(
                    entry_index=entry_index, exit_index=idx,
                    direction=direction, entry=entry, stop_loss=stop_loss, take_profit=take_profit,
                    outcome="sl", pnl_r=-1.0,
                )
            if float(candle["high"]) >= take_profit:
                return SimulatedTrade(
                    entry_index=entry_index, exit_index=idx,
                    direction=direction, entry=entry, stop_loss=stop_loss, take_profit=take_profit,
                    outcome="tp", pnl_r=round(rr, 2),
                )
        elif direction == "sell":
            if float(candle["high"]) >= stop_loss:
                return SimulatedTrade(
                    entry_index=entry_index, exit_index=idx,
                    direction=direction, entry=entry, stop_loss=stop_loss, take_profit=take_profit,
                    outcome="sl", pnl_r=-1.0,
                )
            if float(candle["low"]) <= take_profit:
                return SimulatedTrade(
                    entry_index=entry_index, exit_index=idx,
                    direction=direction, entry=entry, stop_loss=stop_loss, take_profit=take_profit,
                    outcome="tp", pnl_r=round(rr, 2),
                )

    return SimulatedTrade(
        entry_index=entry_index, exit_index=None,
        direction=direction, entry=entry, stop_loss=stop_loss, take_profit=take_profit,
        outcome="open", pnl_r=0.0,
    )
