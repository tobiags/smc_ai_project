# SMC AI Project Start Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first working SMC AI project: independent Python SMC backtest core plus FastAPI/Jinja2/Plotly dashboard reading exported result files.

**Architecture:** The trading/backtest engine is a standalone Python package under `smc_ai/`; the dashboard is a thin visualization layer under `smc_ai/dashboard/`. The first build uses deterministic sample OHLCV data and JSON exports so the app works before MT5/yfinance/VPS integration.

**Tech Stack:** Python 3.12+, pytest, pandas, numpy, FastAPI, Jinja2, Plotly, pydantic-settings, optional smartmoneyconcepts, GSTACK/Browser for dashboard QA.

---

## File Structure Map

Root: `C:\Users\tobid\Downloads\PROJECT TRADING\smc_ai_project`

- `pyproject.toml` — package metadata, dependencies, pytest/ruff config.
- `README.md` — local setup, sample backtest command, dashboard command.
- `.gitignore` — already created; keep `.superpowers/` ignored.
- `smc_ai/config.py` — typed settings, pairs, timeframes, sessions, paths.
- `smc_ai/data/models.py` — OHLCV schema helpers and validation.
- `smc_ai/data/csv_loader.py` — CSV OHLCV loader.
- `smc_ai/data/fetcher.py` — provider registry with CSV first and explicit future MT5/yfinance adapter interface.
- `smc_ai/core/sessions.py` — session classification and allow/block logic.
- `smc_ai/core/indicators.py` — SMC wrapper functions with graceful fallback if `smartmoneyconcepts` is unavailable.
- `smc_ai/core/signals.py` — signal/trade domain models and a deterministic initial signal detector.
- `smc_ai/backtest/models.py` — backtest run/trade/KPI models.
- `smc_ai/backtest/runner.py` — sample backtest runner producing trades and equity curve.
- `smc_ai/backtest/exporter.py` — write/read JSON result files.
- `smc_ai/reports/sample_results.py` — deterministic sample OHLCV/run generator.
- `smc_ai/dashboard/app.py` — FastAPI app factory.
- `smc_ai/dashboard/views.py` — routes.
- `smc_ai/dashboard/templates/*.html` — Jinja pages.
- `smc_ai/dashboard/static/styles.css` — dashboard styling.
- `tests/**` — pytest coverage for each module.
- `docs/vps/deployment.md` — VPS deployment notes.
- `docs/qa/gstack-dashboard-qa.md` — GSTACK/browser QA checklist.

Future, explicitly out of scope for this first implementation:

- `smc_ai/regime/markov.py` — observable Markov chain filter for Bull/Bear/Sideways regimes.
- `smc_ai/regime/hmm.py` — `hmmlearn` GaussianHMM hidden regime filter.
- `smc_ai/regime/macro.py` — Trading Economics macro adapter.
- `smc_ai/regime/scoring.py` — agreement/disagreement scoring against SMC signals.
- `markovify` is not planned because it targets text generation, not financial regime modeling.

---

## Task 1: Project Scaffold and Dependencies

**Files:**
- Create: `C:\Users\tobid\Downloads\PROJECT TRADING\smc_ai_project\pyproject.toml`
- Create: `C:\Users\tobid\Downloads\PROJECT TRADING\smc_ai_project\README.md`
- Create: `C:\Users\tobid\Downloads\PROJECT TRADING\smc_ai_project\smc_ai\__init__.py`
- Create: `C:\Users\tobid\Downloads\PROJECT TRADING\smc_ai_project\tests\test_package_import.py`

- [ ] **Step 1: Write the failing package import test**

Create `tests/test_package_import.py`:

```python
def test_package_imports():
    import smc_ai

    assert smc_ai.__version__ == "0.1.0"
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
rtk pytest tests/test_package_import.py -v
```

Expected: FAIL because `smc_ai` package does not exist yet.

- [ ] **Step 3: Create package and project metadata**

Create `smc_ai/__init__.py`:

```python
"""SMC AI project: independent SMC backtest core plus dashboard."""

__version__ = "0.1.0"
```

Create `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=69", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "smc-ai-project"
version = "0.1.0"
description = "Personal SMC backtester and dashboard"
requires-python = ">=3.12"
dependencies = [
  "fastapi>=0.115",
  "uvicorn[standard]>=0.30",
  "jinja2>=3.1",
  "plotly>=5.24",
  "pandas>=2.2",
  "numpy>=2.0",
  "pydantic>=2.8",
  "pydantic-settings>=2.4",
  "python-multipart>=0.0.9",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.3",
  "httpx>=0.27",
  "ruff>=0.6",
]
smc = [
  "smartmoneyconcepts>=0.0.26",
]

[tool.setuptools.packages.find]
include = ["smc_ai*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]

[tool.ruff]
line-length = 100
target-version = "py312"
```

Create `README.md`:

