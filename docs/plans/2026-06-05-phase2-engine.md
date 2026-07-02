# Phase 2 — WinWorld Engine Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implémenter le moteur WinWorld réel : IDM detection, pipeline multi-timeframe (D1→H4→M15), CSV provider branché, et signal generation réel remplaçant les signaux factices.

**Architecture:** Le pipeline suit la hiérarchie D1 (bias) → H4 (confluence) → M15 (entry). L'IDM est la condition requise avant tout signal : un sweep de liquidité confirmé par un BOS/ChoCh en sens inverse. Toute la logique s'enchaîne via `run_multitf_analysis()` qui orchestre les modules existants.

**Tech Stack:** Python 3.12, pandas 2.2, pytest 8.3, modules existants smc_ai.core.*, smc_ai.data.*

---

## Contexte codebase

Modules existants à utiliser (NE PAS recréer) :
- `smc_ai/core/indicators.py` — `calculate_swing_highs_lows`, `calculate_fvg`
- `smc_ai/core/market_structure.py` — `detect_structure_events`, `latest_structure_bias`, `label_market_structure`
- `smc_ai/core/order_blocks.py` — `detect_order_blocks`
- `smc_ai/core/poi.py` — `PoiZone`, `zones_from_fvg`, `zones_from_order_blocks`, `filter_zones_by_confluence`
- `smc_ai/core/entry_pipeline.py` — `scan_latest_m15_entry`, `EntryAnalysis`
- `smc_ai/core/entry_decision.py` — `evaluate_entry_decision`, `EntryDecision`
- `smc_ai/data/csv_loader.py` — `load_ohlcv_csv`
- `smc_ai/data/fetcher.py` — `DataFetcher`, `DataRequest`
- `smc_ai/data/models.py` — `validate_ohlcv`

Run tests : `cd "C:/Users/tobid/Downloads/PROJECT TRADING/smc_ai_project" && python -m pytest tests/ -v`

---

## Task 1 : IDM Detection

