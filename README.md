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

Available after the dashboard implementation task:

```powershell
uvicorn smc_ai.dashboard.app:app --reload
```

## Architecture

The SMC core is independent from the dashboard. The dashboard reads JSON results from `results/`.

## Project memory

Durable strategy and architecture memory lives in `brain/`. It is plain markdown today and is
designed to be indexed later by GBrain. Do not store broker credentials or secrets there.
