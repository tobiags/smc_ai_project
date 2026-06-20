"""Twelve Data OHLCV provider — fetches historical forex data via REST API.

Supports D1, H4, M15 for all major forex pairs and XAUUSD.
Free plan: 800 calls/day, 8 calls/min, 5000 bars per call.
"""
from __future__ import annotations

import os
import time
from pathlib import Path

import pandas as pd
import requests

_API_BASE = "https://api.twelvedata.com/time_series"

_INTERVAL_MAP = {
    "M1":  "1min",
    "M5":  "5min",
    "M15": "15min",
    "M30": "30min",
    "H1":  "1h",
    "H4":  "4h",
    "D1":  "1day",
    "W1":  "1week",
}

# Bars needed per timeframe for meaningful backtesting
_DEFAULT_BARS = {
    "D1":  5000,   # ~20 years
    "H4":  5000,   # ~2.5 years
    "M15": 5000,   # ~2.5 months per chunk
}

# Twelve Data rate limit: 8 requests/minute on free plan
_REQUEST_DELAY = 8.0  # seconds between requests


def symbol_to_td(symbol: str) -> str:
    """Convert broker symbol to Twelve Data format.

    Examples:
        EURUSD   → EUR/USD
        EURUSD.s → EUR/USD
        XAUUSD   → XAU/USD
        USDJPY.s → USD/JPY
    """
    s = symbol.upper()
    for suffix in (".S", ".M", ".PRO", ".ECN", ".STP"):
        s = s.replace(suffix, "")
    if len(s) == 6 and s.isalpha():
        return f"{s[:3]}/{s[3:]}"
    return s


def fetch_ohlcv(
    symbol: str,
    timeframe: str,
    bars: int = 5000,
    api_key: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> pd.DataFrame:
    """Fetch OHLCV data from Twelve Data.

    Args:
        symbol:     Broker symbol (e.g. "EURUSD.s" or "EURUSD")
        timeframe:  One of M1, M5, M15, M30, H1, H4, D1, W1
        bars:       Number of bars (max 5000 per call on free plan)
        api_key:    API key — falls back to TWELVEDATA_API_KEY env var
        start_date: Optional ISO date string "YYYY-MM-DD" for range query
        end_date:   Optional ISO date string "YYYY-MM-DD" for range query

    Returns:
        DataFrame with DatetimeIndex (UTC) and columns: open, high, low, close, volume
    """
    key = api_key or os.environ.get("TWELVEDATA_API_KEY")
    if not key:
        raise ValueError(
            "No Twelve Data API key. Set TWELVEDATA_API_KEY env var or pass api_key=..."
        )

    interval = _INTERVAL_MAP.get(timeframe)
    if not interval:
        raise ValueError(f"Unknown timeframe '{timeframe}'. Choose from: {list(_INTERVAL_MAP)}")

    td_symbol = symbol_to_td(symbol)

    params: dict[str, str | int] = {
        "symbol":     td_symbol,
        "interval":   interval,
        "outputsize": min(bars, 5000),
        "timezone":   "UTC",
        "order":      "ASC",
        "apikey":     key,
    }
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date

    resp = requests.get(_API_BASE, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if data.get("status") == "error":
        raise RuntimeError(f"Twelve Data error: {data.get('message', data)}")

    values = data.get("values")
    if not values:
        raise RuntimeError(f"No data returned for {td_symbol} {interval}")

    df = pd.DataFrame(values)
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
    df = df.set_index("datetime").rename_axis("time")
    cols = ["open", "high", "low", "close"]
    if "volume" in df.columns:
        cols.append("volume")
    df = df[cols].astype(float)
    if "volume" not in df.columns:
        df["volume"] = 0.0  # forex has no volume

    # Fix occasional bad candles from the API (high < open/close or low > open/close)
    oc_max = df[["open", "close"]].max(axis=1)
    oc_min = df[["open", "close"]].min(axis=1)
    df["high"] = df["high"].combine(oc_max, max)
    df["low"]  = df["low"].combine(oc_min, min)

    return df[["open", "high", "low", "close", "volume"]]


def fetch_bulk(
    symbol: str,
    out_dir: Path,
    api_key: str | None = None,
    timeframes: list[str] | None = None,
    bars_per_tf: dict[str, int] | None = None,
) -> dict[str, Path]:
    """Fetch D1, H4, M15 data and save to CSV files.

    Returns a dict of {timeframe: csv_path}.
    """
    tfs = timeframes or ["D1", "H4", "M15"]
    bars = bars_per_tf or _DEFAULT_BARS
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    results: dict[str, Path] = {}
    td_symbol = symbol_to_td(symbol)

    for i, tf in enumerate(tfs):
        if i > 0:
            time.sleep(_REQUEST_DELAY)

        n = bars.get(tf, 5000)
        print(f"  Fetching {td_symbol} {tf} ({n} bars)…", end=" ", flush=True)

        try:
            df = fetch_ohlcv(symbol, tf, bars=n, api_key=api_key)
            # Save using broker symbol name for compatibility with backtester
            fname = f"{symbol}_{tf}.csv"
            path = out_dir / fname
            df.to_csv(path)
            results[tf] = path
            print(f"OK  {len(df)} rows -> {path}")
        except Exception as exc:
            print(f"ERR  {exc}")

    return results
