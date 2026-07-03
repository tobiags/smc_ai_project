"""Background execution of backtests + Twelve Data fetches for the API.

One backtest at a time (module-level lock). Results are persisted to SQLite
as soon as the run finishes so the frontend can poll GET /api/runs/{id}.
"""
from __future__ import annotations

import threading
from datetime import UTC, datetime
from pathlib import Path

from smc_ai.db import BacktestRun, QuarterResult, Trade, get_session

_run_lock = threading.Lock()

# In-memory state of the current Twelve Data fetch (single-user app)
fetch_state: dict = {"status": "idle", "symbol": None, "message": ""}


def _load_frames(symbol: str, data_dir: Path | None):
    from smc_ai.data.fetcher import DataRequest
    from smc_ai.data.providers.csv_provider import default_fetcher

    fetcher = default_fetcher(data_dir)
    df_d1 = fetcher.get(DataRequest(symbol=symbol, timeframe="D1", bars=0))
    df_h4 = fetcher.get(DataRequest(symbol=symbol, timeframe="H4", bars=0))
    df_m15 = fetcher.get(DataRequest(symbol=symbol, timeframe="M15", bars=0))
    return df_d1, df_h4, df_m15


def _execute_run(run_id: int, data_dir: Path | None) -> None:
    session = get_session()
    run = session.get(BacktestRun, run_id)
    if run is None:
        session.close()
        return

    run.status = "running"
    run.started_at = datetime.now(UTC)
    session.commit()

    try:
        df_d1, df_h4, df_m15 = _load_frames(run.symbol, data_dir)

        if run.kind == "quarterly":
            from smc_ai.backtest.quarterly import run_quarterly_backtest

            quarters = run_quarterly_backtest(
                symbol=run.symbol,
                df_d1=df_d1,
                df_h4=df_h4,
                df_m15=df_m15,
                min_rr=run.min_rr,
                scan_step=run.scan_step,
                sim_horizon=run.sim_horizon,
            )
            for q in quarters:
                session.add(QuarterResult(
                    run_id=run.id,
                    label=q["quarter"],
                    start=q["start"],
                    end=q["end"],
                    kpis=q.get("kpis", {}),
                    equity_curve=q.get("equity_curve", []),
                    error=q.get("error"),
                ))
                for t in q.get("trades", []):
                    session.add(_trade_row(run.id, t, quarter_label=q["quarter"]))
        else:  # full walk-forward
            from smc_ai.backtest.walkforward import run_walkforward_backtest

            result = run_walkforward_backtest(
                symbol=run.symbol,
                df_d1=df_d1,
                df_h4=df_h4,
                df_m15=df_m15,
                min_rr=run.min_rr,
                scan_step=run.scan_step,
                sim_horizon=run.sim_horizon,
            )
            session.add(QuarterResult(
                run_id=run.id,
                label="FULL",
                start=str(df_m15.index.min()),
                end=str(df_m15.index.max()),
                kpis=result.kpis,
                equity_curve=result.equity_curve,
            ))
            for t in result.trades:
                session.add(_trade_row(run.id, t, quarter_label=None))

        run.status = "done"
    except Exception as exc:  # persist the failure so the UI can show it
        run.status = "failed"
        run.error = f"{type(exc).__name__}: {exc}"
    finally:
        run.finished_at = datetime.now(UTC)
        session.commit()
        session.close()
        _run_lock.release()


def _trade_row(run_id: int, t: dict, quarter_label: str | None) -> Trade:
    return Trade(
        run_id=run_id,
        quarter_label=quarter_label,
        symbol=str(t.get("symbol", "")),
        timestamp=str(t.get("timestamp", "")),
        direction=str(t.get("direction", "")),
        entry=float(t.get("entry", 0.0)),
        stop_loss=float(t.get("stop_loss", 0.0)),
        take_profit=float(t.get("take_profit", 0.0)),
        rr=float(t.get("rr", 0.0)),
        pnl=float(t.get("pnl", 0.0)),
        pnl_r=float(t.get("pnl_r", 0.0)),
        outcome=str(t.get("outcome", "")),
        status=str(t.get("status", "")),
    )


def start_run(run_id: int, data_dir: Path | None = None) -> bool:
    """Launch a backtest in a background thread. Returns False if busy."""
    if not _run_lock.acquire(blocking=False):
        return False
    thread = threading.Thread(
        target=_execute_run, args=(run_id, data_dir), daemon=True
    )
    thread.start()
    return True


def is_busy() -> bool:
    if _run_lock.acquire(blocking=False):
        _run_lock.release()
        return False
    return True


# ── Twelve Data fetch ────────────────────────────────────────────────────────

_fetch_lock = threading.Lock()


def _execute_fetch(symbol: str, out_dir: Path, bars_m15: int) -> None:
    try:
        from smc_ai.data.providers.twelvedata_provider import fetch_bulk
        from smc_ai.utils import load_dotenv

        load_dotenv()
        fetch_state.update(status="running", symbol=symbol, message="Téléchargement en cours…")
        results = fetch_bulk(
            symbol,
            out_dir=out_dir,
            bars_per_tf={"D1": 5000, "H4": 5000, "M15": bars_m15},
        )
        fetch_state.update(
            status="done",
            message=f"{len(results)} fichiers enregistrés : {', '.join(results)}",
        )
    except Exception as exc:
        fetch_state.update(status="failed", message=f"{type(exc).__name__}: {exc}")
    finally:
        _fetch_lock.release()


def start_fetch(symbol: str, out_dir: Path, bars_m15: int = 25000) -> bool:
    if not _fetch_lock.acquire(blocking=False):
        return False
    fetch_state.update(status="starting", symbol=symbol, message="")
    thread = threading.Thread(
        target=_execute_fetch, args=(symbol, out_dir, bars_m15), daemon=True
    )
    thread.start()
    return True
