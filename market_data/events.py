from dataclasses import dataclass
from datetime import datetime
import pandas as pd
from typing import Generator, List, Optional

from .storage import load_from_parquet

@dataclass
class MarketEvent:
    timestamp: datetime
    symbol: str
    price: float
    volume: float

@dataclass
class DividendEvent:
    """
    Represents a dividend payment on a specific date.

    Emitted by the DataHandler when the simulation bar date matches
    a dividend ex-date for a held symbol.

    Attributes:
        timestamp          : Ex-dividend date (UTC).
        symbol             : Ticker symbol.
        dividend_per_share : Dividend amount in dollars per share.
    """
    timestamp:          datetime
    symbol:             str
    dividend_per_share: float

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

def stream_dividends(
    symbol: str, data_dir: str = "data/"
) -> Generator[DividendEvent, None, None]:
    """
    Load dividend data for a symbol and yield DividendEvents.
    Returns empty generator if no dividend file exists (not an error).
    """
    from .storage import load_dividends_from_parquet
    df = load_dividends_from_parquet(symbol, data_dir)
    if df is None or df.empty:
        return
    for _, row in df.iterrows():
        yield DividendEvent(
            timestamp=row["timestamp"],
            symbol=row["symbol"],
            dividend_per_share=float(row["dividend_per_share"]),
        )


def stream_multiple_with_dividends(
    symbols: List[str], data_dir: str = "data/"
) -> Generator:
    """
    Stream MarketEvents and DividendEvents merged chronologically.

    The engine's DataHandler will use this to receive both price bars
    and dividend events in correct temporal order, ensuring dividends
    are credited on the right date during simulation.

    Yields: MarketEvent | DividendEvent (in timestamp order)
    """
    from .storage import load_dividends_from_parquet

    all_events = []

    for symbol in symbols:
        try:
            df = load_from_parquet(symbol, data_dir)
            for _, row in df.iterrows():
                all_events.append(MarketEvent(
                    timestamp=row["timestamp"],
                    symbol=row["symbol"],
                    price=float(row["close"]),
                    volume=float(row["volume"]),
                ))
        except FileNotFoundError:
            print(f"Warning: Data not found for {symbol}, skipping.")

        div_df = load_dividends_from_parquet(symbol, data_dir)
        if div_df is not None:
            for _, row in div_df.iterrows():
                all_events.append(DividendEvent(
                    timestamp=row["timestamp"],
                    symbol=row["symbol"],
                    dividend_per_share=float(row["dividend_per_share"]),
                ))

    # Sort all events chronologically — MarketEvents and DividendEvents together
    all_events.sort(key=lambda e: e.timestamp)
    yield from all_events
