from typing import List, Generator
import pandas as pd

from .storage import load_from_parquet, get_available_symbols
from .events import MarketEvent, stream_events as events_stream_single, stream_multiple

def get_symbols(data_dir: str = "data/") -> List[str]:
    """Return available symbols."""
    return get_available_symbols(data_dir)

def load_data(symbol: str, data_dir: str = "data/") -> pd.DataFrame:
    """Load normalized dataframe for a symbol."""
    return load_from_parquet(symbol, data_dir)

def stream_events(symbol: str, data_dir: str = "data/") -> Generator[MarketEvent, None, None]:
    """Stream events for a single symbol."""
    return events_stream_single(symbol, data_dir)

def stream_multi_symbol(symbols: List[str], data_dir: str = "data/") -> Generator[MarketEvent, None, None]:
    """Stream merged events for multiple symbols."""
    return stream_multiple(symbols, data_dir)
