import json
from pathlib import Path

import pandas as pd
import pytest


def _write_ohlcv_csv(path: Path, symbol: str, timeframe: str, n: int = 60) -> None:
    index = pd.date_range("2026-01-01", periods=n, freq="D")
    base = [1.10 + i * 0.001 for i in range(n)]
    df = pd.DataFrame(
        {
            "open": [c - 0.0005 for c in base],
            "high": [c + 0.001 for c in base],
            "low": [c - 0.001 for c in base],
            "close": base,
            "volume": [1000] * n,
        },
        index=index,
    )
    df.index.name = "time"
    (path / f"{symbol}_{timeframe}.csv").write_text(df.to_csv())


def test_cmd_analyze_outputs_valid_json(tmp_path, capsys):
    _write_ohlcv_csv(tmp_path, "EURUSD", "D1", n=60)
    _write_ohlcv_csv(tmp_path, "EURUSD", "H4", n=100)
    _write_ohlcv_csv(tmp_path, "EURUSD", "M15", n=200)

    import argparse
    from smc_ai.cli import cmd_analyze

    args = argparse.Namespace(symbol="EURUSD", data_dir=tmp_path)
    cmd_analyze(args)

    captured = capsys.readouterr()
    data = json.loads(captured.out)

    assert data["symbol"] == "EURUSD"
    assert data["d1_bias"] in {"bullish", "bearish", "neutral"}
    assert isinstance(data["h4_zones"], list)
    assert isinstance(data["idm_confirmed"], bool)
    assert "m15_entry" in data


def test_cmd_analyze_raises_for_missing_csv(tmp_path):
    import argparse
    from smc_ai.cli import cmd_analyze

    args = argparse.Namespace(symbol="MISSING", data_dir=tmp_path)
    # DataFetcher wraps provider errors in RuntimeError when all providers fail
    with pytest.raises((FileNotFoundError, RuntimeError)):
        cmd_analyze(args)
