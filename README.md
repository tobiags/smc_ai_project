# SMC AI Project

Personal Advanced SMC backtester and dashboard.

## First local setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest
```

## First dashboard run

Generate a deterministic sample backtest result first:

```powershell
python -m smc_ai.main
```

Then start the dashboard:

```powershell
uvicorn smc_ai.dashboard.app:app --reload
```

Open:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/health
```

## Architecture

The SMC core is independent from the dashboard. The dashboard reads JSON results from `results/`.

Current implemented flow:

```text
sample OHLCV -> sample signals -> sample backtest -> JSON result -> FastAPI dashboard
```

The signal detector is deliberately simple for now. It is a stable scaffold for the dashboard,
export, and backtest loop before the full WinWorld SMC engine is implemented.

## QA and VPS notes

- Dashboard QA checklist: `docs/qa/gstack-dashboard-qa.md`
- VPS deployment direction: `docs/vps/deployment.md`

## Project memory

Durable strategy and architecture memory lives in `brain/`. It is plain markdown today and is
designed to be indexed later by GBrain. Do not store broker credentials or secrets there.