```markdown
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

```powershell
uvicorn smc_ai.dashboard.app:app --reload
```

## Architecture

The SMC core is independent from the dashboard. The dashboard reads JSON results from `results/`.
```
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
rtk pytest tests/test_package_import.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
rtk git add pyproject.toml README.md smc_ai/__init__.py tests/test_package_import.py
rtk git commit -m "chore: scaffold smc ai package"
```

---

## Task 2: Typed Configuration

**Files:**
- Create: `C:\Users\tobid\Downloads\PROJECT TRADING\smc_ai_project\smc_ai\config.py`
- Test: `C:\Users\tobid\Downloads\PROJECT TRADING\smc_ai_project\tests\test_config.py`

- [ ] **Step 1: Write failing config tests**

Create `tests/test_config.py`:

```python
from pathlib import Path

from smc_ai.config import Settings, get_settings


def test_default_pairs_and_timeframes():
    settings = Settings()

    assert settings.pairs == ("EURUSD", "GBPUSD", "XAUUSD", "USDJPY", "AUDUSD")
    assert settings.timeframes == ("D1", "H4", "M15")
    assert settings.min_rr == 5.0


def test_results_dir_defaults_to_project_results():
    settings = get_settings()

    assert isinstance(settings.results_dir, Path)
    assert settings.results_dir.name == "results"
```

- [ ] **Step 2: Run test to verify it fails**

```powershell
rtk pytest tests/test_config.py -v
```

Expected: FAIL because `smc_ai.config` does not exist.

- [ ] **Step 3: Implement config**

Create `smc_ai/config.py`:

```python
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """Application settings shared by the core and dashboard."""

    model_config = SettingsConfigDict(env_prefix="SMC_", env_file=".env", extra="ignore")

    pairs: tuple[str, ...] = ("EURUSD", "GBPUSD", "XAUUSD", "USDJPY", "AUDUSD")
    crypto_pairs: tuple[str, ...] = ("BTCUSDT", "ETHUSDT")
    timeframes: tuple[str, ...] = ("D1", "H4", "M15")
    entry_timeframe: str = "M15"
    bias_timeframe: str = "D1"
    confluence_timeframe: str = "H4"
    min_rr: float = 5.0
    results_dir: Path = PROJECT_ROOT / "results"
    data_dir: Path = PROJECT_ROOT / "data"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
```

- [ ] **Step 4: Run test to verify it passes**

```powershell
rtk pytest tests/test_config.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
rtk git add smc_ai/config.py tests/test_config.py
rtk git commit -m "feat: add typed project settings"
```

---

## Task 3: OHLCV Data Models and CSV Loader

**Files:**
- Create: `smc_ai/data/__init__.py`
- Create: `smc_ai/data/models.py`
- Create: `smc_ai/data/csv_loader.py`
- Test: `tests/data/test_csv_loader.py`

- [ ] **Step 1: Write failing CSV loader tests**

Create `tests/data/test_csv_loader.py`:

```python
from pathlib import Path

import pandas as pd

from smc_ai.data.csv_loader import load_ohlcv_csv


def test_load_ohlcv_csv_normalizes_columns(tmp_path: Path):
    csv_path = tmp_path / "EURUSD_M15.csv"
    csv_path.write_text(
        "time,open,high,low,close,volume\n"
        "2026-01-01 07:00:00,1.1000,1.1010,1.0990,1.1005,100\n",
        encoding="utf-8",
    )

    df = load_ohlcv_csv(csv_path)

    assert list(df.columns) == ["open", "high", "low", "close", "volume"]
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.iloc[0]["close"] == 1.1005


def test_load_ohlcv_csv_rejects_missing_columns(tmp_path: Path):
    csv_path = tmp_path / "bad.csv"
    csv_path.write_text("time,open,close\n2026-01-01,1.0,1.1\n", encoding="utf-8")

    try:
        load_ohlcv_csv(csv_path)
    except ValueError as exc:
        assert "Missing OHLCV columns" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
```

- [ ] **Step 2: Run tests to verify they fail**

```powershell
rtk pytest tests/data/test_csv_loader.py -v
```

Expected: FAIL because loader files do not exist.

- [ ] **Step 3: Implement data models and CSV loader**

Create `smc_ai/data/__init__.py`:

```python
"""Data loading utilities for OHLCV market data."""
```

Create `smc_ai/data/models.py`:

```python
from typing import Final

import pandas as pd


OHLCV_COLUMNS: Final[tuple[str, ...]] = ("open", "high", "low", "close", "volume")