**Concept WinWorld :**
Un IDM (Inducement) est un sweep de liquidité (wick au-delà d'un swing) suivi d'un BOS/ChoCh confirmé en sens INVERSE dans une fenêtre de `lookahead` bougies. Cela prouve que le sweep était intentionnel (pour induire des positions perdantes) avant le vrai mouvement.

Règles :
- SWEEP "bullish" (wick au-dessus d'un high) + BOS/CHOCH "bearish" → IDM bearish confirmé
- SWEEP "bearish" (wick en dessous d'un low) + BOS/CHOCH "bullish" → IDM bullish confirmé

**Files :**
- Create: `smc_ai/core/idm.py`
- Create: `tests/core/test_idm.py`

---

### Task 1 — Step 1 : Écrire les tests IDM (en ÉCHEC)

Créer `tests/core/test_idm.py` :

```python
import pandas as pd
import pytest

from smc_ai.core.idm import detect_idm, latest_confirmed_idm


def _events(rows: list[tuple[str, str, str]]) -> pd.DataFrame:
    """Build a minimal events DataFrame from (Event, Direction, BreakType) tuples."""
    index = pd.date_range("2026-01-01 07:00:00", periods=len(rows), freq="15min")
    return pd.DataFrame(
        [
            {"Event": e, "Direction": d, "BreakType": bt, "BrokenStructure": "H", "BrokenLevel": 1.10}
            for e, d, bt in rows
        ],
        index=index,
    )


def test_detect_idm_bullish_sweep_then_bearish_bos():
    events = _events([
        (pd.NA, pd.NA, pd.NA),
        ("SWEEP", "bullish", "wick"),
        (pd.NA, pd.NA, pd.NA),
        ("CHOCH", "bearish", "close"),
    ])

    result = detect_idm(events, lookahead=5)

    assert result.loc[events.index[1], "IDM"] == -1      # bearish IDM at sweep candle
    assert result.loc[events.index[1], "ConfirmIndex"] == events.index[3]


def test_detect_idm_bearish_sweep_then_bullish_bos():
    events = _events([
        (pd.NA, pd.NA, pd.NA),
        ("SWEEP", "bearish", "wick"),
        (pd.NA, pd.NA, pd.NA),
        ("BOS", "bullish", "close"),
    ])

    result = detect_idm(events, lookahead=5)

    assert result.loc[events.index[1], "IDM"] == 1       # bullish IDM at sweep candle
    assert result.loc[events.index[1], "ConfirmIndex"] == events.index[3]


def test_detect_idm_no_idm_when_confirm_is_same_direction():
    events = _events([
        (pd.NA, pd.NA, pd.NA),
        ("SWEEP", "bullish", "wick"),
        (pd.NA, pd.NA, pd.NA),
        ("BOS", "bullish", "close"),  # same direction — NOT an IDM
    ])

    result = detect_idm(events, lookahead=5)

    assert result["IDM"].eq(0).all()


def test_detect_idm_no_idm_when_confirm_is_outside_lookahead():
    events = _events([
        (pd.NA, pd.NA, pd.NA),
        ("SWEEP", "bearish", "wick"),
        (pd.NA, pd.NA, pd.NA),
        (pd.NA, pd.NA, pd.NA),
        (pd.NA, pd.NA, pd.NA),
        ("BOS", "bullish", "close"),  # candle 5 = distance 4 from candle 1
    ])

    result = detect_idm(events, lookahead=3)   # window too small

    assert result["IDM"].eq(0).all()


def test_latest_confirmed_idm_returns_most_recent():
    events = _events([
        (pd.NA, pd.NA, pd.NA),
        ("SWEEP", "bearish", "wick"),
        (pd.NA, pd.NA, pd.NA),
        ("BOS", "bullish", "close"),
        ("SWEEP", "bullish", "wick"),
        ("CHOCH", "bearish", "close"),
    ])

    idm = detect_idm(events, lookahead=5)
    latest = latest_confirmed_idm(idm)

    assert latest is not None
    assert latest["direction"] == "bearish"   # most recent IDM


def test_latest_confirmed_idm_returns_none_when_no_idm():
    events = _events([
        (pd.NA, pd.NA, pd.NA),
        (pd.NA, pd.NA, pd.NA),
    ])

    idm = detect_idm(events, lookahead=5)

    assert latest_confirmed_idm(idm) is None
```

### Task 1 — Step 2 : Vérifier que les tests échouent

```bash
cd "C:/Users/tobid/Downloads/PROJECT TRADING/smc_ai_project" && python -m pytest tests/core/test_idm.py -v
```

Attendu : `ModuleNotFoundError: No module named 'smc_ai.core.idm'`

### Task 1 — Step 3 : Implémenter `smc_ai/core/idm.py`

```python
from typing import Any

import pandas as pd


def detect_idm(events: pd.DataFrame, lookahead: int = 20) -> pd.DataFrame:
    """Detect Inducement (IDM) events.

    An IDM is a SWEEP followed by a confirming BOS/CHOCH in the OPPOSITE
    direction within `lookahead` candles.

    Returns a DataFrame with columns:
        IDM           int  : 0 = none, 1 = bullish IDM, -1 = bearish IDM
        SweptLevel    float: the level swept (from the SWEEP event)
        ConfirmIndex  obj  : Timestamp of the confirming BOS/CHOCH (or pd.NA)
    """
    if lookahead < 1:
        raise ValueError("lookahead must be at least 1")

    result = pd.DataFrame(
        {"IDM": 0, "SweptLevel": pd.NA, "ConfirmIndex": pd.NA},
        index=events.index,
    )

    sweep_mask = events["Event"] == "SWEEP"
    sweep_indices = events.index[sweep_mask]

    all_indices = list(events.index)

    for sweep_idx in sweep_indices:
        sweep_row = events.loc[sweep_idx]
        sweep_direction = str(sweep_row["Direction"]) if not _is_na(sweep_row["Direction"]) else ""
        swept_level = float(sweep_row["BrokenLevel"]) if not _is_na(sweep_row["BrokenLevel"]) else None

        # IDM direction is OPPOSITE to sweep direction
        if sweep_direction == "bullish":
            confirm_direction = "bearish"
            idm_value = -1
        elif sweep_direction == "bearish":
            confirm_direction = "bullish"
            idm_value = 1
        else:
            continue

        pos = all_indices.index(sweep_idx)
        window_end = min(pos + lookahead + 1, len(all_indices))
        future_slice = events.iloc[pos + 1 : window_end]

        confirm_idx = _find_confirming_event(future_slice, confirm_direction)
        if confirm_idx is None:
            continue

        result.loc[sweep_idx, "IDM"] = idm_value
        result.loc[sweep_idx, "SweptLevel"] = swept_level
        result.loc[sweep_idx, "ConfirmIndex"] = confirm_idx

    return result


def latest_confirmed_idm(idm: pd.DataFrame) -> dict[str, Any] | None:
    """Return the most recent confirmed IDM as a dict, or None."""
    confirmed = idm[idm["IDM"] != 0]
    if confirmed.empty:
        return None
    row = confirmed.iloc[-1]
    direction = "bullish" if int(row["IDM"]) == 1 else "bearish"
    return {
        "direction": direction,
        "swept_level": row["SweptLevel"],
        "confirm_index": row["ConfirmIndex"],
        "sweep_index": confirmed.index[-1],
    }


def _find_confirming_event(future: pd.DataFrame, direction: str) -> pd.Timestamp | None:
    for idx, row in future.iterrows():
        event = str(row["Event"]) if not _is_na(row["Event"]) else ""
        row_direction = str(row["Direction"]) if not _is_na(row["Direction"]) else ""
        break_type = str(row["BreakType"]) if not _is_na(row["BreakType"]) else ""
        if event in {"BOS", "CHOCH"} and row_direction == direction and break_type == "close":
            return idx
    return None


def _is_na(value: object) -> bool:
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False
```

### Task 1 — Step 4 : Vérifier que les tests passent

```bash
cd "C:/Users/tobid/Downloads/PROJECT TRADING/smc_ai_project" && python -m pytest tests/core/test_idm.py -v
```

Attendu : `6 passed`

### Task 1 — Step 5 : Commit

```bash
cd "C:/Users/tobid/Downloads/PROJECT TRADING/smc_ai_project" && git add smc_ai/core/idm.py tests/core/test_idm.py && git commit -m "feat: add IDM (inducement) detection with lookahead confirmation"
```

---

## Task 2 : Intégrer IDM dans `entry_decision.py`

WinWorld exige un IDM confirmé avant toute entrée. Ajouter le paramètre `idm_confirmed` à `evaluate_entry_decision`.

**Files :**
- Modify: `smc_ai/core/entry_decision.py`
- Modify: `smc_ai/core/entry_pipeline.py`
- Modify: `tests/core/test_entry_decision.py`
- Modify: `tests/core/test_entry_pipeline.py`

### Task 2 — Step 1 : Ajouter les tests IDM dans `test_entry_decision.py`

Ajouter à la fin de `tests/core/test_entry_decision.py` :

```python
def test_evaluate_entry_decision_rejects_when_idm_not_confirmed():
    poi = PoiZone("OB", "bullish", top=1.120, bottom=1.100, source_index="m15")
    event = pd.Series({
        "Event": "BOS", "Direction": "bullish", "BreakType": "close",
        "BrokenStructure": "HH", "BrokenLevel": 1.12,
    })

    decision = evaluate_entry_decision(
        symbol="EURUSD",
        timestamp=pd.Timestamp("2026-01-01 08:00:00"),
        bias_direction="bullish",
        session_allowed=True,
        structure_event=event,
        confirmed_pois=[poi],
        idm_confirmed=False,
    )

    assert decision.accepted is False
    assert "IDM" in decision.reason
```

### Task 2 — Step 2 : Vérifier que le test échoue

```bash
cd "C:/Users/tobid/Downloads/PROJECT TRADING/smc_ai_project" && python -m pytest tests/core/test_entry_decision.py::test_evaluate_entry_decision_rejects_when_idm_not_confirmed -v
```

Attendu : `TypeError` (unexpected keyword argument `idm_confirmed`)

### Task 2 — Step 3 : Modifier `evaluate_entry_decision` dans `entry_decision.py`

Remplacer la signature et ajouter la vérification IDM :

```python
def evaluate_entry_decision(
    symbol: str,
    timestamp: pd.Timestamp,
    bias_direction: str,
    session_allowed: bool,
    structure_event: pd.Series,
    confirmed_pois: list[PoiZone],
    idm_confirmed: bool = True,   # default True pour rétro-compatibilité des tests existants
) -> EntryDecision:
    if not session_allowed:
        return _reject(symbol, timestamp, "session is not allowed")

    if not idm_confirmed:
        return _reject(symbol, timestamp, "no confirmed IDM for this leg")

    event = str(structure_event.get("Event", ""))
    # ... reste du code inchangé
```

### Task 2 — Step 4 : Propager `idm_confirmed` dans `build_entry_analysis`

Dans `smc_ai/core/entry_pipeline.py`, modifier `build_entry_analysis` :

```python
def build_entry_analysis(
    symbol: str,
    timestamp: pd.Timestamp,
    entry_price: float,
    bias_direction: str,
    session_allowed: bool,
    structure_event: pd.Series,
    confirmed_pois: list[PoiZone],
    min_rr: float,
    stop_buffer: float = 0.0,
    idm_confirmed: bool = True,
) -> EntryAnalysis:
    decision = evaluate_entry_decision(
        symbol=symbol,
        timestamp=timestamp,
        bias_direction=bias_direction,
        session_allowed=session_allowed,
        structure_event=structure_event,
        confirmed_pois=confirmed_pois,
        idm_confirmed=idm_confirmed,
    )
    # ... reste inchangé
```

Et modifier `scan_latest_m15_entry` pour accepter et passer `idm_confirmed` :

```python
def scan_latest_m15_entry(
    symbol: str,
    df_m15: pd.DataFrame,
    bias_direction: str,
    confirmed_pois: list[PoiZone],
    min_rr: float,
    stop_buffer: float = 0.0,
    structure: pd.DataFrame | None = None,
    idm_confirmed: bool = True,
) -> EntryAnalysis:
    # ...
    return build_entry_analysis(
        # ... tous les args existants
        idm_confirmed=idm_confirmed,
    )
```

### Task 2 — Step 5 : Vérifier tous les tests

```bash
cd "C:/Users/tobid/Downloads/PROJECT TRADING/smc_ai_project" && python -m pytest tests/ -v
```

Attendu : tous les tests existants passent + le nouveau test IDM passe.

### Task 2 — Step 6 : Commit

```bash
cd "C:/Users/tobid/Downloads/PROJECT TRADING/smc_ai_project" && git add smc_ai/core/entry_decision.py smc_ai/core/entry_pipeline.py tests/core/test_entry_decision.py tests/core/test_entry_pipeline.py && git commit -m "feat: enforce IDM confirmation in entry decision pipeline"
```

---

## Task 3 : CSV Provider Factory

Le `DataFetcher` a une architecture registry mais zéro provider concret branché. On crée une factory CSV et un `default_fetcher()`.

**Files :**
- Create: `smc_ai/data/providers/__init__.py` (vide)
- Create: `smc_ai/data/providers/csv_provider.py`
- Modify: `smc_ai/data/__init__.py` (créer si absent)
- Create: `tests/data/test_csv_provider.py`

### Task 3 — Step 1 : Écrire les tests CSV provider

Créer `tests/data/test_csv_provider.py` :

```python
import pandas as pd
import pytest

from smc_ai.data.providers.csv_provider import make_csv_provider, default_fetcher
from smc_ai.data.fetcher import DataRequest


def _write_sample_csv(path, symbol: str = "EURUSD", timeframe: str = "M15") -> None:
    index = pd.date_range("2026-01-01 07:00:00", periods=10, freq="15min")
    df = pd.DataFrame({
        "open": [1.10] * 10,
        "high": [1.11] * 10,
        "low": [1.09] * 10,
        "close": [1.105] * 10,
        "volume": [1000] * 10,
    }, index=index)
    df.index.name = "time"
    csv_file = path / f"{symbol}_{timeframe}.csv"
    df.to_csv(csv_file)


def test_make_csv_provider_loads_ohlcv(tmp_path):
    _write_sample_csv(tmp_path)
    provider = make_csv_provider(tmp_path)
    request = DataRequest(symbol="EURUSD", timeframe="M15", bars=10)

    df = provider(request)

    assert list(df.columns) == ["open", "high", "low", "close", "volume"]
    assert len(df) == 10


def test_make_csv_provider_raises_for_missing_file(tmp_path):
    provider = make_csv_provider(tmp_path)
    request = DataRequest(symbol="MISSING", timeframe="M15", bars=10)

    with pytest.raises(FileNotFoundError):
        provider(request)


def test_default_fetcher_is_a_data_fetcher_with_csv_registered(tmp_path):
    _write_sample_csv(tmp_path)
    fetcher = default_fetcher(data_dir=tmp_path)
    request = DataRequest(symbol="EURUSD", timeframe="M15", bars=10)

    df = fetcher.get(request)

    assert len(df) == 10
```

### Task 3 — Step 2 : Vérifier que les tests échouent

```bash
cd "C:/Users/tobid/Downloads/PROJECT TRADING/smc_ai_project" && python -m pytest tests/data/test_csv_provider.py -v
```

Attendu : `ModuleNotFoundError`

### Task 3 — Step 3 : Créer le provider CSV

Créer `smc_ai/data/providers/__init__.py` (vide).

Créer `smc_ai/data/providers/csv_provider.py` :

```python
from pathlib import Path

from smc_ai.data.csv_loader import load_ohlcv_csv
from smc_ai.data.fetcher import DataFetcher, DataProvider, DataRequest


def make_csv_provider(data_dir: Path) -> DataProvider:
    """Return a DataProvider that loads OHLCV from {data_dir}/{symbol}_{timeframe}.csv."""
    data_dir = Path(data_dir)

    def provider(request: DataRequest) -> "pd.DataFrame":  # noqa: F821
        path = data_dir / f"{request.symbol}_{request.timeframe}.csv"
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {path}")
        return load_ohlcv_csv(path)

    return provider


def default_fetcher(data_dir: Path | None = None) -> DataFetcher:
    """Build a DataFetcher with the CSV provider registered."""
    from smc_ai.config import get_settings

    resolved_dir = Path(data_dir) if data_dir is not None else get_settings().data_dir
    fetcher = DataFetcher()
    fetcher.register("csv", make_csv_provider(resolved_dir))
    return fetcher
```

Ajouter l'import pandas manquant en tête du fichier :

```python
import pandas as pd
from pathlib import Path
# ...
```

(Retirer le `noqa: F821` et ajouter l'import `pd`)

### Task 3 — Step 4 : Vérifier les tests

```bash
cd "C:/Users/tobid/Downloads/PROJECT TRADING/smc_ai_project" && python -m pytest tests/data/test_csv_provider.py -v
```

Attendu : `3 passed`

### Task 3 — Step 5 : Commit

```bash
cd "C:/Users/tobid/Downloads/PROJECT TRADING/smc_ai_project" && git add smc_ai/data/providers/ tests/data/test_csv_provider.py && git commit -m "feat: add CSV provider factory and default_fetcher()"
```

---

## Task 4 : Pipeline Multi-Timeframe

C'est le coeur de Phase 2 : orchestrer D1 bias → H4 confluence → M15 entry + IDM.

**Files :**
- Create: `smc_ai/core/pipeline.py`
- Create: `tests/core/test_pipeline.py`

### Task 4 — Step 1 : Écrire les tests pipeline

Créer `tests/core/test_pipeline.py` :

```python
import pandas as pd
import pytest

from smc_ai.core.pipeline import MultiTFAnalysis, run_multitf_analysis


def _ohlcv_trending_up(n: int = 100) -> pd.DataFrame:
    """Uptrending OHLCV data for testing D1 bullish bias."""
    index = pd.date_range("2026-01-01 08:00:00", periods=n, freq="D")
    base = 1.10
    closes = [base + i * 0.001 for i in range(n)]
    return pd.DataFrame(
        {
            "open": [c - 0.0005 for c in closes],
            "high": [c + 0.001 for c in closes],
            "low": [c - 0.001 for c in closes],
            "close": closes,
            "volume": [1000] * n,
        },
        index=index,
    )


def _ohlcv_flat(n: int = 50, freq: str = "h", base: float = 1.10) -> pd.DataFrame:
    """Flat OHLCV data."""
    index = pd.date_range("2026-01-01 08:00:00", periods=n, freq=freq)
    return pd.DataFrame(
        {
            "open": [base] * n,
            "high": [base + 0.001] * n,
            "low": [base - 0.001] * n,
            "close": [base] * n,
            "volume": [1000] * n,
        },
        index=index,
    )


def test_run_multitf_analysis_returns_multitf_analysis():
    df_d1 = _ohlcv_trending_up(60)
    df_h4 = _ohlcv_flat(100, freq="4h")
    df_m15 = _ohlcv_flat(200, freq="15min")

    result = run_multitf_analysis(
        symbol="EURUSD",
        df_d1=df_d1,
        df_h4=df_h4,
        df_m15=df_m15,
        min_rr=5.0,
    )

    assert isinstance(result, MultiTFAnalysis)
    assert result.symbol == "EURUSD"
    assert result.d1_bias in {"bullish", "bearish", "neutral"}
    assert isinstance(result.h4_zones, list)
    assert isinstance(result.m15_entry, object)


def test_run_multitf_analysis_captures_d1_bias():
    df_d1 = _ohlcv_trending_up(60)
    df_h4 = _ohlcv_flat(100, freq="4h")
    df_m15 = _ohlcv_flat(200, freq="15min")

    result = run_multitf_analysis("EURUSD", df_d1, df_h4, df_m15)

    # Uptrending D1 should produce bullish bias
    assert result.d1_bias == "bullish"


def test_run_multitf_analysis_entry_rejected_without_h4_confluence():
    """Without H4 zones, M15 confirmed_pois will be empty → entry rejected."""
    df_d1 = _ohlcv_flat(60, freq="D")
    df_h4 = _ohlcv_flat(100, freq="4h")     # flat → no OBs/FVGs
    df_m15 = _ohlcv_flat(200, freq="15min")

    result = run_multitf_analysis("EURUSD", df_d1, df_h4, df_m15)

    assert result.m15_entry.decision.accepted is False


def test_multitf_analysis_to_dict_is_serialisable():
    df_d1 = _ohlcv_trending_up(60)
    df_h4 = _ohlcv_flat(100, freq="4h")
    df_m15 = _ohlcv_flat(200, freq="15min")

    result = run_multitf_analysis("EURUSD", df_d1, df_h4, df_m15)
    data = result.to_dict()

    assert "symbol" in data
    assert "d1_bias" in data
    assert "h4_zones" in data
    assert "m15_entry" in data
    assert "idm_confirmed" in data
```

### Task 4 — Step 2 : Vérifier que les tests échouent

```bash
cd "C:/Users/tobid/Downloads/PROJECT TRADING/smc_ai_project" && python -m pytest tests/core/test_pipeline.py -v
```

Attendu : `ModuleNotFoundError: No module named 'smc_ai.core.pipeline'`

### Task 4 — Step 3 : Implémenter `smc_ai/core/pipeline.py`

```python
from dataclasses import dataclass

import pandas as pd

from smc_ai.core.entry_pipeline import EntryAnalysis, scan_latest_m15_entry
from smc_ai.core.idm import detect_idm, latest_confirmed_idm
from smc_ai.core.indicators import calculate_fvg
from smc_ai.core.market_structure import (
    detect_structure_events,
    label_market_structure,
    latest_structure_bias,
)
from smc_ai.core.order_blocks import detect_order_blocks
from smc_ai.core.poi import (
    PoiZone,
    filter_zones_by_confluence,
    zones_from_fvg,
    zones_from_order_blocks,
)
from smc_ai.data.models import validate_ohlcv


@dataclass(frozen=True)
class MultiTFAnalysis:
    symbol: str
    d1_bias: str
    h4_zones: list[PoiZone]
    m15_entry: EntryAnalysis
    idm_confirmed: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "symbol": self.symbol,
            "d1_bias": self.d1_bias,
            "h4_zones": [z.to_dict() for z in self.h4_zones],
            "m15_entry": self.m15_entry.to_dict(),
            "idm_confirmed": self.idm_confirmed,
        }


def run_multitf_analysis(
    symbol: str,
    df_d1: pd.DataFrame,
    df_h4: pd.DataFrame,
    df_m15: pd.DataFrame,
    min_rr: float = 5.0,
    swing_length: int = 5,
    stop_buffer: float = 0.0,
) -> MultiTFAnalysis:
    """Orchestrate D1 bias → H4 confluence → M15 entry with IDM confirmation."""
    d1 = validate_ohlcv(df_d1)
    h4 = validate_ohlcv(df_h4)
    m15 = validate_ohlcv(df_m15)

    # Step 1 — D1 directional bias
    d1_structure = label_market_structure(d1, swing_length=swing_length)
    d1_bias = latest_structure_bias(d1_structure)

    # Step 2 — H4 institutional zones
    h4_fvg = calculate_fvg(h4)
    h4_ob = detect_order_blocks(h4, fvg=h4_fvg)
    h4_zones: list[PoiZone] = zones_from_order_blocks(h4_ob) + zones_from_fvg(h4_fvg)

    # Step 3 — M15 zones filtered by H4 confluence
    m15_fvg = calculate_fvg(m15)
    m15_ob = detect_order_blocks(m15, fvg=m15_fvg)
    m15_zones: list[PoiZone] = zones_from_order_blocks(m15_ob) + zones_from_fvg(m15_fvg)
    confirmed_pois = filter_zones_by_confluence(m15_zones, h4_zones)

    # Step 4 — IDM confirmation on M15
    m15_structure = label_market_structure(m15, swing_length=swing_length)
    m15_events = detect_structure_events(m15, structure=m15_structure)
    idm_result = detect_idm(m15_events, lookahead=20)
    idm_info = latest_confirmed_idm(idm_result)
    idm_confirmed = idm_info is not None and idm_info["direction"] == (
        "bullish" if d1_bias == "bullish" else "bearish"
    )

    # Step 5 — M15 entry scan
    m15_entry = scan_latest_m15_entry(
        symbol=symbol,
        df_m15=m15,
        bias_direction=d1_bias,
        confirmed_pois=confirmed_pois,
        min_rr=min_rr,
        stop_buffer=stop_buffer,
        structure=m15_structure,
        idm_confirmed=idm_confirmed,
    )

    return MultiTFAnalysis(
        symbol=symbol,
        d1_bias=d1_bias,
        h4_zones=h4_zones,
        m15_entry=m15_entry,
        idm_confirmed=idm_confirmed,
    )
```

### Task 4 — Step 4 : Vérifier les tests pipeline

```bash
cd "C:/Users/tobid/Downloads/PROJECT TRADING/smc_ai_project" && python -m pytest tests/core/test_pipeline.py -v
```

Attendu : `4 passed`

### Task 4 — Step 5 : Vérifier toute la suite

```bash
cd "C:/Users/tobid/Downloads/PROJECT TRADING/smc_ai_project" && python -m pytest tests/ -v
```

Attendu : tous les tests passent.

### Task 4 — Step 6 : Commit

```bash
cd "C:/Users/tobid/Downloads/PROJECT TRADING/smc_ai_project" && git add smc_ai/core/pipeline.py tests/core/test_pipeline.py && git commit -m "feat: multi-timeframe pipeline D1-H4-M15 with IDM confirmation"
```

---

## Task 5 : Real Signal Generator

Remplacer `detect_initial_signals` (signaux factices) par un générateur réel qui utilise le pipeline multi-TF.

**Files :**
- Modify: `smc_ai/core/signals.py`
- Modify: `tests/core/test_signals.py`

### Task 5 — Step 1 : Ajouter un test pour le générateur réel

Ajouter à `tests/core/test_signals.py` :

```python
def test_generate_signals_from_multitf_uses_pipeline(tmp_path):
    """generate_signals_from_multitf returns Signal list from real pipeline data."""
    from smc_ai.core.signals import generate_signals_from_multitf

    index_d1 = pd.date_range("2026-01-01", periods=60, freq="D")
    closes_d1 = [1.10 + i * 0.001 for i in range(60)]
    df_d1 = pd.DataFrame({
        "open": [c - 0.0005 for c in closes_d1],
        "high": [c + 0.001 for c in closes_d1],
        "low": [c - 0.001 for c in closes_d1],
        "close": closes_d1,
        "volume": [1000] * 60,
    }, index=index_d1)

    index_m = pd.date_range("2026-01-01 08:00:00", periods=100, freq="15min")
    df_flat = pd.DataFrame({
        "open": [1.10] * 100, "high": [1.11] * 100,
        "low": [1.09] * 100, "close": [1.10] * 100, "volume": [1000] * 100,
    }, index=index_m)

    index_h4 = pd.date_range("2026-01-01 08:00:00", periods=50, freq="4h")
    df_h4 = pd.DataFrame({
        "open": [1.10] * 50, "high": [1.11] * 50,
        "low": [1.09] * 50, "close": [1.10] * 50, "volume": [1000] * 50,
    }, index=index_h4)

    signals = generate_signals_from_multitf(
        symbol="EURUSD",
        df_d1=df_d1,
        df_h4=df_h4,
        df_m15=df_flat,
        strategy_id="winworld_smc_v1",
        strategy_version="0.1",
        min_rr=5.0,
    )

    # With flat data, pipeline produces no accepted entry — empty list is valid
    assert isinstance(signals, list)
    for sig in signals:
        assert sig.rr >= 5.0
        assert sig.direction in {"buy", "sell"}
```

### Task 5 — Step 2 : Vérifier que le test échoue

```bash
cd "C:/Users/tobid/Downloads/PROJECT TRADING/smc_ai_project" && python -m pytest tests/core/test_signals.py::test_generate_signals_from_multitf_uses_pipeline -v
```

Attendu : `ImportError: cannot import name 'generate_signals_from_multitf'`

### Task 5 — Step 3 : Implémenter `generate_signals_from_multitf`

Ajouter à la fin de `smc_ai/core/signals.py` :

```python
def generate_signals_from_multitf(
    symbol: str,
    df_d1: "pd.DataFrame",
    df_h4: "pd.DataFrame",
    df_m15: "pd.DataFrame",
    strategy_id: str,
    strategy_version: str,
    min_rr: float = 5.0,
    stop_buffer: float = 0.0,
    confidence: float = 0.70,
) -> list[Signal]:
    """Generate real signals using the multi-timeframe WinWorld pipeline."""
    from smc_ai.core.pipeline import run_multitf_analysis

    analysis = run_multitf_analysis(
        symbol=symbol,
        df_d1=df_d1,
        df_h4=df_h4,
        df_m15=df_m15,
        min_rr=min_rr,
        stop_buffer=stop_buffer,
    )

    if not analysis.m15_entry.decision.accepted or analysis.m15_entry.levels is None:
        return []

    return [
        signal_from_entry_analysis(
            analysis=analysis.m15_entry,
            strategy_id=strategy_id,
            strategy_version=strategy_version,
            confidence=confidence,
        )
    ]
```

Ajouter l'import `import pandas as pd` en haut si absent.

### Task 5 — Step 4 : Vérifier les tests

```bash
cd "C:/Users/tobid/Downloads/PROJECT TRADING/smc_ai_project" && python -m pytest tests/core/test_signals.py -v && python -m pytest tests/ -v
```

Attendu : tous passent.

### Task 5 — Step 5 : Commit

```bash
cd "C:/Users/tobid/Downloads/PROJECT TRADING/smc_ai_project" && git add smc_ai/core/signals.py tests/core/test_signals.py && git commit -m "feat: real signal generator using multi-TF pipeline"
```

---

## Task 6 : Real Backtest Runner (walk-forward simulation)

Remplacer la simulation factice (`pnl = 100 si trade_index % 3 != 0 else -20`) par une simulation réelle depuis Entry/SL/TP.

**Files :**
- Create: `smc_ai/backtest/simulator.py`
- Modify: `smc_ai/backtest/runner.py`
- Create: `tests/backtest/test_simulator.py`

### Task 6 — Step 1 : Écrire les tests du simulateur

Créer `tests/backtest/test_simulator.py` :

```python
import pandas as pd
import pytest

from smc_ai.backtest.simulator import simulate_trade, SimulatedTrade


def _ohlcv_with_tp_hit(entry: float, tp: float, sl: float) -> pd.DataFrame:
    """OHLCV where the first candle hits TP."""
    index = pd.date_range("2026-01-01 08:00:00", periods=3, freq="15min")
    return pd.DataFrame({
        "open": [entry, entry, entry],
        "high": [tp + 0.001, entry + 0.0001, entry + 0.0001],
        "low":  [entry - 0.0001, entry - 0.0001, entry - 0.0001],
        "close": [tp, entry, entry],
        "volume": [1000, 1000, 1000],
    }, index=index)


def _ohlcv_with_sl_hit(entry: float, tp: float, sl: float) -> pd.DataFrame:
    """OHLCV where the first candle hits SL."""
    index = pd.date_range("2026-01-01 08:00:00", periods=3, freq="15min")
    return pd.DataFrame({
        "open": [entry, entry, entry],
        "high": [entry + 0.0001, entry + 0.0001, entry + 0.0001],
        "low":  [sl - 0.001, entry - 0.0001, entry - 0.0001],
        "close": [sl, entry, entry],
        "volume": [1000, 1000, 1000],
    }, index=index)


def test_simulate_trade_detects_tp_hit():
    entry, tp, sl = 1.100, 1.125, 1.095
    df = _ohlcv_with_tp_hit(entry, tp, sl)

    trade = simulate_trade(
        df=df,
        entry=entry,
        stop_loss=sl,
        take_profit=tp,
        direction="buy",
        entry_index=df.index[0],
    )

    assert trade.outcome == "tp"
    assert trade.pnl_r == pytest.approx(5.0, abs=0.1)


def test_simulate_trade_detects_sl_hit():
    entry, tp, sl = 1.100, 1.125, 1.095
    df = _ohlcv_with_sl_hit(entry, tp, sl)

    trade = simulate_trade(
        df=df,
        entry=entry,
        stop_loss=sl,
        take_profit=tp,
        direction="buy",
        entry_index=df.index[0],
    )

    assert trade.outcome == "sl"
    assert trade.pnl_r == pytest.approx(-1.0, abs=0.01)


def test_simulate_trade_is_open_when_neither_hit():
    entry, tp, sl = 1.100, 1.125, 1.095
    index = pd.date_range("2026-01-01 08:00:00", periods=2, freq="15min")
    df = pd.DataFrame({
        "open": [entry, entry], "high": [1.105, 1.107],
        "low": [1.098, 1.099], "close": [1.103, 1.104], "volume": [1000, 1000],
    }, index=index)

    trade = simulate_trade(
        df=df, entry=entry, stop_loss=sl, take_profit=tp, direction="buy",
        entry_index=df.index[0],
    )

    assert trade.outcome == "open"
    assert trade.pnl_r == 0.0
```

### Task 6 — Step 2 : Vérifier que les tests échouent

```bash
cd "C:/Users/tobid/Downloads/PROJECT TRADING/smc_ai_project" && python -m pytest tests/backtest/test_simulator.py -v
```

Attendu : `ModuleNotFoundError: No module named 'smc_ai.backtest.simulator'`

### Task 6 — Step 3 : Implémenter `smc_ai/backtest/simulator.py`

```python
from dataclasses import dataclass

import pandas as pd

from smc_ai.data.models import validate_ohlcv


@dataclass(frozen=True)
class SimulatedTrade:
    entry_index: pd.Timestamp
    exit_index: pd.Timestamp | None
    direction: str
    entry: float
    stop_loss: float
    take_profit: float
    outcome: str   # "tp" | "sl" | "open"
    pnl_r: float   # profit in R units: +RR for TP, -1 for SL, 0 for open

    def to_dict(self) -> dict[str, object]:
        return {
            "entry_index": str(self.entry_index),
            "exit_index": str(self.exit_index) if self.exit_index is not None else None,
            "direction": self.direction,
            "entry": self.entry,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "outcome": self.outcome,
            "pnl_r": self.pnl_r,
        }


def simulate_trade(
    df: pd.DataFrame,
    entry: float,
    stop_loss: float,
    take_profit: float,
    direction: str,
    entry_index: pd.Timestamp,
) -> SimulatedTrade:
    """Simulate a trade against OHLCV candles after entry_index.

    Returns SimulatedTrade with outcome "tp", "sl", or "open".
    pnl_r is in R units: positive = multiple of risk, negative = loss.
    """
    df = validate_ohlcv(df)
    risk = abs(entry - stop_loss)
    rr = abs(take_profit - entry) / risk if risk > 0 else 0.0

    future = df.loc[entry_index:]

    for idx, candle in future.iterrows():
        if direction == "buy":
            if float(candle["low"]) <= stop_loss:
                return SimulatedTrade(
                    entry_index=entry_index, exit_index=idx,
                    direction=direction, entry=entry, stop_loss=stop_loss, take_profit=take_profit,
                    outcome="sl", pnl_r=-1.0,
                )
            if float(candle["high"]) >= take_profit:
                return SimulatedTrade(
                    entry_index=entry_index, exit_index=idx,
                    direction=direction, entry=entry, stop_loss=stop_loss, take_profit=take_profit,
                    outcome="tp", pnl_r=round(rr, 2),
                )
        elif direction == "sell":
            if float(candle["high"]) >= stop_loss:
                return SimulatedTrade(
                    entry_index=entry_index, exit_index=idx,
                    direction=direction, entry=entry, stop_loss=stop_loss, take_profit=take_profit,
                    outcome="sl", pnl_r=-1.0,
                )
            if float(candle["low"]) <= take_profit:
                return SimulatedTrade(
                    entry_index=entry_index, exit_index=idx,
                    direction=direction, entry=entry, stop_loss=stop_loss, take_profit=take_profit,
                    outcome="tp", pnl_r=round(rr, 2),
                )

    return SimulatedTrade(
        entry_index=entry_index, exit_index=None,
        direction=direction, entry=entry, stop_loss=stop_loss, take_profit=take_profit,
        outcome="open", pnl_r=0.0,
    )
```

### Task 6 — Step 4 : Vérifier les tests simulateur

```bash
cd "C:/Users/tobid/Downloads/PROJECT TRADING/smc_ai_project" && python -m pytest tests/backtest/test_simulator.py -v
```

Attendu : `3 passed`

### Task 6 — Step 5 : Vérifier toute la suite

```bash
cd "C:/Users/tobid/Downloads/PROJECT TRADING/smc_ai_project" && python -m pytest tests/ -v
```

Attendu : tous les tests passent (107 + nouveaux).

### Task 6 — Step 6 : Commit

```bash
cd "C:/Users/tobid/Downloads/PROJECT TRADING/smc_ai_project" && git add smc_ai/backtest/simulator.py tests/backtest/test_simulator.py && git commit -m "feat: trade simulator with R-unit PnL tracking (TP/SL detection)"
```

---

## Vérification finale

Après toutes les tâches :

```bash
cd "C:/Users/tobid/Downloads/PROJECT TRADING/smc_ai_project" && python -m pytest tests/ -v --tb=short
```

Attendu : 100% pass, zéro erreur.

```bash
cd "C:/Users/tobid/Downloads/PROJECT TRADING/smc_ai_project" && python -m smc_ai.main
```

Attendu : génère un fichier JSON dans `results/`.

---

## Récapitulatif des fichiers créés / modifiés

| Fichier | Action |
|---|---|
| `smc_ai/core/idm.py` | Créé — IDM detection |
| `smc_ai/core/entry_decision.py` | Modifié — paramètre `idm_confirmed` |
| `smc_ai/core/entry_pipeline.py` | Modifié — propagation `idm_confirmed` |
| `smc_ai/core/pipeline.py` | Créé — orchestrateur multi-TF |
| `smc_ai/core/signals.py` | Modifié — ajout `generate_signals_from_multitf` |
| `smc_ai/data/providers/__init__.py` | Créé (vide) |
| `smc_ai/data/providers/csv_provider.py` | Créé — factory CSV + `default_fetcher` |
| `smc_ai/backtest/simulator.py` | Créé — simulation TP/SL en R-units |
| `tests/core/test_idm.py` | Créé |
| `tests/core/test_pipeline.py` | Créé |
| `tests/data/test_csv_provider.py` | Créé |
| `tests/backtest/test_simulator.py` | Créé |
