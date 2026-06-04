from dataclasses import dataclass

from smc_ai.core.poi import PoiZone


@dataclass(frozen=True)
class TradeLevels:
    entry: float
    stop_loss: float
    take_profit: float
    rr: float

    def to_dict(self) -> dict[str, float]:
        return {
            "entry": self.entry,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "rr": self.rr,
        }


def calculate_trade_levels(
    entry: float,
    direction: str,
    poi: PoiZone,
    min_rr: float,
    buffer: float = 0.0,
) -> TradeLevels:
    if min_rr <= 0:
        raise ValueError("min_rr must be positive")
    if buffer < 0:
        raise ValueError("buffer must be zero or positive")

    if direction == "buy":
        stop_loss = poi.bottom - buffer
        if entry <= stop_loss:
            raise ValueError("entry must be beyond the structural stop")
        risk = entry - stop_loss
        take_profit = entry + risk * min_rr
    elif direction == "sell":
        stop_loss = poi.top + buffer
        if entry >= stop_loss:
            raise ValueError("entry must be beyond the structural stop")
        risk = stop_loss - entry
        take_profit = entry - risk * min_rr
    else:
        raise ValueError("direction must be buy or sell")

    return TradeLevels(
        entry=round(entry, 5),
        stop_loss=round(stop_loss, 5),
        take_profit=round(take_profit, 5),
        rr=round(abs(take_profit - entry) / risk, 2),
    )
