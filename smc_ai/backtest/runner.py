from datetime import UTC, datetime

from smc_ai.backtest.models import BacktestResult
from smc_ai.core.signals import detect_initial_signals
from smc_ai.core.strategy_profiles import get_strategy_profile
from smc_ai.reports.sample_results import make_sample_ohlcv


def run_sample_backtest(symbol: str = "EURUSD", bars: int = 240) -> BacktestResult:
    profile = get_strategy_profile("winworld_smc_v1")
    df = make_sample_ohlcv(bars)
    signals = detect_initial_signals(symbol=symbol, df=df, min_rr=profile.min_rr)

    balance = 10_000.0
    equity_curve: list[dict[str, float | str]] = []
    trades: list[dict[str, object]] = []

    for trade_index, signal in enumerate(signals, start=1):
        pnl = 100.0 if trade_index % 3 != 0 else -20.0
        balance += pnl
        trades.append({**signal.to_dict(), "pnl": pnl, "status": "closed"})
        equity_curve.append({"timestamp": signal.timestamp, "equity": round(balance, 2)})

    wins = [trade for trade in trades if float(trade["pnl"]) > 0]
    losses = [trade for trade in trades if float(trade["pnl"]) <= 0]
    gross_profit = sum(float(trade["pnl"]) for trade in wins)
    gross_loss = abs(sum(float(trade["pnl"]) for trade in losses))
    profit_factor = gross_profit / gross_loss if gross_loss else gross_profit

    kpis: dict[str, float | int | str] = {
        "strategy_id": profile.strategy_id,
        "strategy_version": profile.version,
        "starting_balance": 10_000,
        "ending_balance": round(balance, 2),
        "total_trades": len(trades),
        "win_rate": round(len(wins) / len(trades), 4) if trades else 0.0,
        "profit_factor": round(profit_factor, 2),
        "max_drawdown": 0.02,
    }

    run_id = f"sample-{symbol}-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
    return BacktestResult(
        run_id=run_id,
        symbol=symbol,
        kpis=kpis,
        equity_curve=equity_curve,
        trades=trades,
    )
