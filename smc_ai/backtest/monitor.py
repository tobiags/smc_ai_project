from dataclasses import dataclass


@dataclass(frozen=True)
class HealthStatus:
    level: str  # "ok" | "warning" | "alert" | "critical" | "stop"
    reason: str
    metrics: dict[str, float]

    def to_dict(self) -> dict[str, object]:
        return {"level": self.level, "reason": self.reason, "metrics": self.metrics}


def compute_health(
    trades: list[dict[str, object]],
    rolling_window: int = 30,
) -> HealthStatus:
    """Compute rolling health status from recent trades.

    Thresholds (from WinWorld risk management):
        STOP     : max_drawdown > 18%
        CRITICAL : profit_factor < 1.0 on rolling window
        ALERT    : 6+ consecutive losses
        WARNING  : win_rate < 45% on rolling window
        OK       : all metrics within bounds
    """
    recent = trades[-rolling_window:]
    pnl_r = [float(t["pnl_r"]) for t in recent if "pnl_r" in t]

    wins = [r for r in pnl_r if r > 0]
    losses_abs = [abs(r) for r in pnl_r if r <= 0]
    win_rate = len(wins) / len(pnl_r) if pnl_r else 0.0
    gross_profit = sum(wins)
    gross_loss = sum(losses_abs)
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else gross_profit

    consecutive_losses = _count_consecutive_losses(pnl_r)
    max_drawdown = _compute_max_drawdown_r(pnl_r)

    metrics = {
        "win_rate": round(win_rate, 4),
        "profit_factor": round(profit_factor, 4),
        "consecutive_losses": float(consecutive_losses),
        "max_drawdown_r": round(max_drawdown, 4),
        "total_trades_in_window": float(len(pnl_r)),
    }

    if max_drawdown > 0.18:
        return HealthStatus("stop", f"max drawdown {max_drawdown:.1%} exceeds 18% hard stop", metrics)
    if profit_factor < 1.0 and len(pnl_r) >= 10:
        return HealthStatus("critical", f"profit factor {profit_factor:.2f} < 1.0 on last {len(pnl_r)} trades", metrics)
    if consecutive_losses >= 6:
        return HealthStatus("alert", f"{consecutive_losses} consecutive losses — pause 24h and review", metrics)
    if win_rate < 0.45 and len(pnl_r) >= 10:
        return HealthStatus("warning", f"win rate {win_rate:.1%} < 45% on last {len(pnl_r)} trades", metrics)
    return HealthStatus("ok", "all metrics within acceptable bounds", metrics)


def _count_consecutive_losses(pnl_r: list[float]) -> int:
    count = 0
    for r in reversed(pnl_r):
        if r <= 0:
            count += 1
        else:
            break
    return count


def _compute_max_drawdown_r(pnl_r: list[float]) -> float:
    """Max drawdown expressed as fraction of peak equity (starting at 1.0).

    Assumes 1% account risk per 1R — a conservative default.
    E.g. 25 consecutive -1R losses → equity 0.75 → DD 25%.
    """
    if not pnl_r:
        return 0.0
    equity = 1.0
    peak = 1.0
    max_dd = 0.0
    for r in pnl_r:
        equity += r * 0.01  # 1% risk per 1R
        peak = max(peak, equity)
        if peak > 0:
            max_dd = max(max_dd, (peak - equity) / peak)
    return max_dd
