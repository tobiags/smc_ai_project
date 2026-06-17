from datetime import UTC, datetime

import pandas as pd

from smc_ai.backtest.models import BacktestResult
from smc_ai.backtest.simulator import simulate_trade
from smc_ai.core.pipeline import run_multitf_analysis
from smc_ai.core.trading_math import (
    expectancy_r,
    half_kelly,
    kelly_criterion,
    risk_of_ruin,
    signal_to_noise,
    std_dev_r,
    validation_progress,
)

_RISK_UNIT = 100.0  # dollars per 1R


def run_walkforward_backtest(
    symbol: str,
    df_d1: pd.DataFrame,
    df_h4: pd.DataFrame,
    df_m15: pd.DataFrame,
    min_rr: float = 5.0,
    scan_step: int = 40,
    d1_lookback: int = 200,
    h4_lookback: int = 500,
    m15_lookback: int = 1000,
    sim_horizon: int = 200,
) -> BacktestResult:
    """Walk-forward backtest over real OHLCV data.

    Scans through df_m15 every `scan_step` bars. At each position:
    1. Builds non-overlapping data windows (no look-ahead).
    2. Runs multi-TF analysis on those windows.
    3. If a signal is accepted, simulates the trade on the NEXT `sim_horizon` bars.

    Args:
        scan_step:    How many M15 bars to advance between analysis points.
        d1_lookback:  Max D1 bars used for bias computation.
        h4_lookback:  Max H4 bars used for H4 confluence.
        m15_lookback: Max M15 bars in the analysis window.
        sim_horizon:  How many M15 bars after entry to look for TP/SL.
    """
    trades: list[dict[str, object]] = []
    analyses: list[dict[str, object]] = []
    balance = 10_000.0
    equity_curve: list[dict[str, float | str]] = []

    start = m15_lookback
    for pos in range(start, len(df_m15), scan_step):
        current_ts = df_m15.index[pos - 1]

        window_m15 = df_m15.iloc[pos - m15_lookback : pos]
        window_d1 = df_d1[df_d1.index <= current_ts].iloc[-d1_lookback:]
        window_h4 = df_h4[df_h4.index <= current_ts].iloc[-h4_lookback:]

        if len(window_d1) < 2 or len(window_h4) < 3:
            continue

        try:
            analysis = run_multitf_analysis(
                symbol=symbol,
                df_d1=window_d1,
                df_h4=window_h4,
                df_m15=window_m15,
                min_rr=min_rr,
            )
        except Exception:
            continue

        analyses.append(analysis.m15_entry.to_dict())

        if not analysis.m15_entry.decision.accepted or analysis.m15_entry.levels is None:
            continue

        levels = analysis.m15_entry.levels
        sim_df = df_m15.iloc[pos : pos + sim_horizon]
        if sim_df.empty:
            continue

        sim = simulate_trade(
            df=sim_df,
            entry=levels.entry,
            stop_loss=levels.stop_loss,
            take_profit=levels.take_profit,
            direction=analysis.m15_entry.decision.direction,
            entry_index=sim_df.index[0],
        )

        pnl = sim.pnl_r * _RISK_UNIT
        balance += pnl
        trades.append({
            "symbol": symbol,
            "timestamp": current_ts.isoformat(),
            "direction": analysis.m15_entry.decision.direction,
            "entry": levels.entry,
            "stop_loss": levels.stop_loss,
            "take_profit": levels.take_profit,
            "rr": levels.rr,
            "pnl": round(pnl, 2),
            "pnl_r": sim.pnl_r,
            "outcome": sim.outcome,
            "status": "closed" if sim.outcome != "open" else "open",
        })
        equity_curve.append({"timestamp": current_ts.isoformat(), "equity": round(balance, 2)})

    kpis = _compute_kpis(trades, balance)
    run_id = f"wf-{symbol}-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
    return BacktestResult(
        run_id=run_id,
        symbol=symbol,
        kpis=kpis,
        equity_curve=equity_curve,
        trades=trades,
        analyses=analyses,
    )


def _compute_kpis(trades: list[dict[str, object]], ending_balance: float) -> dict[str, float | int | str]:
    pnl_r_list = [float(t["pnl_r"]) for t in trades]
    wins_r = [r for r in pnl_r_list if r > 0]
    losses_r = [abs(r) for r in pnl_r_list if r <= 0]
    gross_profit_r = sum(wins_r)
    gross_loss_r = sum(losses_r)
    profit_factor = gross_profit_r / gross_loss_r if gross_loss_r else gross_profit_r
    average_win_r = gross_profit_r / len(wins_r) if wins_r else 0.0
    average_loss_r = gross_loss_r / len(losses_r) if losses_r else 1.0
    win_rate = len(wins_r) / len(pnl_r_list) if pnl_r_list else 0.0

    eq_values = [10_000.0]
    for t in trades:
        eq_values.append(eq_values[-1] + float(t["pnl"]))
    max_dd = _max_drawdown(eq_values)

    ev = (
        expectancy_r(
            win_rate=win_rate,
            average_win_r=average_win_r,
            average_loss_r=average_loss_r if average_loss_r > 0 else 1.0,
        )
        if pnl_r_list and wins_r
        else 0.0
    )

    rr_ratio = average_win_r / average_loss_r if average_loss_r > 0 else 0.0
    kelly_pct  = kelly_criterion(win_rate, rr_ratio)
    hkelly_pct = half_kelly(win_rate, rr_ratio)

    # n_units = account / risk_per_trade; default: $10,000 at 1% = 100 units
    ror = risk_of_ruin(win_rate, rr_ratio, n_units=100)

    sd    = std_dev_r(pnl_r_list)
    stn   = signal_to_noise(pnl_r_list)
    valid = validation_progress(len(trades), win_rate if win_rate > 0 else 0.5)

    return {
        "starting_balance": 10_000,
        "ending_balance": round(ending_balance, 2),
        "total_trades": len(trades),
        "win_rate": round(win_rate, 4),
        "avg_win_r": round(average_win_r, 4),
        "avg_loss_r": round(average_loss_r, 4),
        "rr_ratio": round(rr_ratio, 4),
        "profit_factor": round(profit_factor, 2),
        "expectancy_r": round(ev, 4),
        "max_drawdown": max_dd,
        # ── Advanced math metrics (from article) ─────────────────────────
        "std_dev_r": sd,
        "signal_to_noise": stn,
        "kelly_pct": kelly_pct,
        "half_kelly_pct": hkelly_pct,
        "risk_of_ruin_pct": round(ror * 100, 6),
        "validation_required": int(valid["required_trades"]),
        "validation_progress_pct": valid["progress_pct"],
        "statistically_confident": valid["confident"],
    }


def _max_drawdown(equity_values: list[float]) -> float:
    if not equity_values:
        return 0.0
    peak = equity_values[0]
    max_dd = 0.0
    for eq in equity_values:
        peak = max(peak, eq)
        if peak > 0:
            max_dd = max(max_dd, (peak - eq) / peak)
    return round(max_dd, 4)
