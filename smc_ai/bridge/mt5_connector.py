"""MT5 Connector — connection management and OHLCV data fetching.

MetaTrader5 is a Windows-only package and requires the MT5 terminal to be
running. The module degrades gracefully when the package is not installed so
that the rest of the codebase (and tests) can import without errors.

Usage:
    from smc_ai.bridge.mt5_connector import connect, disconnect, fetch_ohlcv

    connect()                                      # uses terminal credentials
    connect(login=12345, password="xxx", server="ICMarkets-Demo")
    df_m15 = fetch_ohlcv("EURUSD", "M15", bars=1000)
    disconnect()
"""
from __future__ import annotations

import pandas as pd

# Optional import — graceful degradation when not on Windows / not installed
try:
    import MetaTrader5 as _mt5  # type: ignore[import-untyped]
    MT5_AVAILABLE = True
except ImportError:
    _mt5 = None  # type: ignore[assignment]
    MT5_AVAILABLE = False

# Map human-readable strings → MT5 timeframe constants (resolved lazily)
_TF_NAMES = ("M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1")


def connect(
    login: int | None = None,
    password: str | None = None,
    server: str | None = None,
) -> None:
    """Open connection to the running MT5 terminal.

    If login/password/server are omitted, MT5 uses the credentials of the
    account currently open in the terminal.
    """
    _require_mt5()
    kwargs: dict[str, object] = {}
    if login is not None:
        kwargs["login"] = login
    if password is not None:
        kwargs["password"] = password
    if server is not None:
        kwargs["server"] = server

    if not _mt5.initialize(**kwargs):
        code, msg = _mt5.last_error()
        raise RuntimeError(f"MT5 initialize failed — code={code}: {msg}")


def disconnect() -> None:
    """Close the MT5 connection."""
    if MT5_AVAILABLE and _mt5 is not None:
        _mt5.shutdown()


def fetch_ohlcv(symbol: str, timeframe: str, bars: int = 1000) -> pd.DataFrame:
    """Fetch the last `bars` closed candles for *symbol* at *timeframe*.

    Args:
        symbol:    e.g. "EURUSD", "XAUUSD"
        timeframe: "M1"|"M5"|"M15"|"M30"|"H1"|"H4"|"D1"|"W1"
        bars:      number of candles to fetch (most recent first)

    Returns a DataFrame with UTC DatetimeIndex and columns:
        open, high, low, close, volume
    """
    _require_mt5()
    tf_code = _tf_code(timeframe)
    rates = _mt5.copy_rates_from_pos(symbol, tf_code, 0, bars)

    if rates is None or len(rates) == 0:
        code, msg = _mt5.last_error()
        raise RuntimeError(
            f"No data returned for {symbol} {timeframe} — code={code}: {msg}"
        )

    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df = df.set_index("time")
    df = df.rename(columns={"tick_volume": "volume"})
    return df[["open", "high", "low", "close", "volume"]].copy()


def account_balance() -> float:
    """Return the current account balance in account currency."""
    _require_mt5()
    info = _mt5.account_info()
    if info is None:
        raise RuntimeError("Cannot read account info from MT5")
    return float(info.balance)


def current_tick(symbol: str) -> tuple[float, float]:
    """Return (bid, ask) for *symbol*."""
    _require_mt5()
    tick = _mt5.symbol_info_tick(symbol)
    if tick is None:
        raise RuntimeError(f"Cannot get tick for {symbol}")
    return float(tick.bid), float(tick.ask)


# ── internal helpers ──────────────────────────────────────────────────────────

def _require_mt5() -> None:
    if not MT5_AVAILABLE:
        raise RuntimeError(
            "MetaTrader5 package is not installed.\n"
            "Run:  pip install MetaTrader5\n"
            "(Windows only — requires MT5 terminal to be running)"
        )


def _tf_code(timeframe: str) -> int:
    """Convert a timeframe string to the MT5 integer constant."""
    mapping = {
        "M1":  _mt5.TIMEFRAME_M1,
        "M5":  _mt5.TIMEFRAME_M5,
        "M15": _mt5.TIMEFRAME_M15,
        "M30": _mt5.TIMEFRAME_M30,
        "H1":  _mt5.TIMEFRAME_H1,
        "H4":  _mt5.TIMEFRAME_H4,
        "D1":  _mt5.TIMEFRAME_D1,
        "W1":  _mt5.TIMEFRAME_W1,
    }
    if timeframe not in mapping:
        raise ValueError(f"Unknown timeframe '{timeframe}'. Valid: {_TF_NAMES}")
    return mapping[timeframe]
