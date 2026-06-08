"""Live analysis loop — fires on every new M15 candle.

Usage (semi-auto, with user confirmation):
    python -m smc_ai.cli live --symbol EURUSD

Usage (fully automatic — use with caution on a demo account first):
    python -m smc_ai.cli live --symbol EURUSD --auto-trade

Loop cadence:
    • Checks every 10 seconds whether a new 15-minute candle has opened.
    • On each new candle: fetches D1/H4/M15 data, runs run_multitf_analysis,
      prints the result, and (optionally) sends an order via MT5.
"""
from __future__ import annotations

import time
from datetime import UTC, datetime

from smc_ai.bridge.mt5_connector import (
    account_balance,
    connect,
    disconnect,
    fetch_ohlcv,
)
from smc_ai.bridge.order_manager import (
    build_order,
    compute_volume,
    get_open_positions,
    send_order,
)
from smc_ai.bridge.signal_writer import clear_signal, write_signal
from smc_ai.core.pipeline import MultiTFAnalysis, run_multitf_analysis
from smc_ai.core.risk import TradeLevels

_POLL_SECONDS = 10          # how often to check for a new candle
_CANDLE_MINUTES = 15        # M15 candle period


def run_live(
    symbol: str = "EURUSD",
    risk_pct: float = 0.01,
    min_rr: float = 5.0,
    auto_trade: bool = False,
    login: int | None = None,
    password: str | None = None,
    server: str | None = None,
) -> None:
    """Start the live analysis loop.

    Args:
        symbol:     Forex symbol (e.g. "EURUSD", "XAUUSD").
        risk_pct:   Account risk per trade as a fraction (0.01 = 1 %).
        min_rr:     Minimum reward-to-risk ratio accepted.
        auto_trade: If True, orders are sent without user confirmation.
                    **Always test on a demo account first.**
        login / password / server: Optional MT5 credentials; omit to use the
                    account currently open in the terminal.
    """
    _banner(symbol, risk_pct, min_rr, auto_trade)

    connect(login=login, password=password, server=server)
    print("✓ Connected to MT5 terminal.\n")

    last_candle: datetime | None = None

    try:
        while True:
            now = datetime.now(UTC)
            candle_open = _candle_open_time(now)

            if candle_open != last_candle:
                last_candle = candle_open
                _analysis_cycle(symbol, risk_pct, min_rr, auto_trade)

            time.sleep(_POLL_SECONDS)

    except KeyboardInterrupt:
        print("\n[Ctrl-C] Loop stopped by user.")
    finally:
        disconnect()
        print("MT5 disconnected.")


# ── private ───────────────────────────────────────────────────────────────────

