"""Quarterly walk-forward backtest runner.

Splits M15 data by calendar quarter, runs an independent backtest on each,
and returns per-quarter KPIs so performance evolution is trackable.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from smc_ai.backtest.walkforward import run_walkforward_backtest


def run_quarterly_backtest(
    symbol: str,
    df_d1: pd.DataFrame,
    df_h4: pd.DataFrame,
    df_m15: pd.DataFrame,
    min_rr: float = 2.5,
    scan_step: int = 120,
    d1_lookback: int = 200,
    h4_lookback: int = 500,
    m15_lookback: int = 500,
    sim_horizon: int = 500,
    out_dir: "Path | None" = None,
) -> list[dict]:
    """Run one backtest per calendar quarter found in df_m15.

    For each quarter:
    - M15 bars are restricted to that quarter only (simulation window)
    - D1 and H4 use all bars UP TO the end of the quarter (proper lookback)
    - The m15_lookback warmup comes from bars BEFORE the quarter start

    Returns a list of dicts, one per quarter, each containing:
        quarter, start, end, kpis, trades, equity_curve
    """
    m15 = df_m15.sort_index()
    d1  = df_d1.sort_index()
    h4  = df_h4.sort_index()

    # Build quarter periods from the M15 index
    quarters = _quarter_periods(m15)
    results: list[dict] = []

    for q_label, q_start, q_end in quarters:
        # M15 warmup: m15_lookback bars BEFORE the quarter for context
        pre_q = m15[m15.index < q_start]
        warmup = pre_q.iloc[-m15_lookback:] if len(pre_q) >= m15_lookback else pre_q

        q_m15 = m15[(m15.index >= q_start) & (m15.index <= q_end)]
        if len(q_m15) < scan_step * 2:
            continue  # too few bars in this quarter

        # Concatenate warmup + quarter so the backtest has lookback context
        m15_window = pd.concat([warmup, q_m15]).drop_duplicates()

        # D1 / H4: all bars up to end of quarter
        d1_window = d1[d1.index <= q_end].iloc[-d1_lookback:]
        h4_window = h4[h4.index <= q_end].iloc[-h4_lookback:]

        if len(d1_window) < 2 or len(h4_window) < 3:
            continue

        try:
            result = run_walkforward_backtest(
                symbol=symbol,
                df_d1=d1_window,
                df_h4=h4_window,
                df_m15=m15_window,
                min_rr=min_rr,
                scan_step=scan_step,
                d1_lookback=d1_lookback,
                h4_lookback=h4_lookback,
                m15_lookback=m15_lookback,
                sim_horizon=sim_horizon,
            )
        except Exception as exc:
            print(f"  {q_label}: FAILED — {type(exc).__name__}: {exc}", flush=True)
            results.append({
                "quarter": q_label,
                "start": q_start.isoformat(),
                "end": q_end.isoformat(),
                "error": f"{type(exc).__name__}: {exc}",
                "kpis": {},
                "trades": [],
                "equity_curve": [],
            })
            continue

        q_result = {
            "quarter": q_label,
            "start": q_start.isoformat(),
            "end": q_end.isoformat(),
            "kpis": result.kpis,
            "trades": result.trades,
            "equity_curve": result.equity_curve,
        }
        results.append(q_result)

        msg = (
            f"  {q_label}: {result.kpis.get('total_trades', 0)} trades | "
            f"WR {result.kpis.get('win_rate', 0)*100:.1f}% | "
            f"PF {result.kpis.get('profit_factor', 0):.2f} | "
            f"EV {result.kpis.get('expectancy_r', 0):+.3f}R"
        )
        print(msg, flush=True)

        # Write incremental results so each quarter is readable immediately
        if out_dir is not None:
            import json as _json
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / f"{q_label}.json").write_text(
                _json.dumps(q_result, indent=2, default=str), encoding="utf-8"
            )

    return results


def _quarter_periods(df: pd.DataFrame) -> list[tuple[str, pd.Timestamp, pd.Timestamp]]:
    """Return (label, start, end) for each calendar quarter in df's index."""
    if df.empty:
        return []

    idx = df.index
    tz = idx.tzinfo if hasattr(idx, "tzinfo") else None

    first = idx.min()
    last  = idx.max()

    # Quarter end months: 3, 6, 9, 12
    QUARTER_ENDS = {1: (3, 31), 2: (3, 31), 3: (3, 31),
                    4: (6, 30), 5: (6, 30), 6: (6, 30),
                    7: (9, 30), 8: (9, 30), 9: (9, 30),
                    10: (12, 31), 11: (12, 31), 12: (12, 31)}

    # Floor to quarter start
    q_start_month = ((first.month - 1) // 3) * 3 + 1
    year, month = first.year, q_start_month

    periods: list[tuple[str, pd.Timestamp, pd.Timestamp]] = []
    while True:
        q_num = (month - 1) // 3 + 1
        end_month, end_day = QUARTER_ENDS[month]
        end_year = year if end_month >= month else year + 1

        q_label = f"{year}Q{q_num}"
        q_start = pd.Timestamp(year=year, month=month, day=1, tz=tz)
        q_end   = pd.Timestamp(year=end_year, month=end_month, day=end_day, tz=tz)

        periods.append((q_label, q_start, q_end))

        # Advance to next quarter
        month += 3
        if month > 12:
            month -= 12
            year += 1

        if year > last.year or (year == last.year and month > last.month):
            break

    return periods
