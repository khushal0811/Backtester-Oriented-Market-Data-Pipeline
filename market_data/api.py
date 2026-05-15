from typing import List, Generator, Optional

import pandas as pd

from .storage import (
    load_from_parquet,
    get_available_symbols,
    load_dividends_from_parquet,
    get_data_info,
)
from .events import (
    MarketEvent,
    DividendEvent,
    stream_events as events_stream_single,
    stream_multiple,
    stream_dividends,
    stream_multiple_with_dividends,
)


def get_symbols(data_dir: str = "data/") -> List[str]:
    """Return all symbols with available OHLCV data."""
    return get_available_symbols(data_dir)


def load_data(symbol: str, data_dir: str = "data/") -> pd.DataFrame:
    """Load normalized OHLCV dataframe for a symbol."""
    return load_from_parquet(symbol, data_dir)


def load_dividend_data(
    symbol: str, data_dir: str = "data/"
) -> Optional[pd.DataFrame]:
    """Load dividend history for a symbol. Returns None if no dividends."""
    return load_dividends_from_parquet(symbol, data_dir)


def get_symbol_info(symbol: str, data_dir: str = "data/") -> dict:
    """
    Return availability metadata for a symbol without loading full data.
    Used by the frontend to validate tickers before running a backtest.
    """
    return get_data_info(symbol, data_dir)


def stream_events(
    symbol: str, data_dir: str = "data/"
) -> Generator[MarketEvent, None, None]:
    """Stream MarketEvents for a single symbol."""
    return events_stream_single(symbol, data_dir)


def stream_multi_symbol(
    symbols: List[str], data_dir: str = "data/"
) -> Generator[MarketEvent, None, None]:
    """Stream merged chronological MarketEvents for multiple symbols."""
    return stream_multiple(symbols, data_dir)


def stream_multi_symbol_with_dividends(
    symbols: List[str], data_dir: str = "data/"
) -> Generator:
    """
    Stream MarketEvents and DividendEvents merged chronologically.
    Used by the backtesting engine when dividend tracking is enabled.
    Yields: MarketEvent | DividendEvent
    """
    return stream_multiple_with_dividends(symbols, data_dir)
