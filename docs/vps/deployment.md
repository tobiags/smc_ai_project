# VPS Deployment Direction

The first VPS deployment hosts only the FastAPI dashboard and exported `results/` files.

## Initial Shape

```text
VPS
|-- smc_ai_project/
|-- .venv/
|-- results/
`-- systemd, Coolify, or another process manager running uvicorn/gunicorn
```

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Run Command

```powershell
uvicorn smc_ai.dashboard.app:app --host 0.0.0.0 --port 8000
```

## Reverse Proxy

Use Coolify, Caddy, or Nginx to route HTTPS traffic to port `8000`.

## Result Sync

MT5 data access remains local on Windows at first. The VPS dashboard consumes exported JSON result
files. Later, a sync job can upload `results/*.json` from the Windows machine to the VPS.

## Important Boundary

The VPS dashboard is read-only in the first deployment. It must not:

- send MT5 orders
- store broker passwords
- modify strategy parameters without human validation
- run autonomous live execution
