"""Export OHLCV data from MT5 terminal to CSV files for backtesting.

Usage:
    python scripts/export_mt5_data.py --symbol EURUSD.s --login 2000529599 --server JustMarkets-Demo

The script saves:
    data/EURUSD.s_D1.csv
    data/EURUSD.s_H4.csv
    data/EURUSD.s_M15.csv

These CSV files are then used by the walkforward backtester.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


# ── MT5 import ────────────────────────────────────────────────────────────────
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False


# ── Timeframe map ─────────────────────────────────────────────────────────────
_TF_MAP = {
    "M1":  lambda: mt5.TIMEFRAME_M1,
    "M5":  lambda: mt5.TIMEFRAME_M5,
    "M15": lambda: mt5.TIMEFRAME_M15,
    "M30": lambda: mt5.TIMEFRAME_M30,
    "H1":  lambda: mt5.TIMEFRAME_H1,
    "H4":  lambda: mt5.TIMEFRAME_H4,
    "D1":  lambda: mt5.TIMEFRAME_D1,
    "W1":  lambda: mt5.TIMEFRAME_W1,
}

_BARS = {
    "D1":  500,
    "H4":  1000,
    "M15": 2000,
}


def connect(login: int | None, password: str | None, server: str | None) -> None:
    if not MT5_AVAILABLE:
        print("❌  MetaTrader5 package not installed. Run: pip install MetaTrader5")
        sys.exit(1)

    kwargs: dict = {}
    if login:
        kwargs["login"] = login
    if password:
        kwargs["password"] = password
    if server:
        kwargs["server"] = server

    ok = mt5.initialize(**kwargs) if kwargs else mt5.initialize()
    if not ok:
        code, msg = mt5.last_error()
        print(f"❌  MT5 initialize failed ({code}): {msg}")
        print("    → Make sure MetaTrader 5 is open and you are logged in.")
        sys.exit(1)

    info = mt5.account_info()
    if info:
        print(f"✓ Connected — Account #{info.login}  Balance: {info.balance} {info.currency}")
    else:
        print("✓ Connected to MT5 terminal.")


def fetch_ohlcv(symbol: str, timeframe: str, bars: int) -> pd.DataFrame:
    tf_code = _TF_MAP[timeframe]()
    rates = mt5.copy_rates_from_pos(symbol, tf_code, 0, bars)
    if rates is None or len(rates) == 0:
        raise RuntimeError(
            f"No data for {symbol} {timeframe}. "
            f"Make sure the symbol is visible in MT5 (right-click → Show Symbol)."
        )
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df = df.set_index("time").rename(columns={"tick_volume": "volume"})
    df = df[["open", "high", "low", "close", "volume"]]
    return df


def export(symbol: str, out_dir: Path, login: int | None, password: str | None, server: str | None) -> None:
    connect(login, password, server)
    out_dir.mkdir(parents=True, exist_ok=True)

    for tf, bars in _BARS.items():
        print(f"  Fetching {symbol} {tf} ({bars} bars)…", end=" ", flush=True)
        try:
            df = fetch_ohlcv(symbol, tf, bars)
            path = out_dir / f"{symbol}_{tf}.csv"
            df.to_csv(path)
            print(f"✓  {len(df)} rows → {path}")
        except Exception as exc:
            print(f"✗  {exc}")

    mt5.shutdown()
    print("\nDone. Run the backtest with:")
    print(f'  python -m smc_ai.cli backtest --symbol "{symbol}" --data-dir "{out_dir}"')


def main() -> None:
    parser = argparse.ArgumentParser(description="Export MT5 OHLCV data to CSV for backtesting")
    parser.add_argument("--symbol",   default="EURUSD.s",       help="MT5 symbol (e.g. EURUSD.s)")
    parser.add_argument("--out-dir",  default="data",            help="Output directory for CSV files")
    parser.add_argument("--login",    type=int,   default=None,  help="MT5 account number")
    parser.add_argument("--password", type=str,   default=None,  help="MT5 password")
    parser.add_argument("--server",   type=str,   default=None,  help="MT5 broker server")
    args = parser.parse_args()

    export(
        symbol=args.symbol,
        out_dir=Path(args.out_dir),
        login=args.login,
        password=args.password,
        server=args.server,
    )


if __name__ == "__main__":
    main()
