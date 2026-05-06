from dataclasses import dataclass
from datetime import datetime
import pandas as pd
from typing import Generator, List

from .storage import load_from_parquet

@dataclass
class MarketEvent:
    timestamp: datetime
    symbol: str
    price: float
    volume: float

def dataframe_to_events(df: pd.DataFrame) -> Generator[MarketEvent, None, None]:
    """
    Convert a DataFrame to a stream (generator) of MarketEvent objects.
    """
    for _, row in df.iterrows():
        yield MarketEvent(
            timestamp=row['timestamp'],
            symbol=row['symbol'],
            price=row['close'],
            volume=row['volume']
        )

def stream_events(symbol: str, data_dir: str = "data/") -> Generator[MarketEvent, None, None]:
    """
    Load data for a single symbol from Parquet and yield events.
    """
    df = load_from_parquet(symbol, data_dir)
    yield from dataframe_to_events(df)

def stream_multiple(symbols: List[str], data_dir: str = "data/") -> Generator[MarketEvent, None, None]:
    """
    Load data for multiple symbols, merge, sort by timestamp, and yield events in order.
    """
    dfs = []
    for symbol in symbols:
        try:
            df = load_from_parquet(symbol, data_dir)
            dfs.append(df)
        except FileNotFoundError:
            print(f"Warning: Data not found for {symbol}, skipping.")
            
    if not dfs:
        return
        
    # Combine and sort by timestamp
    combined_df = pd.concat(dfs, ignore_index=True)
    combined_df = combined_df.sort_values(by='timestamp')
    
    yield from dataframe_to_events(combined_df)
