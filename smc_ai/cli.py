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
    df_d1 = fetcher.get(DataRequest(symbol=args.symbol, timeframe="D1", bars=200))
    df_h4 = fetcher.get(DataRequest(symbol=args.symbol, timeframe="H4", bars=500))
    df_m15 = fetcher.get(DataRequest(symbol=args.symbol, timeframe="M15", bars=1000))

    result = run_walkforward_backtest(
        symbol=args.symbol,
        df_d1=df_d1,
        df_h4=df_h4,
        df_m15=df_m15,
        min_rr=args.min_rr,
        scan_step=args.scan_step,
    )
    print(json.dumps(result.to_dict(), indent=2, default=str))


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
    p_backtest.set_defaults(func=cmd_backtest)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