def validate_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    missing = [column for column in OHLCV_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing OHLCV columns: {missing}")

    normalized = df.loc[:, list(OHLCV_COLUMNS)].copy()
    normalized = normalized.astype(float)

    if not isinstance(normalized.index, pd.DatetimeIndex):
        raise ValueError("OHLCV dataframe index must be a DatetimeIndex")

    return normalized.sort_index()
```

Create `smc_ai/data/csv_loader.py`:

```python
from pathlib import Path

import pandas as pd

from smc_ai.data.models import validate_ohlcv


def load_ohlcv_csv(path: str | Path) -> pd.DataFrame:
    csv_path = Path(path)
    df = pd.read_csv(csv_path)

    if "time" not in df.columns:
        raise ValueError("CSV must contain a 'time' column")

    df["time"] = pd.to_datetime(df["time"], utc=False)
    df = df.set_index("time")
    df.columns = [column.strip().lower() for column in df.columns]

    return validate_ohlcv(df)
```

- [ ] **Step 4: Run tests**

```powershell
rtk pytest tests/data/test_csv_loader.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
rtk git add smc_ai/data tests/data
rtk git commit -m "feat: add csv ohlcv loader"
```

---

## Task 4: Data Fetcher Registry and Sample Data

**Files:**
- Create: `smc_ai/data/fetcher.py`
- Create: `smc_ai/reports/__init__.py`
- Create: `smc_ai/reports/sample_results.py`
- Test: `tests/data/test_fetcher.py`

- [ ] **Step 1: Write failing fetcher tests**

Create `tests/data/test_fetcher.py`:

```python
from smc_ai.data.fetcher import DataFetcher, DataRequest
from smc_ai.reports.sample_results import make_sample_ohlcv


def test_data_fetcher_uses_registered_provider():
    request = DataRequest(symbol="EURUSD", timeframe="M15", bars=10)
    fetcher = DataFetcher()
    fetcher.register("sample", lambda req: make_sample_ohlcv(req.bars))

    df = fetcher.get(request)

    assert len(df) == 10
    assert {"open", "high", "low", "close", "volume"}.issubset(df.columns)


def test_data_fetcher_raises_when_no_provider_registered():
    request = DataRequest(symbol="EURUSD", timeframe="M15", bars=10)
    fetcher = DataFetcher()

    try:
        fetcher.get(request)
    except RuntimeError as exc:
        assert "No data provider succeeded" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError")
```

- [ ] **Step 2: Run tests to verify they fail**

```powershell
rtk pytest tests/data/test_fetcher.py -v
```

Expected: FAIL because `fetcher.py` and sample data do not exist.

- [ ] **Step 3: Implement fetcher and sample data**

Create `smc_ai/data/fetcher.py`:

```python
from collections.abc import Callable
from dataclasses import dataclass

import pandas as pd

from smc_ai.data.models import validate_ohlcv


@dataclass(frozen=True)
class DataRequest:
    symbol: str
    timeframe: str
    bars: int


DataProvider = Callable[[DataRequest], pd.DataFrame]


class DataFetcher:
    """Provider registry. First successful provider wins."""

    def __init__(self) -> None:
        self._providers: list[tuple[str, DataProvider]] = []

    def register(self, name: str, provider: DataProvider) -> None:
        self._providers.append((name, provider))

    def get(self, request: DataRequest) -> pd.DataFrame:
        errors: list[str] = []
        for name, provider in self._providers:
            try:
                return validate_ohlcv(provider(request))
            except Exception as exc:
                errors.append(f"{name}: {exc}")
        raise RuntimeError(f"No data provider succeeded for {request}. Errors: {errors}")
```

Create `smc_ai/reports/__init__.py`:

```python
"""Report and sample data helpers."""
```

Create `smc_ai/reports/sample_results.py`:

```python
import numpy as np
import pandas as pd


def make_sample_ohlcv(bars: int = 200) -> pd.DataFrame:
    index = pd.date_range("2026-01-01 07:00:00", periods=bars, freq="15min")
    base = 1.10 + np.linspace(0, 0.01, bars)
    wave = np.sin(np.linspace(0, 8, bars)) * 0.002
    close = base + wave
    open_ = close - 0.0003
    high = np.maximum(open_, close) + 0.0008
    low = np.minimum(open_, close) - 0.0008
    volume = np.linspace(100, 200, bars)
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=index,
    )
```

- [ ] **Step 4: Run tests**

```powershell
rtk pytest tests/data/test_fetcher.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
rtk git add smc_ai/data/fetcher.py smc_ai/reports tests/data/test_fetcher.py
rtk git commit -m "feat: add data fetcher registry"
```

---

## Task 5: Session Filter

**Files:**
- Create: `smc_ai/core/__init__.py`
- Create: `smc_ai/core/sessions.py`
- Test: `tests/core/test_sessions.py`

- [ ] **Step 1: Write failing session tests**

Create `tests/core/test_sessions.py`:

```python
import pandas as pd

from smc_ai.core.sessions import classify_session, is_trade_allowed


def test_classify_session_utc_hours():
    assert classify_session(pd.Timestamp("2026-01-01 03:00:00")) == "asia"
    assert classify_session(pd.Timestamp("2026-01-01 08:00:00")) == "london"
    assert classify_session(pd.Timestamp("2026-01-01 14:00:00")) == "ny"
    assert classify_session(pd.Timestamp("2026-01-01 22:00:00")) == "off"


