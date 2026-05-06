import pandas as pd
import numpy as np

def normalize_data(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """
    Normalize the yfinance DataFrame.
    
    Args:
        df (pd.DataFrame): Raw dataframe from yfinance.
        symbol (str): The ticker symbol.
        
    Returns:
        pd.DataFrame: Normalized dataframe.
    """
    if df is None or df.empty:
        return pd.DataFrame()
        
    # Reset index to move Date/Datetime to a column
    df = df.reset_index()
    
    # Flatten columns if they are a MultiIndex (happens in newer yfinance versions)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [str(col[0]).lower() for col in df.columns]
    else:
        df.columns = [str(col).lower() for col in df.columns]
    
    # Ensure standard schema exists, yfinance might use 'date' or 'datetime'
    if 'date' in df.columns:
        df.rename(columns={'date': 'timestamp'}, inplace=True)
    elif 'datetime' in df.columns:
        df.rename(columns={'datetime': 'timestamp'}, inplace=True)
    
    # Keep only needed columns; if adj close exists, drop it
    expected_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    
    for col in expected_cols:
        if col not in df.columns:
            if col == 'timestamp':
                raise ValueError("Could not find date/datetime column to map to timestamp.")
            else:
                df[col] = np.nan
                
    df = df[expected_cols].copy()
    
    # Add symbol column
    df['symbol'] = symbol
    
    # Enforce types
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)
    df['symbol'] = df['symbol'].astype(str)
    
    # Sort by timestamp
    df = df.sort_values(by='timestamp')
    
    # Drop duplicates
    df = df.drop_duplicates(subset=['timestamp'])
    
    # Handle missing values
    df = df.dropna()
    
    # Reset index again after dropping/sorting
    df = df.reset_index(drop=True)
    
    # Rearrange columns to put symbol and timestamp first
    cols = ['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume']
    df = df[cols]
    
    return df
