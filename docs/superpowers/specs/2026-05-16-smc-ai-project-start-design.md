# SMC AI Project Start Design

**Date:** 2026-05-16  
**Repo:** `https://github.com/tobiags/smc_ai_project.git`  
**Local path:** `C:\Users\tobid\Downloads\PROJECT TRADING\smc_ai_project`  
**Status:** Approved for implementation planning

---

## 1. Goal

Build the first working version of the SMC AI project as a hybrid system:

1. A Python SMC core that is independent, testable, and usable without any dashboard.
2. A FastAPI dashboard that visualizes backtest outputs, trades, KPIs, charts, and strategy health.
3. A deployment path for the user's VPS, where the dashboard can run continuously and expose progress/results.

The dashboard must never become a dependency of the trading logic. It is a cockpit, not the engine.

---

## 2. Approved Architecture

```text
SMC Core Python
  -> fetches/imports OHLCV data
  -> detects structure, POI, sessions, signals
  -> runs backtests
  -> exports JSON/HTML-ready results

FastAPI Dashboard
  -> reads exported run files
  -> renders Jinja2 pages
  -> displays Plotly charts
  -> can be deployed to VPS
```

The first implementation must produce useful local results before VPS deployment.

---

## 3. Scope for the First Build

### In Scope

- Repo scaffold with `pyproject.toml`, `README.md`, `.gitignore`, and package layout.
- Python package `smc_ai`.
- Core configuration for:
  - pairs: `EURUSD`, `GBPUSD`, `XAUUSD`, `USDJPY`, `AUDUSD`
  - timeframes: `D1`, `H4`, `M15`
  - sessions: Asia block, London allow, NY allow
  - risk thresholds: RR minimum `1:5`
- Data loader interface with initial CSV loader and explicit adapter interfaces for future MT5/yfinance integration.
- SMC indicator wrapper layer.
- Simple first backtest runner with deterministic sample data support.
- Result export to JSON.
- FastAPI dashboard using Jinja2 and Plotly.
- Dashboard pages:
  - home overview
  - run detail
  - pair detail
  - strategy health
- GSTACK support for local dashboard QA and future canary-style visual checks.
- `brain/` markdown memory base for durable decisions, strategy notes, experiments, and
  future GBrain indexing.

### Out of Scope for the First Build

- Live trading.
- MT5 `order_send`.
- TradingView Desktop MCP integration.
- Kronos confirmation.
- Markov/HMM regime intelligence.
- Trading Economics macro integration.
- Autoresearch optimization loop.
- Full EA.
- Production authentication.
- GBrain installation/indexing.
- Lossless runtime memory.

These are later phases after the core/backtest/dashboard loop works.

---

## 4. Core Domain Rules to Preserve

The source strategy is Advanced SMC WinWorld, extracted from the user's three NotebookLM PDFs.

The first implementation must preserve these decisions:

- TF hierarchy: `D1 -> H4 -> M15`
- `D1`: directional bias and previous day high/low.
- `H4`: institutional filter via active OB/FVG zones.
- `M15`: structure, POI, and entries.
- BOS requires candle body close beyond structure.
- Wick-only break is a sweep, not a BOS.
- OB validity requires liquidity taken plus valid imbalance.
- Only two true OBs per leg: OB IDM and OB Extreme; middle OBs are liquidity traps.
- Minimum RR is `1:5`.
- First implementation can use simplified deterministic signal logic while preserving interfaces for full WinWorld entry schemas.

---

## 5. Dashboard Requirements

Dashboard stack:

- FastAPI
- Jinja2 templates
- Plotly charts
- Static CSS
- JSON result files as data source

Initial pages:

```text
/                 -> overview: latest run KPIs, pairs, health status
/runs             -> list of backtest runs
/runs/{run_id}    -> run detail: equity curve, trades table, KPIs
/pairs/{symbol}   -> pair detail: per-pair metrics and trades
/health           -> strategy health: WR, PF, DD, alert state
```

The dashboard must be able to run locally with:

```bash
uvicorn smc_ai.dashboard.app:app --reload
```

---

## 6. VPS Direction

The VPS should host only the dashboard and result files at first:

```text
FastAPI dashboard
+ results/ directory
+ optional scheduled runner later
```

The first deployable shape should work behind a reverse proxy such as Caddy, Nginx, or Coolify routing.

The SMC core must also remain executable locally on the user's Windows machine, especially for MT5 data access.