def test_trade_allowed_only_london_and_ny():
    assert is_trade_allowed(pd.Timestamp("2026-01-01 03:00:00")) is False
    assert is_trade_allowed(pd.Timestamp("2026-01-01 08:00:00")) is True
    assert is_trade_allowed(pd.Timestamp("2026-01-01 14:00:00")) is True
```

- [ ] **Step 2: Run tests to verify they fail**

```powershell
rtk pytest tests/core/test_sessions.py -v
```

Expected: FAIL because `smc_ai.core.sessions` does not exist.

- [ ] **Step 3: Implement session filter**

Create `smc_ai/core/__init__.py`:

```python
"""Core SMC analysis modules."""
```

Create `smc_ai/core/sessions.py`:

```python
import pandas as pd


def classify_session(timestamp: pd.Timestamp) -> str:
    hour = timestamp.hour
    if 1 <= hour < 7:
        return "asia"
    if 7 <= hour < 13:
        return "london"
    if 13 <= hour < 21:
        return "ny"
    return "off"


def is_trade_allowed(timestamp: pd.Timestamp) -> bool:
    return classify_session(timestamp) in {"london", "ny"}
```

- [ ] **Step 4: Run tests**

```powershell
rtk pytest tests/core/test_sessions.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
rtk git add smc_ai/core tests/core
rtk git commit -m "feat: add trading session filter"
```

---

## Task 6: Signal Domain Models and Initial Detector

**Files:**
- Create: `smc_ai/core/signals.py`
- Test: `tests/core/test_signals.py`

- [ ] **Step 1: Write failing signal tests**

Create `tests/core/test_signals.py`:

```python
from smc_ai.core.signals import Signal, detect_initial_signals
from smc_ai.reports.sample_results import make_sample_ohlcv


def test_signal_rr_calculation():
    signal = Signal(
        symbol="EURUSD",
        timestamp="2026-01-01T08:00:00",
        direction="buy",
        schema="sample",
        entry=1.1000,
        stop_loss=1.0990,
        take_profit=1.1050,
        confidence=0.5,
    )

    assert signal.rr == 5.0


def test_detect_initial_signals_returns_only_min_rr_signals():
    df = make_sample_ohlcv(120)

    signals = detect_initial_signals("EURUSD", df, min_rr=5.0)

    assert signals
    assert all(signal.rr >= 5.0 for signal in signals)
```

- [ ] **Step 2: Run tests to verify they fail**

```powershell
rtk pytest tests/core/test_signals.py -v
```

Expected: FAIL because `signals.py` does not exist.

- [ ] **Step 3: Implement initial signal model and detector**

Create `smc_ai/core/signals.py`:

```python
from dataclasses import asdict, dataclass

import pandas as pd

from smc_ai.core.sessions import is_trade_allowed


@dataclass(frozen=True)
class Signal:
    symbol: str
    timestamp: str
    direction: str
    schema: str
    entry: float
    stop_loss: float
    take_profit: float
    confidence: float

    @property
    def rr(self) -> float:
        risk = abs(self.entry - self.stop_loss)
        reward = abs(self.take_profit - self.entry)
        return round(reward / risk, 2)

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["rr"] = self.rr
        return data


def detect_initial_signals(symbol: str, df: pd.DataFrame, min_rr: float) -> list[Signal]:
    """Deterministic first detector.

    This is not the final WinWorld entry engine. It creates stable sample signals so
    the backtest/export/dashboard loop can be built and tested before full SMC logic.
    """

    signals: list[Signal] = []
    for index_position in range(20, len(df), 40):
        timestamp = df.index[index_position]
        if not is_trade_allowed(timestamp):
            continue

        close = float(df.iloc[index_position]["close"])
        stop_loss = close - 0.001
        take_profit = close + (close - stop_loss) * min_rr
        signal = Signal(
            symbol=symbol,
            timestamp=timestamp.isoformat(),
            direction="buy",
            schema="sample_smc_long",
            entry=round(close, 5),
            stop_loss=round(stop_loss, 5),
            take_profit=round(take_profit, 5),
            confidence=0.50,
        )
        if signal.rr >= min_rr:
            signals.append(signal)
    return signals
```

- [ ] **Step 4: Run tests**

```powershell
rtk pytest tests/core/test_signals.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
rtk git add smc_ai/core/signals.py tests/core/test_signals.py
rtk git commit -m "feat: add initial signal model"
```

---

## Task 7: Backtest Models and Runner

**Files:**
- Create: `smc_ai/backtest/__init__.py`
- Create: `smc_ai/backtest/models.py`
- Create: `smc_ai/backtest/runner.py`
- Test: `tests/backtest/test_runner.py`

- [ ] **Step 1: Write failing backtest tests**

Create `tests/backtest/test_runner.py`:

```python
from smc_ai.backtest.runner import run_sample_backtest


