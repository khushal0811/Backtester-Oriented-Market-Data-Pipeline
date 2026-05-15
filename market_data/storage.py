import os
import pandas as pd
from typing import List, Optional

def save_to_parquet(df: pd.DataFrame, symbol: str, data_dir: str = "data/") -> None:
    """
    Save normalized dataframe to Parquet.
    """
    os.makedirs(data_dir, exist_ok=True)
    file_path = os.path.join(data_dir, f"{symbol}.parquet")
    df.to_parquet(file_path, index=False)

def load_from_parquet(symbol: str, data_dir: str = "data/") -> pd.DataFrame:
    """
    Load data from Parquet for a specific symbol.
    """
    file_path = os.path.join(data_dir, f"{symbol}.parquet")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No data found for {symbol} at {file_path}")
    return pd.read_parquet(file_path)

def get_available_symbols(data_dir: str = "data/") -> List[str]:
    """
    Scan data directory and return list of symbols with available OHLCV data.
    Excludes dividend files (e.g. AAPL_dividends.parquet).
    """
    if not os.path.exists(data_dir):
        return []
    
    symbols = []
    for file in os.listdir(data_dir):
        if file.endswith(".parquet") and "_dividends" not in file:
            symbol = file.replace(".parquet", "")
            symbols.append(symbol)
    return sorted(symbols)

def save_dividends_to_parquet(
    df: pd.DataFrame, symbol: str, data_dir: str = "data/"
) -> None:
    """
    Save dividend DataFrame to Parquet.
    Stored as <data_dir>/<symbol>_dividends.parquet
    """
    os.makedirs(data_dir, exist_ok=True)
    file_path = os.path.join(data_dir, f"{symbol}_dividends.parquet")
    df.to_parquet(file_path, index=False)


def load_dividends_from_parquet(
    symbol: str, data_dir: str = "data/"
) -> Optional[pd.DataFrame]:
    """
    Load dividend data for a symbol. Returns None if no dividend file exists.
    Not all symbols pay dividends — a missing file is normal, not an error.
    """
    file_path = os.path.join(data_dir, f"{symbol}_dividends.parquet")
    if not os.path.exists(file_path):
        return None
    return pd.read_parquet(file_path)


def get_data_info(symbol: str, data_dir: str = "data/") -> dict:
    """
    Return metadata about stored data for a symbol without loading
    the full Parquet file into memory.

    Used by the frontend to check data availability before running
    a backtest — called once per ticker chip on add.

    Returns:
        dict with keys:
            exists              (bool)   — whether any data file is present
            start               (str)    — earliest available date (ISO format)
            end                 (str)    — latest available date (ISO format)
            row_count           (int)    — number of bars available
            has_dividends       (bool)   — whether dividend data exists
            dividend_start      (str)    — earliest dividend date or None
            dividend_end        (str)    — latest dividend date or None
    """
    file_path = os.path.join(data_dir, f"{symbol}.parquet")

    if not os.path.exists(file_path):
        return {
            "exists": False,
            "start": None,
            "end": None,
            "row_count": 0,
            "has_dividends": False,
            "dividend_start": None,
            "dividend_end": None,
        }

    # Read only the Parquet metadata — does not load row data
    import pyarrow.parquet as pq
    meta = pq.read_metadata(file_path)
    row_count = meta.num_rows

    # To get min/max timestamp we need one column scan — efficient with
    # column projection (reads only the timestamp column, not OHLCV)
    table = pq.read_table(file_path, columns=["timestamp"])
    timestamps = table.column("timestamp")
    start_ts = timestamps[0].as_py()
    end_ts = timestamps[-1].as_py()

    # Check dividend file
    div_path = os.path.join(data_dir, f"{symbol}_dividends.parquet")
    has_dividends = os.path.exists(div_path)
    div_start = None
    div_end = None

    if has_dividends:
        div_table = pq.read_table(div_path, columns=["timestamp"])
        div_ts = div_table.column("timestamp")
        div_start = div_ts[0].as_py().isoformat()
        div_end = div_ts[-1].as_py().isoformat()

    return {
        "exists": True,
        "start": start_ts.isoformat(),
        "end": end_ts.isoformat(),
        "row_count": row_count,
        "has_dividends": has_dividends,
        "dividend_start": div_start,
        "dividend_end": div_end,
    }
