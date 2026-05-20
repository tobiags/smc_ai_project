import pandas as pd

from smc_ai.core.sessions import classify_session, is_trade_allowed


def test_classify_session_utc_hours():
    assert classify_session(pd.Timestamp("2026-01-01 03:00:00")) == "asia"
    assert classify_session(pd.Timestamp("2026-01-01 08:00:00")) == "london"
    assert classify_session(pd.Timestamp("2026-01-01 14:00:00")) == "ny"
    assert classify_session(pd.Timestamp("2026-01-01 22:00:00")) == "off"


def test_classify_session_boundaries():
    assert classify_session(pd.Timestamp("2026-01-01 01:00:00")) == "asia"
    assert classify_session(pd.Timestamp("2026-01-01 07:00:00")) == "london"
    assert classify_session(pd.Timestamp("2026-01-01 13:00:00")) == "ny"
    assert classify_session(pd.Timestamp("2026-01-01 21:00:00")) == "off"


def test_trade_allowed_only_london_and_ny():
    assert is_trade_allowed(pd.Timestamp("2026-01-01 03:00:00")) is False
    assert is_trade_allowed(pd.Timestamp("2026-01-01 08:00:00")) is True
    assert is_trade_allowed(pd.Timestamp("2026-01-01 14:00:00")) is True
    assert is_trade_allowed(pd.Timestamp("2026-01-01 22:00:00")) is False
