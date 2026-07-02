"""Fetch historical OHLCV data from Twelve Data and save as CSV.

Reads TWELVEDATA_API_KEY from .env or environment.

Usage:
    python scripts/fetch_twelvedata.py --symbol EURUSD
    python scripts/fetch_twelvedata.py --symbol XAUUSD --out-dir data
    python scripts/fetch_twelvedata.py --symbol EURUSD --symbol GBPUSD --symbol XAUUSD

Then run the backtest:
    python -m smc_ai.cli backtest --symbol EURUSD --data-dir data
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running as plain script without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from smc_ai.utils import load_dotenv


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Fetch Twelve Data OHLCV → CSV")
    parser.add_argument("--symbol",  action="append", default=[], dest="symbols",
                        metavar="SYM", help="Symbol(s) to fetch (repeat for multiple)")
    parser.add_argument("--out-dir", default="data", dest="out_dir",
                        help="Output directory (default: data/)")
    parser.add_argument("--api-key", default=None, dest="api_key",
                        help="Twelve Data API key (overrides .env)")
    parser.add_argument("--bars-m15", type=int, default=25000, dest="bars_m15",
                        help="Number of M15 bars (>5000 = paginated, default 25000 ~ 2 years)")
    parser.add_argument("--bars-h4",  type=int, default=5000, dest="bars_h4",
                        help="Number of H4 bars (default 5000 ~ 2.5 years)")
    parser.add_argument("--bars-d1",  type=int, default=5000, dest="bars_d1",
                        help="Number of D1 bars (default 5000 ~ 20 years)")
    args = parser.parse_args()

    symbols = args.symbols or ["EURUSD"]
    api_key = args.api_key or os.environ.get("TWELVEDATA_API_KEY")
    if not api_key:
        print("❌  No API key. Add TWELVEDATA_API_KEY=... to .env or use --api-key.")
        sys.exit(1)

    from smc_ai.data.providers.twelvedata_provider import fetch_bulk

    out_dir = Path(args.out_dir)
    bars = {"D1": args.bars_d1, "H4": args.bars_h4, "M15": args.bars_m15}

    sep = "=" * 52
    print(f"\n{sep}")
    print(f"  Twelve Data Fetcher -- {len(symbols)} symbol(s)")
    print(f"  Output : {out_dir.resolve()}")
    print(f"  Bars   : D1={bars['D1']} | H4={bars['H4']} | M15={bars['M15']}")
    print(f"{sep}\n")

    for sym in symbols:
        print(f"-- {sym} {'-'*44}")
        results = fetch_bulk(
            symbol=sym,
            out_dir=out_dir,
            api_key=api_key,
            bars_per_tf=bars,
        )
        print()

    print("Done! Run backtest with:")
    for sym in symbols:
        print(f'  python -m smc_ai.cli backtest --symbol "{sym}" --data-dir "{out_dir}"')
    print()
    print("Or generate the visual report:")
    for sym in symbols:
        print(f'  python scripts/generate_report.py --symbol "{sym}" --data-dir "{out_dir}"')


if __name__ == "__main__":
    main()