def test_run_sample_backtest_produces_kpis_and_trades():
    result = run_sample_backtest(symbol="EURUSD", bars=160)

    assert result.run_id.startswith("sample-EURUSD-")
    assert result.symbol == "EURUSD"
    assert result.kpis["total_trades"] > 0
    assert "profit_factor" in result.kpis
    assert result.equity_curve
    assert result.trades
```

- [ ] **Step 2: Run test to verify it fails**

```powershell
rtk pytest tests/backtest/test_runner.py -v
```

Expected: FAIL because backtest files do not exist.

- [ ] **Step 3: Implement backtest models and runner**

Create `smc_ai/backtest/__init__.py`:

```python
"""Backtest runner and result export modules."""
```

Create `smc_ai/backtest/models.py`:

```python
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class BacktestResult:
    run_id: str
    symbol: str
    kpis: dict[str, float | int | str]
    equity_curve: list[dict[str, float | str]]
    trades: list[dict[str, object]]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
```

Create `smc_ai/backtest/runner.py`:

```python
from datetime import UTC, datetime

from smc_ai.backtest.models import BacktestResult
from smc_ai.core.signals import detect_initial_signals
from smc_ai.reports.sample_results import make_sample_ohlcv


def run_sample_backtest(symbol: str = "EURUSD", bars: int = 240) -> BacktestResult:
    df = make_sample_ohlcv(bars)
    signals = detect_initial_signals(symbol=symbol, df=df, min_rr=5.0)

    balance = 10_000.0
    equity_curve: list[dict[str, float | str]] = []
    trades: list[dict[str, object]] = []

    for trade_index, signal in enumerate(signals, start=1):
        pnl = 100.0 if trade_index % 3 != 0 else -20.0
        balance += pnl
        trades.append({**signal.to_dict(), "pnl": pnl, "status": "closed"})
        equity_curve.append({"timestamp": signal.timestamp, "equity": round(balance, 2)})

    wins = [trade for trade in trades if float(trade["pnl"]) > 0]
    losses = [trade for trade in trades if float(trade["pnl"]) <= 0]
    gross_profit = sum(float(trade["pnl"]) for trade in wins)
    gross_loss = abs(sum(float(trade["pnl"]) for trade in losses))
    profit_factor = gross_profit / gross_loss if gross_loss else gross_profit

    kpis: dict[str, float | int | str] = {
        "starting_balance": 10_000,
        "ending_balance": round(balance, 2),
        "total_trades": len(trades),
        "win_rate": round(len(wins) / len(trades), 4) if trades else 0.0,
        "profit_factor": round(profit_factor, 2),
        "max_drawdown": 0.02,
    }

    run_id = f"sample-{symbol}-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
    return BacktestResult(
        run_id=run_id,
        symbol=symbol,
        kpis=kpis,
        equity_curve=equity_curve,
        trades=trades,
    )
```

- [ ] **Step 4: Run tests**

```powershell
rtk pytest tests/backtest/test_runner.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
rtk git add smc_ai/backtest tests/backtest
rtk git commit -m "feat: add sample backtest runner"
```

---

## Task 8: Result Exporter

**Files:**
- Create: `smc_ai/backtest/exporter.py`
- Test: `tests/backtest/test_exporter.py`

- [ ] **Step 1: Write failing exporter tests**

Create `tests/backtest/test_exporter.py`:

```python
from smc_ai.backtest.exporter import list_results, read_result, write_result
from smc_ai.backtest.runner import run_sample_backtest


def test_write_read_and_list_result(tmp_path):
    result = run_sample_backtest("EURUSD", bars=160)

    path = write_result(result, tmp_path)
    loaded = read_result(path)
    listed = list_results(tmp_path)

    assert path.exists()
    assert loaded.run_id == result.run_id
    assert listed[0].run_id == result.run_id
```

- [ ] **Step 2: Run tests to verify they fail**

```powershell
rtk pytest tests/backtest/test_exporter.py -v
```

Expected: FAIL because exporter does not exist.

- [ ] **Step 3: Implement exporter**

Create `smc_ai/backtest/exporter.py`:

```python
import json
from pathlib import Path

from smc_ai.backtest.models import BacktestResult


