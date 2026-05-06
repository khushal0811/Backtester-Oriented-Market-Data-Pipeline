import os
import pandas as pd
from typing import List

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
    Scan data directory and return list of symbols with available data.
    """
    if not os.path.exists(data_dir):
        return []
    
    symbols = []
    for file in os.listdir(data_dir):
        if file.endswith(".parquet"):
            symbol = file.replace(".parquet", "")
            symbols.append(symbol)
    return sorted(symbols)