---

## 7. GSTACK Role

GSTACK is included as project support tooling, not trading logic.

Use GSTACK for:

- local dashboard browser QA after FastAPI starts
- screenshot-driven visual checks of `/`, `/runs/{run_id}`, `/health`
- UX review of dashboard readability and information hierarchy
- future canary checks after VPS deployment
- optional benchmark checks if pages become slow

Relevant GSTACK skills/tools later:

- `gstack-browse` or Browser plugin for local dashboard inspection
- `gstack-qa` for iterative web QA once pages exist
- `gstack-canary` after VPS deployment
- `gstack-benchmark` if dashboard performance becomes relevant

GSTACK must not be part of the SMC backtest core. It sits outside the domain model as QA/verification tooling.

---

## 8. File Structure

Target structure:

```text
smc_ai_project/
├── pyproject.toml
├── README.md
├── .gitignore
├── docs/
│   └── superpowers/
│       ├── specs/
│       └── plans/
├── brain/
│   ├── decisions/
│   ├── experiments/
│   ├── strategy/
│   ├── operations/
│   └── weekly-reviews/
├── smc_ai/
│   ├── __init__.py
│   ├── config.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── csv_loader.py
│   │   └── fetcher.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── indicators.py
│   │   ├── bias.py
│   │   ├── sessions.py
│   │   └── signals.py
│   ├── backtest/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── runner.py
│   │   └── exporter.py
│   ├── dashboard/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── views.py
│   │   ├── templates/
│   │   └── static/
│   └── reports/
│       └── sample_results.py
├── tests/
│   ├── data/
│   ├── core/
│   ├── backtest/
│   └── dashboard/
└── results/
```

---

## 9. Testing Strategy

Use test-driven development for the first build.

Minimum verification:

- `pytest`
- unit tests for config, CSV loader, sessions, signal models, backtest result export
- dashboard tests using FastAPI `TestClient`
- run the dashboard locally and inspect with Browser/GSTACK when pages exist

The first version should be able to produce a sample run without external broker data.

---

## 10. Acceptance Criteria

The first implementation is complete when:

1. `pytest` passes.
2. A sample backtest run can be generated from deterministic sample OHLCV data.
3. A JSON result file is written under `results/`.
4. FastAPI dashboard starts locally.
5. Dashboard home page shows latest run KPIs.
6. Run detail page shows a Plotly equity chart and trades table.
7. README explains local setup and first run.
8. Repo has a first commit and can be pushed to `tobiags/smc_ai_project`.

---

## 11. Later Phases

After the first build:

- MT5 real historical data loader.
- yfinance fallback.
- Full WinWorld 8 entry schemas.
- Autoresearch optimization.
- TradingView MCP decision assistant.
- Regime Intelligence:
  - observable Markov chain filter for Bull/Bear/Sideways states
  - `hmmlearn` GaussianHMM for hidden market regimes
  - `Trading Economics` macro adapter for richer future emission variables
  - `HiddenMarkovModels.jl` as conceptual reference only, not a Python dependency
  - `markovify` explicitly excluded because it is text-generation oriented
- Signal Ensemble / Conviction Engine:
  - measure signal family IC and correlation
  - estimate effective breadth instead of overcounting correlated confirmations
  - score valid SMC setups into A+/A/B/C/reject tiers
  - support conservative sizing recommendations after walk-forward tests
  - keep WinWorld SMC validity as the trade permission layer
- Kronos A/B confirmation:
  - A = SMC pure
  - B = SMC + Kronos confirmation
- VPS deployment with canary checks.
- Semi-auto MT5 execution.
- Agentic research/platform roadmap:
  - ARIS-style overnight and weekly research after demo validation
  - TradingAgents-style real-time decision committee
  - QuantDinger-inspired full platform monitoring and audit patterns
  - Qlib research lab for advanced quant experiments
  - AI-Trader-inspired future sharing/signal layer
  - Scientific Agent Skills-inspired research discipline
  - Dash as a future advanced dashboard option if FastAPI/Jinja/Plotly becomes limiting
- Project Memory / GBrain layer:
  - local markdown `brain/` directory for durable project facts
  - later GBrain indexing over decisions, experiments, backtests, strategy rules, operations,
    and weekly reviews
  - Lossless remains optional and postponed until a Hermes/OpenClaw-style runtime actually
    needs searchable raw conversation recall
