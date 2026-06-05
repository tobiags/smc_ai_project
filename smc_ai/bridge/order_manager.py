"""Order Manager — lot sizing, order construction and MT5 order_send wrapper.

All dollar/pip calculations use conservative approximations suitable for
major Forex pairs. Crypto or CFD symbols may need pip_value adjustments.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:
    import MetaTrader5 as _mt5  # type: ignore[import-untyped]
    MT5_AVAILABLE = True
except ImportError:
    _mt5 = None  # type: ignore[assignment]
    MT5_AVAILABLE = False

MAGIC_NUMBER = 234_001  # identifies all smc_ai orders in MT5


@dataclass(frozen=True)
class OrderResult:
    success: bool
    order_id: int | None
    retcode: int | None
    comment: str

    def __str__(self) -> str:
        if self.success:
            return f"OK — order #{self.order_id}"
        return f"FAILED — retcode={self.retcode} | {self.comment}"


def compute_volume(
    balance: float,
    risk_pct: float,
    entry: float,
    stop_loss: float,
    pip_value_per_lot: float = 10.0,
    min_lot: float = 0.01,
    max_lot: float = 10.0,
) -> float:
    """Calculate lot size for a fixed-percentage risk trade.

    Formula:
        risk_amount  = balance × risk_pct
        risk_pips    = |entry - stop_loss| × 10_000
        lots         = risk_amount / (risk_pips × pip_value_per_lot)

    Args:
        balance:           Account balance in account currency.
        risk_pct:          Fraction of balance to risk (e.g. 0.01 = 1 %).
        entry:             Trade entry price.
        stop_loss:         Stop-loss price.
        pip_value_per_lot: Value of 1 pip for 1 standard lot (default $10
                           for major Forex pairs vs USD).
        min_lot / max_lot: Broker min/max lot sizes.

    Returns the calculated lot size clamped to [min_lot, max_lot].
    """
    risk_distance = abs(entry - stop_loss)
    if risk_distance <= 0:
        return min_lot

    risk_amount = balance * risk_pct
    risk_pips = risk_distance * 10_000          # price distance → pips
    raw_lots = risk_amount / (risk_pips * pip_value_per_lot)
    return max(min_lot, min(max_lot, round(raw_lots, 2)))


def build_order(
    symbol: str,
    direction: str,
    volume: float,
    stop_loss: float,
    take_profit: float,
    schema: str,
    deviation: int = 20,
) -> dict[str, Any]:
    """Build an MT5 order_send request dict using the current market price.

    The entry price is taken from the live bid/ask at the moment of calling.
    """
    if not MT5_AVAILABLE or _mt5 is None:
        raise RuntimeError("MetaTrader5 not available")

    tick = _mt5.symbol_info_tick(symbol)
    if tick is None:
        raise RuntimeError(f"Cannot get tick for {symbol} — is the symbol visible in MT5?")

    if direction == "buy":
        order_type = _mt5.ORDER_TYPE_BUY
        price = float(tick.ask)
    elif direction == "sell":
        order_type = _mt5.ORDER_TYPE_SELL
        price = float(tick.bid)
    else:
        raise ValueError(f"direction must be 'buy' or 'sell', got '{direction}'")

    return {
        "action":      _mt5.TRADE_ACTION_DEAL,
        "symbol":      symbol,
        "volume":      volume,
        "type":        order_type,
        "price":       price,
        "sl":          round(stop_loss, 5),
        "tp":          round(take_profit, 5),
        "deviation":   deviation,
        "magic":       MAGIC_NUMBER,
        "comment":     f"smc_ai_{schema}",
        "type_time":   _mt5.ORDER_TIME_GTC,
        "type_filling": _mt5.ORDER_FILLING_IOC,
    }


def send_order(request: dict[str, Any]) -> OrderResult:
    """Send the order to MT5 and return a structured result."""
    if not MT5_AVAILABLE or _mt5 is None:
        raise RuntimeError("MetaTrader5 not available")

    result = _mt5.order_send(request)

    if result is None:
        code, msg = _mt5.last_error()
        return OrderResult(success=False, order_id=None, retcode=code, comment=msg)

    success = result.retcode == _mt5.TRADE_RETCODE_DONE
    return OrderResult(
        success=success,
        order_id=int(result.order) if success else None,
        retcode=int(result.retcode),
        comment=str(result.comment),
    )


def get_open_positions(symbol: str | None = None) -> list[dict[str, Any]]:
    """Return all open positions managed by smc_ai (magic=MAGIC_NUMBER)."""
    if not MT5_AVAILABLE or _mt5 is None:
        return []

    positions = _mt5.positions_get(symbol=symbol) if symbol else _mt5.positions_get()
    if positions is None:
        return []

    return [
        {
            "ticket":     p.ticket,
            "symbol":     p.symbol,
            "direction":  "buy" if p.type == 0 else "sell",
            "volume":     p.volume,
            "entry":      p.price_open,
            "sl":         p.sl,
            "tp":         p.tp,
            "profit":     p.profit,
            "magic":      p.magic,
        }
        for p in positions
        if p.magic == MAGIC_NUMBER
    ]
