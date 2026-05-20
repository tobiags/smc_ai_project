from collections.abc import Callable
from dataclasses import dataclass

import pandas as pd

from smc_ai.data.models import validate_ohlcv


@dataclass(frozen=True)
class DataRequest:
    symbol: str
    timeframe: str
    bars: int


DataProvider = Callable[[DataRequest], pd.DataFrame]


class DataFetcher:
    """Provider registry. The first provider returning valid OHLCV data wins."""

    def __init__(self) -> None:
        self._providers: list[tuple[str, DataProvider]] = []

    def register(self, name: str, provider: DataProvider) -> None:
        self._providers.append((name, provider))

    def get(self, request: DataRequest) -> pd.DataFrame:
        errors: list[str] = []
        for name, provider in self._providers:
            try:
                return validate_ohlcv(provider(request))
            except Exception as exc:
                errors.append(f"{name}: {exc}")

        raise RuntimeError(f"No data provider succeeded for {request}. Errors: {errors}")
