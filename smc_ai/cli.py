import argparse
import json
from pathlib import Path


def cmd_analyze(args: argparse.Namespace) -> None:
    from smc_ai.core.pipeline import run_multitf_analysis
    from smc_ai.data.fetcher import DataRequest
    from smc_ai.data.providers.csv_provider import default_fetcher

    fetcher = default_fetcher(args.data_dir)
    df_d1 = fetcher.get(DataRequest(symbol=args.symbol, timeframe="D1", bars=200))
    df_h4 = fetcher.get(DataRequest(symbol=args.symbol, timeframe="H4", bars=500))
    df_m15 = fetcher.get(DataRequest(symbol=args.symbol, timeframe="M15", bars=1000))

    result = run_multitf_analysis(
        symbol=args.symbol,
        df_d1=df_d1,
        df_h4=df_h4,
        df_m15=df_m15,
    )
    print(json.dumps(result.to_dict(), indent=2, default=str))


def cmd_backtest(args: argparse.Namespace) -> None:
    from smc_ai.backtest.walkforward import run_walkforward_backtest
    from smc_ai.data.fetcher import DataRequest
    from smc_ai.data.providers.csv_provider import default_fetcher

    fetcher = default_fetcher(args.data_dir)
    # Load all available bars from CSV (0 = no limit)
    df_d1 = fetcher.get(DataRequest(symbol=args.symbol, timeframe="D1", bars=0))
    df_h4 = fetcher.get(DataRequest(symbol=args.symbol, timeframe="H4", bars=0))
    df_m15 = fetcher.get(DataRequest(symbol=args.symbol, timeframe="M15", bars=0))

    result = run_walkforward_backtest(
        symbol=args.symbol,
        df_d1=df_d1,
        df_h4=df_h4,
        df_m15=df_m15,
        min_rr=args.min_rr,
        scan_step=args.scan_step,
        sim_horizon=args.sim_horizon,
    )
    print(json.dumps(result.to_dict(), indent=2, default=str))


def cmd_live(args: argparse.Namespace) -> None:
    from smc_ai.bridge.live_loop import run_live

    run_live(
        symbol=args.symbol,
        risk_pct=args.risk_pct,
        min_rr=args.min_rr,
        auto_trade=args.auto_trade,
        login=args.login,
        password=args.password,
        server=args.server,
    )


def main() -> None:
    parser = argparse.ArgumentParser(prog="smc_ai.cli", description="SMC AI trading CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_analyze = sub.add_parser("analyze", help="Run multi-TF analysis for a symbol")
    p_analyze.add_argument("--symbol", default="EURUSD", help="Trading symbol (e.g. EURUSD)")
    p_analyze.add_argument("--data-dir", type=Path, default=None, dest="data_dir",
                           help="Directory containing {symbol}_{timeframe}.csv files")
    p_analyze.set_defaults(func=cmd_analyze)

    p_backtest = sub.add_parser("backtest", help="Walk-forward backtest on CSV data")
    p_backtest.add_argument("--symbol", default="EURUSD")
    p_backtest.add_argument("--data-dir", type=Path, default=None, dest="data_dir")
    p_backtest.add_argument("--min-rr", type=float, default=5.0, dest="min_rr")
    p_backtest.add_argument("--scan-step", type=int, default=40, dest="scan_step")
    p_backtest.add_argument("--sim-horizon", type=int, default=1000, dest="sim_horizon",
                            help="M15 bars to simulate after entry (default 1000 = ~10 days)")
    p_backtest.set_defaults(func=cmd_backtest)

    p_live = sub.add_parser("live", help="Live MT5 bridge — analysis loop every 15min")
    p_live.add_argument("--symbol",     default="EURUSD", help="e.g. EURUSD, XAUUSD")
    p_live.add_argument("--risk-pct",   type=float, default=0.01, dest="risk_pct",
                        help="Account risk per trade (default 0.01 = 1%%)")
    p_live.add_argument("--min-rr",     type=float, default=5.0,  dest="min_rr")
    p_live.add_argument("--auto-trade", action="store_true", dest="auto_trade",
                        help="Send orders automatically (no confirmation prompt)")
    p_live.add_argument("--login",    type=int,   default=None, help="MT5 account number")
    p_live.add_argument("--password", type=str,   default=None, help="MT5 password")
    p_live.add_argument("--server",   type=str,   default=None, help="MT5 broker server name")
    p_live.set_defaults(func=cmd_live)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
