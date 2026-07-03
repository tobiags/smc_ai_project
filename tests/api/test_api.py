import json

import pytest
from fastapi.testclient import TestClient

from smc_ai.api.app import create_api, seed_from_quarter_json
from smc_ai.db import BacktestRun, QuarterResult, Trade, get_session, init_db


@pytest.fixture
def client(tmp_path):
    app = create_api(db_path=tmp_path / "test.db", seed=False)
    with TestClient(app) as c:
        yield c


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert isinstance(body["busy"], bool)


def test_runs_empty(client):
    resp = client.get("/api/runs")
    assert resp.status_code == 200
    assert resp.json() == []


def test_run_not_found(client):
    assert client.get("/api/runs/999").status_code == 404


def test_run_detail_with_quarters_and_trades(client):
    session = get_session()
    run = BacktestRun(symbol="EURUSD", kind="quarterly", status="done")
    session.add(run)
    session.flush()
    session.add(QuarterResult(
        run_id=run.id, label="2026Q1", start="2026-01-01", end="2026-03-31",
        kpis={"total_trades": 6, "win_rate": 0.5}, equity_curve=[],
    ))
    session.add(Trade(
        run_id=run.id, quarter_label="2026Q1", symbol="EURUSD",
        timestamp="2026-01-05T10:00:00+00:00", direction="bullish",
        entry=1.05, stop_loss=1.045, take_profit=1.0625, rr=2.5,
        pnl=250.0, pnl_r=2.5, outcome="tp", status="closed",
    ))
    session.commit()
    run_id = run.id
    session.close()

    detail = client.get(f"/api/runs/{run_id}").json()
    assert detail["symbol"] == "EURUSD"
    assert len(detail["quarters"]) == 1
    assert detail["quarters"][0]["kpis"]["win_rate"] == 0.5

    trades = client.get(f"/api/runs/{run_id}/trades").json()
    assert len(trades) == 1
    assert trades[0]["outcome"] == "tp"

    # filter by quarter
    assert client.get(f"/api/runs/{run_id}/trades", params={"quarter": "2025Q4"}).json() == []


def test_delete_run(client):
    session = get_session()
    run = BacktestRun(symbol="EURUSD", kind="quarterly", status="done")
    session.add(run)
    session.commit()
    run_id = run.id
    session.close()

    assert client.delete(f"/api/runs/{run_id}").status_code == 204
    assert client.get(f"/api/runs/{run_id}").status_code == 404


def test_settings_defaults_and_update(client):
    settings = client.get("/api/settings").json()
    assert settings["min_rr"] == "2.5"

    updated = client.put(
        "/api/settings", json={"values": {"min_rr": "3.0", "default_symbol": "XAUUSD"}}
    ).json()
    assert updated["min_rr"] == "3.0"
    assert updated["default_symbol"] == "XAUUSD"

    # persisted
    assert client.get("/api/settings").json()["min_rr"] == "3.0"


def test_seed_from_quarter_json(tmp_path):
    init_db(tmp_path / "seed.db")
    quarters_dir = tmp_path / "quarters"
    quarters_dir.mkdir()
    (quarters_dir / "2026Q1.json").write_text(json.dumps({
        "quarter": "2026Q1",
        "start": "2026-01-01T00:00:00+00:00",
        "end": "2026-03-31T23:59:59+00:00",
        "kpis": {"total_trades": 6},
        "equity_curve": [{"timestamp": "2026-01-05", "equity": 10150.0}],
        "trades": [{
            "symbol": "EURUSD", "timestamp": "2026-01-05T10:00:00+00:00",
            "direction": "bullish", "entry": 1.05, "stop_loss": 1.045,
            "take_profit": 1.0625, "rr": 2.5, "pnl": 250.0, "pnl_r": 2.5,
            "outcome": "tp", "status": "closed",
        }],
    }), encoding="utf-8")

    run_id = seed_from_quarter_json(quarters_dir)
    assert run_id is not None

    session = get_session()
    run = session.get(BacktestRun, run_id)
    assert run.status == "done"
    assert len(run.quarters) == 1
    assert len(run.trades) == 1
    session.close()

    # idempotent: second call does nothing
    assert seed_from_quarter_json(quarters_dir) is None


def test_create_run_returns_id(client, monkeypatch):
    # Don't actually run a backtest — just check the endpoint contract
    from smc_ai.api import runner

    monkeypatch.setattr(runner, "start_run", lambda run_id, data_dir=None: True)
    resp = client.post("/api/runs", json={"symbol": "eurusd", "kind": "quarterly"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "pending"

    runs = client.get("/api/runs").json()
    assert runs[0]["symbol"] == "EURUSD"
