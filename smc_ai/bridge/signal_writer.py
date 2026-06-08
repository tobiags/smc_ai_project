"""Write SMC AI signals to a file that the MT5 EA can read.

The file format is simple key=value so MQL5 can parse it without
a JSON library.
"""
from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

try:
    import MetaTrader5 as _mt5
    _MT5_AVAILABLE = True
except ImportError:
    _mt5 = None  # type: ignore[assignment]
    _MT5_AVAILABLE = False


def _mt5_files_path() -> Path | None:
    """Return the MT5 terminal MQL5/Files/ folder, or None if unavailable."""
    if not _MT5_AVAILABLE or _mt5 is None:
        return None
    try:
        info = _mt5.terminal_info()
        if info is None:
            return None
        data_path = getattr(info, "data_path", None)
        if not data_path:
            return None
        p = Path(data_path) / "MQL5" / "Files"
        p.mkdir(parents=True, exist_ok=True)
        return p
    except Exception:
        return None


def write_signal(
    symbol: str,
    d1_bias: str,
    idm_confirmed: bool,
    active_schema: str | None,
    direction: str | None = None,
    entry: float | None = None,
    stop_loss: float | None = None,
    take_profit: float | None = None,
    schema: str | None = None,
    extra_path: Path | None = None,
) -> None:
    """Write the current analysis state to a signal file.

    The file is written to two locations:
      1. MT5's MQL5/Files/ folder (read by the EA)
      2. extra_path if provided (for debugging)
    """
    ts = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    has_signal = (
        direction is not None
        and entry is not None
        and stop_loss is not None
        and take_profit is not None
        and active_schema not in (None, "none", "")
    )

    lines = [
        f"SYMBOL={symbol}",
        f"D1_BIAS={d1_bias or 'unknown'}",
        f"IDM_CONFIRMED={'true' if idm_confirmed else 'false'}",
        f"ACTIVE_SCHEMA={active_schema or 'none'}",
        f"DIRECTION={direction or 'none'}",
        f"ENTRY={entry or 0:.5f}",
        f"SL={stop_loss or 0:.5f}",
        f"TP={take_profit or 0:.5f}",
        f"SCHEMA={schema or 'none'}",
        f"STATUS={'SIGNAL' if has_signal else 'WAITING'}",
        f"TIMESTAMP={ts}",
    ]
    content = "\n".join(lines) + "\n"

    # ── Write to MT5 files folder ────────────────────────────────────────────
    mt5_dir = _mt5_files_path()
    if mt5_dir:
        target = mt5_dir / "smc_ai_signal.txt"
        try:
            target.write_text(content, encoding="utf-8")
        except OSError:
            pass

    # ── Write to extra_path (optional) ──────────────────────────────────────
    if extra_path:
        try:
            extra_path.parent.mkdir(parents=True, exist_ok=True)
            extra_path.write_text(content, encoding="utf-8")
        except OSError:
            pass


def clear_signal(symbol: str) -> None:
    """Clear the signal file (called on disconnect)."""
    write_signal(
        symbol=symbol,
        d1_bias="unknown",
        idm_confirmed=False,
        active_schema=None,
    )
