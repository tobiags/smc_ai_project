"""REST API — pilote toute l'infrastructure SMC depuis le front TanStack Start.

Endpoints:
    GET  /api/health                    état de l'API
    GET  /api/runs                      liste des runs de backtest
    POST /api/runs                      lance un backtest (background)
    GET  /api/runs/{id}                 détail (quarters + KPIs)
    GET  /api/runs/{id}/trades          trades d'un run
    DELETE /api/runs/{id}               supprime un run
    GET  /api/datasets                  fichiers CSV disponibles
    POST /api/datasets/fetch            télécharge des données Twelve Data
    GET  /api/datasets/fetch/status     état du téléchargement
    GET  /api/settings                  paramètres persistés
    PUT  /api/settings                  mise à jour des paramètres
"""
from __future__ import annotations

import json
from contextlib import asynccontextmanager
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import select

from smc_ai.api import runner
from smc_ai.config import get_settings
from smc_ai.db import BacktestRun, QuarterResult, Setting, Trade, get_session, init_db

DEFAULT_SETTINGS = {
    "default_symbol": "EURUSD",
    "min_rr": "2.5",
    "scan_step": "120",
    "sim_horizon": "500",
    "risk_per_trade_pct": "1.0",
    "starting_balance": "10000",
}


class RunCreate(BaseModel):
    symbol: str = "EURUSD"
    kind: str = Field(default="quarterly", pattern="^(quarterly|full)$")
    min_rr: float = 2.5
    scan_step: int = Field(default=120, ge=1)
    sim_horizon: int = Field(default=500, ge=10)


class SettingsUpdate(BaseModel):
    values: dict[str, str]


class FetchRequest(BaseModel):
    symbol: str = "EURUSD"
    bars_m15: int = Field(default=25000, ge=1000, le=100000)


def seed_from_quarter_json(quarters_dir: Path, symbol: str = "EURUSD") -> int | None:
    """Import existing data/quarters/*.json as a 'seed' run if the DB is empty."""
    session = get_session()
    try:
        has_runs = session.execute(select(BacktestRun.id).limit(1)).first()
        if has_runs or not quarters_dir.exists():
            return None
        files = sorted(quarters_dir.glob("*.json"))
        if not files:
            return None

        run = BacktestRun(symbol=symbol, kind="quarterly", status="done")
        session.add(run)
        session.flush()
        for f in files:
            q = json.loads(f.read_text(encoding="utf-8"))
            session.add(QuarterResult(
                run_id=run.id,
                label=q.get("quarter", f.stem),
                start=str(q.get("start", "")),
                end=str(q.get("end", "")),
                kpis=q.get("kpis", {}),
                equity_curve=q.get("equity_curve", []),
                error=q.get("error"),
            ))
            for t in q.get("trades", []):
                session.add(runner._trade_row(run.id, t, quarter_label=q.get("quarter", f.stem)))
        session.commit()
        return run.id
    finally:
        session.close()


