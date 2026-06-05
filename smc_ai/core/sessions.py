import pandas as pd


def classify_session(timestamp: pd.Timestamp) -> str:
    utc = timestamp.tz_convert("UTC") if timestamp.tzinfo is not None else timestamp
    hour = utc.hour
    if 1 <= hour < 7:
        return "asia"
    if 7 <= hour < 13:
        return "london"
    if 13 <= hour < 21:
        return "ny"
    return "off"


def is_trade_allowed(timestamp: pd.Timestamp) -> bool:
    return classify_session(timestamp) in {"london", "ny"}