def _candle_open_time(now: datetime) -> datetime:
    """Return the UTC open time of the current M15 candle."""
    candle_minute = (now.minute // _CANDLE_MINUTES) * _CANDLE_MINUTES
    return now.replace(minute=candle_minute, second=0, microsecond=0)


def _analysis_cycle(
    symbol: str,
    risk_pct: float,
    min_rr: float,
    auto_trade: bool,
) -> None:
    ts = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    print(f"{'─'*52}")
    print(f"[{ts}]  Analysing {symbol}…")

    # ── guard: don't open a new trade if one is already open ──────────────
    open_pos = get_open_positions(symbol)
    if open_pos:
        print(f"  ⚠ {len(open_pos)} position(s) already open — skipping entry scan.")
        _print_positions(open_pos)
        return

    # ── fetch data ────────────────────────────────────────────────────────
    try:
        df_d1  = fetch_ohlcv(symbol, "D1",  bars=200)
        df_h4  = fetch_ohlcv(symbol, "H4",  bars=500)
        df_m15 = fetch_ohlcv(symbol, "M15", bars=1000)
    except Exception as exc:
        print(f"  ✗ Data fetch error: {exc}")
        return

    # ── run pipeline ──────────────────────────────────────────────────────
    try:
        analysis = run_multitf_analysis(
            symbol=symbol,
            df_d1=df_d1,
            df_h4=df_h4,
            df_m15=df_m15,
            min_rr=min_rr,
        )
    except Exception as exc:
        print(f"  ✗ Analysis error: {exc}")
        return

    _print_analysis(analysis)

    if analysis.active_schema is None:
        # Write "waiting" state to MT5 panel
        write_signal(
            symbol=symbol,
            d1_bias=analysis.d1_bias or "unknown",
            idm_confirmed=analysis.idm_confirmed,
            active_schema=None,
        )
        print("  → No setup. Waiting for next candle…")
        return

    # ── resolve entry levels ──────────────────────────────────────────────
    try:
        direction, levels, schema = _resolve_entry(analysis, min_rr)
    except ValueError as exc:
        write_signal(
            symbol=symbol,
            d1_bias=analysis.d1_bias or "unknown",
            idm_confirmed=analysis.idm_confirmed,
            active_schema=analysis.active_schema,
        )
        print(f"  ✗ Cannot resolve entry: {exc}")
        return

    # ── write signal to MT5 panel ─────────────────────────────────────────
    write_signal(
        symbol=symbol,
        d1_bias=analysis.d1_bias or "unknown",
        idm_confirmed=analysis.idm_confirmed,
        active_schema=analysis.active_schema,
        direction=direction,
        entry=levels.entry,
        stop_loss=levels.stop_loss,
        take_profit=levels.take_profit,
        schema=schema,
    )

    _print_signal(direction, levels, schema)

    # ── execute or ask ────────────────────────────────────────────────────
    if auto_trade:
        _execute(symbol, direction, levels, schema, risk_pct)
    else:
        _prompt_and_execute(symbol, direction, levels, schema, risk_pct)


def _resolve_entry(
    analysis: MultiTFAnalysis,
    min_rr: float,
) -> tuple[str, TradeLevels, str]:
    """Extract (direction, TradeLevels, schema_name) from the analysis."""
    schema = analysis.active_schema

    if schema == "a1":
        entry_analysis = analysis.m15_entry
        if not entry_analysis.decision.accepted or entry_analysis.levels is None:
            raise ValueError("a1 schema has no accepted entry")
        return (
            entry_analysis.decision.direction,  # type: ignore[return-value]
            entry_analysis.levels,
            "a1",
        )

    if schema == "b4" and analysis.b4_entry is not None:
        b4 = analysis.b4_entry
        direction: str = b4["direction"]
        entry: float = float(b4["entry"])
        stop: float = float(b4["stop"])
        risk = abs(entry - stop)
        tp = entry + risk * min_rr if direction == "buy" else entry - risk * min_rr
        return direction, TradeLevels(
            entry=round(entry, 5),
            stop_loss=round(stop, 5),
            take_profit=round(tp, 5),
            rr=min_rr,
        ), "b4"

    if schema == "b2" and analysis.b2_entry is not None:
        b2 = analysis.b2_entry
        direction = b2["direction"]
        # Entry = midpoint of IFC candle zone
        entry = round((float(b2["entry_zone_top"]) + float(b2["entry_zone_bottom"])) / 2, 5)
        stop = float(b2["entry_zone_top"]) if direction == "sell" else float(b2["entry_zone_bottom"])
        risk = abs(entry - stop)
        tp = entry - risk * min_rr if direction == "sell" else entry + risk * min_rr
        return direction, TradeLevels(
            entry=round(entry, 5),
            stop_loss=round(stop, 5),
            take_profit=round(tp, 5),
            rr=min_rr,
        ), "b2"

    raise ValueError(f"Cannot resolve entry for schema '{schema}'")


def _execute(
    symbol: str,
    direction: str,
    levels: TradeLevels,
    schema: str,
    risk_pct: float,
) -> None:
    try:
        balance = account_balance()
    except Exception:
        balance = 10_000.0

    volume = compute_volume(balance, risk_pct, levels.entry, levels.stop_loss)

    try:
        request = build_order(
            symbol=symbol,
            direction=direction,
            volume=volume,
            stop_loss=levels.stop_loss,
            take_profit=levels.take_profit,
            schema=schema,
        )
        result = send_order(request)
        if result.success:
            print(f"  ✓ Order executed  #{result.order_id}  {volume} lots  {direction.upper()}")
        else:
            print(f"  ✗ Order rejected: {result}")
    except Exception as exc:
        print(f"  ✗ Order error: {exc}")


def _prompt_and_execute(
    symbol: str,
    direction: str,
    levels: TradeLevels,
    schema: str,
    risk_pct: float,
) -> None:
    try:
        answer = input("  Execute trade? [y]es / [n]o : ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        answer = "n"

    if answer == "y":
        _execute(symbol, direction, levels, schema, risk_pct)
    else:
        print("  → Trade skipped.")


# ── display helpers ───────────────────────────────────────────────────────────

def _banner(symbol: str, risk_pct: float, min_rr: float, auto_trade: bool) -> None:
    mode = "AUTO" if auto_trade else "SEMI-AUTO (confirmation required)"
    print("\n" + "═" * 52)
    print("  SMC AI — MT5 Live Bridge")
    print("═" * 52)
    print(f"  Symbol  : {symbol}")
    print(f"  Risk    : {risk_pct * 100:.1f} % per trade")
    print(f"  Min RR  : 1:{min_rr}")
    print(f"  Mode    : {mode}")
    print("═" * 52)


def _print_analysis(a: MultiTFAnalysis) -> None:
    idm_icon = "✓" if a.idm_confirmed else "✗"
    print(f"  D1 Bias      : {a.d1_bias}")
    print(f"  IDM          : {idm_icon} {'confirmed' if a.idm_confirmed else 'not confirmed'}")
    print(f"  Active Schema: {a.active_schema or 'none'}")
    if a.m15_ifc:
        print(f"  IFC          : body_ratio={a.m15_ifc['body_ratio']:.3f}")


def _print_signal(direction: str, levels: TradeLevels, schema: str) -> None:
    arrow = "▲ BUY" if direction == "buy" else "▼ SELL"
    print(f"\n  ╔══ SIGNAL — {arrow} ({'schema ' + schema.upper()}) ══╗")
    print(f"  ║  Entry      : {levels.entry}")
    print(f"  ║  Stop Loss  : {levels.stop_loss}")
    print(f"  ║  Take Profit: {levels.take_profit}")
    print(f"  ║  RR         : 1:{levels.rr}")
    print(f"  ╚{'═' * 38}╝")


def _print_positions(positions: list[dict]) -> None:
    for p in positions:
        side = "▲" if p["direction"] == "buy" else "▼"
        pnl = f"{p['profit']:+.2f}"
        print(f"    {side} {p['symbol']}  {p['volume']} lots  PnL: {pnl}")
