# GSTACK Dashboard QA

GSTACK is support tooling for dashboard verification. It is not part of the SMC trading core.

## Local QA Flow

1. Generate a sample result:

```powershell
rtk python -m smc_ai.main
```

2. Start the dashboard:

```powershell
rtk uvicorn smc_ai.dashboard.app:app --reload
```

3. Inspect these pages with Browser/GSTACK:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/health
http://127.0.0.1:8000/runs/{run_id}
```

## Visual Checks

- Header and navigation are visible.
- Latest run appears on the home page.
- KPI cards are readable.
- Plotly equity chart renders on the run detail page.
- Trades table does not overflow on desktop width.
- Health page shows win rate, profit factor, and max drawdown.

## Later VPS Canary Checks

After deployment, use GSTACK canary-style checks for:

- home page HTTP 200
- no console errors
- chart visible
- health page visible
- latest run link works

## Boundary

GSTACK can inspect the dashboard and help catch visual regressions. It must not receive broker
credentials or direct MT5 execution access.