def create_api(db_path: Path | None = None, seed: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        init_db(db_path)
        if seed:
            seed_from_quarter_json(get_settings().data_dir / "quarters")
        yield

    app = FastAPI(title="SMC AI API", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Health ───────────────────────────────────────────────────────────

    @app.get("/api/health")
    def health():
        return {"status": "ok", "busy": runner.is_busy()}

    # ── Runs ─────────────────────────────────────────────────────────────

    @app.get("/api/runs")
    def list_runs():
        session = get_session()
        try:
            runs = session.execute(
                select(BacktestRun).order_by(BacktestRun.created_at.desc())
            ).scalars().all()
            return [r.to_dict() for r in runs]
        finally:
            session.close()

    @app.post("/api/runs", status_code=201)
    def create_run(payload: RunCreate):
        if runner.is_busy():
            raise HTTPException(status_code=409, detail="Un backtest est déjà en cours")
        session = get_session()
        try:
            run = BacktestRun(
                symbol=payload.symbol.upper(),
                kind=payload.kind,
                min_rr=payload.min_rr,
                scan_step=payload.scan_step,
                sim_horizon=payload.sim_horizon,
                status="pending",
            )
            session.add(run)
            session.commit()
            run_id = run.id
        finally:
            session.close()

        if not runner.start_run(run_id):
            raise HTTPException(status_code=409, detail="Un backtest est déjà en cours")
        return {"id": run_id, "status": "pending"}

    @app.get("/api/runs/{run_id}")
    def get_run(run_id: int):
        session = get_session()
        try:
            run = session.get(BacktestRun, run_id)
            if run is None:
                raise HTTPException(status_code=404, detail="Run introuvable")
            d = run.to_dict()
            d["quarters"] = [q.to_dict() for q in sorted(run.quarters, key=lambda q: q.label)]
            return d
        finally:
            session.close()

    @app.get("/api/runs/{run_id}/trades")
    def get_run_trades(run_id: int, quarter: str | None = None):
        session = get_session()
        try:
            stmt = select(Trade).where(Trade.run_id == run_id)
            if quarter:
                stmt = stmt.where(Trade.quarter_label == quarter)
            trades = session.execute(stmt.order_by(Trade.timestamp)).scalars().all()
            return [t.to_dict() for t in trades]
        finally:
            session.close()

    @app.delete("/api/runs/{run_id}", status_code=204)
    def delete_run(run_id: int):
        session = get_session()
        try:
            run = session.get(BacktestRun, run_id)
            if run is None:
                raise HTTPException(status_code=404, detail="Run introuvable")
            session.delete(run)
            session.commit()
        finally:
            session.close()

    # ── Datasets ─────────────────────────────────────────────────────────

    @app.get("/api/datasets")
    def list_datasets():
        data_dir = get_settings().data_dir
        out = []
        for csv in sorted(data_dir.glob("*.csv")):
            parts = csv.stem.rsplit("_", 1)
            if len(parts) != 2:
                continue
            symbol, timeframe = parts
            try:
                df = pd.read_csv(csv, usecols=[0])
                first, last = (df.iloc[0, 0], df.iloc[-1, 0]) if len(df) else (None, None)
                rows = len(df)
            except Exception:
                first, last, rows = None, None, 0
            out.append({
                "file": csv.name,
                "symbol": symbol,
                "timeframe": timeframe,
                "rows": rows,
                "first": first,
                "last": last,
                "size_kb": round(csv.stat().st_size / 1024, 1),
            })
        return out

    @app.post("/api/datasets/fetch", status_code=202)
    def fetch_dataset(payload: FetchRequest):
        started = runner.start_fetch(
            payload.symbol.upper(),
            out_dir=get_settings().data_dir,
            bars_m15=payload.bars_m15,
        )
        if not started:
            raise HTTPException(status_code=409, detail="Un téléchargement est déjà en cours")
        return {"started": True, "symbol": payload.symbol.upper()}

    @app.get("/api/datasets/fetch/status")
    def fetch_status():
        return runner.fetch_state

    # ── Settings ─────────────────────────────────────────────────────────

    @app.get("/api/settings")
    def read_settings():
        session = get_session()
        try:
            rows = session.execute(select(Setting)).scalars().all()
            stored = {s.key: s.value for s in rows}
            return {**DEFAULT_SETTINGS, **stored}
        finally:
            session.close()

    @app.put("/api/settings")
    def update_settings(payload: SettingsUpdate):
        session = get_session()
        try:
            for key, value in payload.values.items():
                existing = session.get(Setting, key)
                if existing:
                    existing.value = value
                else:
                    session.add(Setting(key=key, value=value))
            session.commit()
            rows = session.execute(select(Setting)).scalars().all()
            return {**DEFAULT_SETTINGS, **{s.key: s.value for s in rows}}
        finally:
            session.close()

    return app


app = create_api()