def write_result(result: BacktestResult, results_dir: str | Path) -> Path:
    directory = Path(results_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{result.run_id}.json"
    path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    return path


def read_result(path: str | Path) -> BacktestResult:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return BacktestResult(
        run_id=data["run_id"],
        symbol=data["symbol"],
        kpis=data["kpis"],
        equity_curve=data["equity_curve"],
        trades=data["trades"],
    )


def list_results(results_dir: str | Path) -> list[BacktestResult]:
    directory = Path(results_dir)
    if not directory.exists():
        return []
    return [read_result(path) for path in sorted(directory.glob("*.json"), reverse=True)]
```

- [ ] **Step 4: Run tests**

```powershell
rtk pytest tests/backtest/test_exporter.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
rtk git add smc_ai/backtest/exporter.py tests/backtest/test_exporter.py
rtk git commit -m "feat: add result exporter"
```

---

## Task 9: CLI Entry Point for Sample Run

**Files:**
- Create: `smc_ai/main.py`
- Test: `tests/test_main.py`

- [ ] **Step 1: Write failing CLI test**

Create `tests/test_main.py`:

```python
from smc_ai.main import generate_sample_run


def test_generate_sample_run_writes_json(tmp_path):
    path = generate_sample_run(symbol="EURUSD", results_dir=tmp_path)

    assert path.exists()
    assert path.suffix == ".json"
```

- [ ] **Step 2: Run test to verify it fails**

```powershell
rtk pytest tests/test_main.py -v
```

Expected: FAIL because `smc_ai.main` does not exist.

- [ ] **Step 3: Implement CLI helper**

Create `smc_ai/main.py`:

```python
from pathlib import Path

from smc_ai.backtest.exporter import write_result
from smc_ai.backtest.runner import run_sample_backtest
from smc_ai.config import get_settings


def generate_sample_run(symbol: str = "EURUSD", results_dir: str | Path | None = None) -> Path:
    settings = get_settings()
    target_dir = Path(results_dir) if results_dir is not None else settings.results_dir
    result = run_sample_backtest(symbol=symbol)
    return write_result(result, target_dir)


if __name__ == "__main__":
    output = generate_sample_run()
    print(f"Wrote sample result: {output}")
```

- [ ] **Step 4: Run tests and generate a local sample**

```powershell
rtk pytest tests/test_main.py -v
rtk python -m smc_ai.main
```

Expected: test PASS and one JSON file appears under `results/`.

- [ ] **Step 5: Commit**

```powershell
rtk git add smc_ai/main.py tests/test_main.py results/.gitkeep
rtk git commit -m "feat: add sample run generator"
```

---

## Task 10: FastAPI Dashboard Routes

**Files:**
- Create: `smc_ai/dashboard/__init__.py`
- Create: `smc_ai/dashboard/app.py`
- Create: `smc_ai/dashboard/views.py`
- Test: `tests/dashboard/test_dashboard_routes.py`

- [ ] **Step 1: Write failing dashboard route tests**

Create `tests/dashboard/test_dashboard_routes.py`:

```python
from fastapi.testclient import TestClient

from smc_ai.dashboard.app import create_app


def test_dashboard_home_returns_html():
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert "SMC AI Dashboard" in response.text


def test_dashboard_health_returns_html():
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert "Strategy Health" in response.text
```

- [ ] **Step 2: Run tests to verify they fail**

```powershell
rtk pytest tests/dashboard/test_dashboard_routes.py -v
```

Expected: FAIL because dashboard files do not exist.

- [ ] **Step 3: Implement app and basic routes**

Create `smc_ai/dashboard/__init__.py`:

```python
"""FastAPI dashboard for SMC AI results."""
```

Create `smc_ai/dashboard/app.py`:

```python
from fastapi import FastAPI

from smc_ai.dashboard.views import router


def create_app() -> FastAPI:
    app = FastAPI(title="SMC AI Dashboard")
    app.include_router(router)
    return app


app = create_app()
```

Create `smc_ai/dashboard/views.py`:

```python
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def home() -> str:
    return "<h1>SMC AI Dashboard</h1><p>Backtest overview will appear here.</p>"


@router.get("/health", response_class=HTMLResponse)
def health() -> str:
    return "<h1>Strategy Health</h1><p>Status: sample mode.</p>"
```

- [ ] **Step 4: Run tests**

```powershell
rtk pytest tests/dashboard/test_dashboard_routes.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
rtk git add smc_ai/dashboard tests/dashboard
rtk git commit -m "feat: add dashboard routes"
```

---

## Task 11: Jinja Templates and Plotly Run Detail

**Files:**
- Create: `smc_ai/dashboard/templates/base.html`
- Create: `smc_ai/dashboard/templates/home.html`
- Create: `smc_ai/dashboard/templates/run_detail.html`
- Create: `smc_ai/dashboard/templates/health.html`
- Create: `smc_ai/dashboard/static/styles.css`
- Modify: `smc_ai/dashboard/views.py`
- Test: `tests/dashboard/test_dashboard_templates.py`

- [ ] **Step 1: Write failing template tests**

Create `tests/dashboard/test_dashboard_templates.py`:

```python
from fastapi.testclient import TestClient

from smc_ai.backtest.exporter import write_result
from smc_ai.backtest.runner import run_sample_backtest
from smc_ai.dashboard.app import create_app


def test_run_detail_includes_plotly_chart(tmp_path, monkeypatch):
    result = run_sample_backtest("EURUSD", bars=160)
    write_result(result, tmp_path)
    monkeypatch.setenv("SMC_RESULTS_DIR", str(tmp_path))

    client = TestClient(create_app())
    response = client.get(f"/runs/{result.run_id}")

    assert response.status_code == 200
    assert "Plotly.newPlot" in response.text
    assert "EURUSD" in response.text
```

- [ ] **Step 2: Run test to verify it fails**

```powershell
rtk pytest tests/dashboard/test_dashboard_templates.py -v
```

Expected: FAIL because templates and run route do not exist.

- [ ] **Step 3: Implement templates and Plotly route**

Modify `smc_ai/dashboard/views.py` to use templates:

```python
from pathlib import Path

import plotly.graph_objects as go
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from smc_ai.backtest.exporter import list_results, read_result
from smc_ai.config import get_settings

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    results = list_results(get_settings().results_dir)
    latest = results[0] if results else None
    return templates.TemplateResponse(
        request,
        "home.html",
        {"latest": latest, "results": results[:10]},
    )


@router.get("/runs/{run_id}", response_class=HTMLResponse)
def run_detail(request: Request, run_id: str):
    path = get_settings().results_dir / f"{run_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Run not found")
    result = read_result(path)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[point["timestamp"] for point in result.equity_curve],
            y=[point["equity"] for point in result.equity_curve],
            mode="lines+markers",
            name="Equity",
        )
    )
    chart_html = fig.to_html(full_html=False, include_plotlyjs="cdn")
    return templates.TemplateResponse(
        request,
        "run_detail.html",
        {"result": result, "chart_html": chart_html},
    )


