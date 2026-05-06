import yfinance as yf
import pandas as pd
from typing import List, Optional, Dict

def fetch_symbol(symbol: str, start: str, end: str, interval: str = "1d") -> Optional[pd.DataFrame]:
    """
    Fetch OHLCV data for a single symbol using yfinance.
    
    Args:
        symbol (str): Ticker symbol.
        start (str): Start date (YYYY-MM-DD).
        end (str): End date (YYYY-MM-DD).
        interval (str): Data interval (e.g., '1d', '1h', '1m').
        
    Returns:
        Optional[pd.DataFrame]: The fetched data, or None if fetching failed.
    """
    try:
        df = yf.download(tickers=symbol, start=start, end=end, interval=interval, progress=False)
        if df is None or df.empty:
            return None
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def fetch_multiple(symbols: List[str], start: str, end: str, interval: str = "1d") -> Dict[str, pd.DataFrame]:
    """
    Fetch OHLCV data for multiple symbols.
    
    Args:
        symbols (List[str]): List of ticker symbols.
        start (str): Start date (YYYY-MM-DD).
        end (str): End date (YYYY-MM-DD).
        interval (str): Data interval.
        
    Returns:
        Dict[str, pd.DataFrame]: Dictionary mapping symbol to its DataFrame.
    """
    data = {}
    for symbol in symbols:
        df = fetch_symbol(symbol, start=start, end=end, interval=interval)
        if df is not None and not df.empty:
            data[symbol] = df
    return data
