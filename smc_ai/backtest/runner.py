from datetime import UTC, datetime

import pandas as pd

from smc_ai.backtest.models import BacktestResult
from smc_ai.backtest.simulator import simulate_trade
from smc_ai.core.signals import detect_initial_signals
from smc_ai.core.strategy_profiles import get_strategy_profile
from smc_ai.core.trading_math import expectancy_r
from smc_ai.reports.sample_results import make_sample_ohlcv

_RISK_UNIT = 100.0  # dollars per 1R


def run_sample_backtest(symbol: str = "EURUSD", bars: int = 240) -> BacktestResult:
    profile = get_strategy_profile("winworld_smc_v1")
    df = make_sample_ohlcv(bars)
    signals = detect_initial_signals(symbol=symbol, df=df, min_rr=profile.min_rr)

    balance = 10_000.0
    equity_curve: list[dict[str, float | str]] = []
    trades: list[dict[str, object]] = []
    analyses: list[dict[str, object]] = []

    for signal in signals:
        entry_ts = pd.Timestamp(signal.timestamp)
        # Signal fires at close of entry_ts candle; start tracking from the next candle.
        entry_pos = df.index.get_loc(entry_ts)
        if entry_pos + 1 >= len(df):
            from smc_ai.backtest.simulator import SimulatedTrade as _ST
            sim = _ST(
                entry_index=entry_ts, exit_index=None,
                direction=signal.direction, entry=signal.entry,
                stop_loss=signal.stop_loss, take_profit=signal.take_profit,
                outcome="open", pnl_r=0.0,
            )
        else:
            sim = simulate_trade(
                df=df,
                entry=signal.entry,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit,
                direction=signal.direction,
                entry_index=df.index[entry_pos + 1],
            )
        pnl = sim.pnl_r * _RISK_UNIT
        balance += pnl
        trades.append({
            **signal.to_dict(),
            "pnl": round(pnl, 2),
            "pnl_r": sim.pnl_r,
            "outcome": sim.outcome,
            "status": "closed" if sim.outcome != "open" else "open",
        })
        analyses.append(
            {
                "decision": {
                    "symbol": signal.symbol,
                    "timestamp": signal.timestamp,
                    "accepted": True,
                    "direction": signal.direction,
                    "schema": signal.schema,
                    "reason": "sample signal accepted",
                    "poi": None,
                },
                "levels": {
                    "entry": signal.entry,
                    "stop_loss": signal.stop_loss,
                    "take_profit": signal.take_profit,
                    "rr": signal.rr,
                },
                "rejection_reason": None,
            }
        )
        equity_curve.append({"timestamp": signal.timestamp, "equity": round(balance, 2)})

    pnl_r_list = [float(t["pnl_r"]) for t in trades]
    wins_r = [r for r in pnl_r_list if r > 0]
    losses_r = [abs(r) for r in pnl_r_list if r <= 0]
    gross_profit_r = sum(wins_r)
    gross_loss_r = sum(losses_r)
    profit_factor = gross_profit_r / gross_loss_r if gross_loss_r else gross_profit_r
    average_win_r = gross_profit_r / len(wins_r) if wins_r else 0.0
    average_loss_r = gross_loss_r / len(losses_r) if losses_r else 1.0
    win_rate = len(wins_r) / len(pnl_r_list) if pnl_r_list else 0.0

    kpis: dict[str, float | int | str] = {
        "strategy_id": profile.strategy_id,
        "strategy_version": profile.version,
        "starting_balance": 10_000,
        "ending_balance": round(balance, 2),
        "total_trades": len(trades),
        "win_rate": round(win_rate, 4),
        "profit_factor": round(profit_factor, 2),
        "expectancy_r": expectancy_r(
            win_rate=win_rate,
            average_win_r=average_win_r,
            average_loss_r=average_loss_r if average_loss_r > 0 else 1.0,
        )
        if pnl_r_list and wins_r
        else 0.0,
        "max_drawdown": _max_drawdown(equity_curve),
    }

    run_id = f"sample-{symbol}-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
    return BacktestResult(
        run_id=run_id,
        symbol=symbol,
        kpis=kpis,
        equity_curve=equity_curve,
        trades=trades,
        analyses=analyses,
    )


def _max_drawdown(equity_curve: list[dict[str, float | str]]) -> float:
    if not equity_curve:
        return 0.0
    peak = float(equity_curve[0]["equity"])
    max_dd = 0.0
    for point in equity_curve:
        equity = float(point["equity"])
        peak = max(peak, equity)
        if peak > 0:
            dd = (peak - equity) / peak
            max_dd = max(max_dd, dd)
    return round(max_dd, 4)