@router.get("/health", response_class=HTMLResponse)
def health(request: Request):
    results = list_results(get_settings().results_dir)
    latest = results[0] if results else None
    return templates.TemplateResponse(request, "health.html", {"latest": latest})
```

Create `smc_ai/dashboard/templates/base.html`:

```html
<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}SMC AI Dashboard{% endblock %}</title>
  <link rel="stylesheet" href="/static/styles.css">
</head>
<body>
  <header class="topbar">
    <h1>SMC AI Dashboard</h1>
    <nav>
      <a href="/">Overview</a>
      <a href="/health">Health</a>
    </nav>
  </header>
  <main class="page">
    {% block content %}{% endblock %}
  </main>
</body>
</html>
```

Create `smc_ai/dashboard/templates/home.html`:

```html
{% extends "base.html" %}
{% block title %}SMC AI Dashboard{% endblock %}
{% block content %}
<section class="panel">
  <h2>Overview</h2>
  {% if latest %}
    <p>Latest run: <a href="/runs/{{ latest.run_id }}">{{ latest.run_id }}</a></p>
    <p>Symbol: {{ latest.symbol }}</p>
    <p>Total trades: {{ latest.kpis.total_trades }}</p>
  {% else %}
    <p>No backtest result found. Run <code>python -m smc_ai.main</code>.</p>
  {% endif %}
