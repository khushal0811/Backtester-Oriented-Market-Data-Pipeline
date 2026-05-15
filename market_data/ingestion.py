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
        df = yf.download(
            tickers=symbol,
            start=start,
            end=end,
            interval=interval,
            auto_adjust=True,   # Adjusts for splits and dividends
            progress=False
        )
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

def fetch_dividends(symbol: str, start: str, end: str) -> Optional[pd.DataFrame]:
    """
    Fetch dividend history for a single symbol using yfinance.

    Args:
        symbol (str): Ticker symbol.
        start  (str): Start date (YYYY-MM-DD).
        end    (str): End date (YYYY-MM-DD).

    Returns:
        Optional[pd.DataFrame]: DataFrame with columns [timestamp, symbol,
        dividend_per_share], or None if no dividends exist or fetch failed.
    """
    try:
        ticker = yf.Ticker(symbol)
        divs = ticker.dividends  # pandas Series: DatetimeIndex → float

        if divs is None or divs.empty:
            return None

        # Filter to requested date range
        divs = divs[(divs.index >= pd.Timestamp(start, tz="UTC"))
                    & (divs.index <= pd.Timestamp(end, tz="UTC"))]

        if divs.empty:
            return None

        df = divs.reset_index()
        df.columns = ["timestamp", "dividend_per_share"]
        df["symbol"] = symbol
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df = df[["timestamp", "symbol", "dividend_per_share"]]
        df = df.sort_values("timestamp").reset_index(drop=True)

        return df

    except Exception as e:
        print(f"Error fetching dividends for {symbol}: {e}")
        return None


def fetch_multiple_dividends(
    symbols: List[str], start: str, end: str
) -> Dict[str, pd.DataFrame]:
    """
    Fetch dividend history for multiple symbols.

    Returns only symbols that have dividend data in the requested range.
    Symbols with no dividends (e.g. growth stocks) are silently omitted.
    """
    data = {}
    for symbol in symbols:
        df = fetch_dividends(symbol, start=start, end=end)
        if df is not None and not df.empty:
            data[symbol] = df
    return data