</section>
{% endblock %}
```

Create `smc_ai/dashboard/templates/run_detail.html`:

```html
{% extends "base.html" %}
{% block title %}Run {{ result.run_id }}{% endblock %}
{% block content %}
<section class="panel">
  <h2>{{ result.symbol }} — {{ result.run_id }}</h2>
  <div class="kpis">
    {% for key, value in result.kpis.items() %}
      <div class="kpi"><span>{{ key }}</span><strong>{{ value }}</strong></div>
    {% endfor %}
  </div>
  <div class="chart">{{ chart_html | safe }}</div>
  <table>
    <thead><tr><th>Time</th><th>Direction</th><th>Schema</th><th>RR</th><th>PNL</th></tr></thead>
    <tbody>
      {% for trade in result.trades %}
      <tr>
        <td>{{ trade.timestamp }}</td>
        <td>{{ trade.direction }}</td>
        <td>{{ trade.schema }}</td>
        <td>{{ trade.rr }}</td>
        <td>{{ trade.pnl }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</section>
{% endblock %}
```

Create `smc_ai/dashboard/templates/health.html`:

```html
{% extends "base.html" %}
{% block title %}Strategy Health{% endblock %}
{% block content %}
<section class="panel">
  <h2>Strategy Health</h2>
  {% if latest %}
    <p>Status: sample monitoring</p>
    <p>Win rate: {{ latest.kpis.win_rate }}</p>
    <p>Profit factor: {{ latest.kpis.profit_factor }}</p>
    <p>Max drawdown: {{ latest.kpis.max_drawdown }}</p>
  {% else %}
    <p>No result available for health calculation.</p>
  {% endif %}
</section>
{% endblock %}
```

Create `smc_ai/dashboard/static/styles.css`:

```css
body { margin: 0; font-family: Inter, system-ui, sans-serif; background: #f8fafc; color: #0f172a; }
.topbar { display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; background: #0f172a; color: white; }
.topbar a { color: #bfdbfe; margin-left: 16px; text-decoration: none; }
.page { max-width: 1180px; margin: 24px auto; padding: 0 20px; }
.panel { background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; }
.kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin: 16px 0; }
.kpi { border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; }
.kpi span { display: block; color: #64748b; font-size: 13px; }
.kpi strong { font-size: 24px; }
table { width: 100%; border-collapse: collapse; margin-top: 20px; }
th, td { border-bottom: 1px solid #e2e8f0; padding: 10px; text-align: left; }
```

Modify `smc_ai/dashboard/app.py`:

```python
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from smc_ai.dashboard.views import router


def create_app() -> FastAPI:
    app = FastAPI(title="SMC AI Dashboard")
    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    app.include_router(router)
    return app


app = create_app()
```

- [ ] **Step 4: Run tests**

```powershell
rtk pytest tests/dashboard/test_dashboard_templates.py tests/dashboard/test_dashboard_routes.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
rtk git add smc_ai/dashboard tests/dashboard
rtk git commit -m "feat: render dashboard templates"
```

---

## Task 12: GSTACK Dashboard QA Documentation

**Files:**
- Create: `docs/qa/gstack-dashboard-qa.md`
- Create: `docs/vps/deployment.md`

- [ ] **Step 1: Create GSTACK QA checklist**

Create `docs/qa/gstack-dashboard-qa.md`:

```markdown
# GSTACK Dashboard QA

GSTACK is support tooling for dashboard verification. It is not part of the SMC trading core.

## Local QA Flow

1. Generate sample result:

```powershell
rtk python -m smc_ai.main
```

2. Start dashboard:

```powershell
rtk uvicorn smc_ai.dashboard.app:app --reload
```

3. Use Browser/GSTACK to inspect:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/health`
- latest `/runs/{run_id}` page

## Visual Checks

- Header and navigation are visible.
- Latest run appears on home page.
- KPI cards are readable.
- Plotly equity chart renders.
- Trades table does not overflow on desktop width.
- Health page shows WR, PF, and DD.

## Later VPS Canary Checks

After deployment, use GSTACK canary-style checks for:

- home page HTTP 200
- no console errors
- chart visible
- health page visible
```

- [ ] **Step 2: Create VPS deployment note**

Create `docs/vps/deployment.md`:

```markdown
# VPS Deployment Direction

The first VPS deployment hosts only the FastAPI dashboard and `results/` files.

## Initial shape

```text
VPS
├── smc_ai_project/
├── .venv/
├── results/
└── systemd or Coolify process running uvicorn/gunicorn
```

## Run command

```powershell
uvicorn smc_ai.dashboard.app:app --host 0.0.0.0 --port 8000
```

## Reverse proxy

Use Coolify, Caddy, or Nginx to route HTTPS traffic to port `8000`.

## Important boundary

MT5 data access remains local on Windows at first. The VPS dashboard consumes exported result JSON files. Later, a sync job can upload results from the Windows machine to the VPS.
```

- [ ] **Step 3: Commit docs**

```powershell
rtk git add docs/qa/gstack-dashboard-qa.md docs/vps/deployment.md
rtk git commit -m "docs: add dashboard qa and vps notes"
```

---

## Task 13: Full Verification Pass

**Files:**
- Modify only if verification reveals a concrete bug.

- [ ] **Step 1: Install project in editable mode**

```powershell
rtk pip install -e ".[dev]"
```

Expected: dependencies install successfully.

- [ ] **Step 2: Run complete test suite**

```powershell
rtk pytest -v
```

Expected: all tests PASS.

- [ ] **Step 3: Generate a sample result**

```powershell
rtk python -m smc_ai.main
```

Expected: output prints `Wrote sample result: ...` and `results/*.json` exists.

- [ ] **Step 4: Start dashboard manually**

```powershell
rtk uvicorn smc_ai.dashboard.app:app --reload
```

Expected: dashboard available at `http://127.0.0.1:8000/`.

- [ ] **Step 5: Use Browser/GSTACK QA**

Open:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/health
```

Expected:

- home page shows latest run
- health page shows KPIs
- run detail page chart renders with Plotly

- [ ] **Step 6: Commit final fixes if any**

```powershell
rtk git status --short
rtk git add .
rtk git commit -m "fix: address verification issues"
```

Only commit if files changed during verification.

---

## Self-Review

### Spec Coverage

- Independent core: Tasks 2-9.
- Dashboard with FastAPI/Jinja2/Plotly: Tasks 10-11.
- JSON result exports: Task 8.
- Sample run before external data: Tasks 4, 7, 9.
- GSTACK support: Task 12 and Task 13.
- VPS direction: Task 12.

### Placeholder Scan

No unresolved implementation markers are intentionally left in this plan. Future MT5/yfinance/Kronos/Markov/HMM/Trading Economics/live trading work is explicitly out of scope for this first implementation.

### Type Consistency

The plan consistently uses:

- `BacktestResult.run_id`
- `BacktestResult.to_dict()`
- `Signal.to_dict()`
- `Settings.results_dir`
- `DataRequest(symbol, timeframe, bars)`
