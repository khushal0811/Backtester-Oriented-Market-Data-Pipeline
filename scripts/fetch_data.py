#!/usr/bin/env python3
import argparse
import sys
import os

# Add parent directory to path to allow importing market_data
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from market_data.ingestion import fetch_multiple, fetch_multiple_dividends
from market_data.normalization import normalize_data
from market_data.storage import save_to_parquet, save_dividends_to_parquet

def main():
    parser = argparse.ArgumentParser(description="Fetch and process market data for backtesting.")
    parser.add_argument("--symbols", type=str, required=True, help="Comma-separated list of ticker symbols (e.g., AAPL,MSFT)")
    parser.add_argument("--start", type=str, required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--interval", type=str, default="1d", help="Data interval (e.g., 1d, 1h, 1m)")
    parser.add_argument("--data-dir", type=str, default="data/", help="Output directory for Parquet files")
    parser.add_argument(
        "--dividends",
        action="store_true",
        default=False,
        help="Also fetch and store dividend history for each symbol."
    )
    
    args = parser.parse_args()
    
    symbols_list = [s.strip() for s in args.symbols.split(",") if s.strip()]
    if not symbols_list:
        print("Error: No valid symbols provided.")
        sys.exit(1)
        
    print(f"Fetching data for {len(symbols_list)} symbol(s)...")
    
    raw_data = fetch_multiple(symbols_list, args.start, args.end, args.interval)
    
    if not raw_data:
        print("No data fetched. Please check symbols, dates, and internet connection.")
        sys.exit(1)
        
    processed_count = 0
    for symbol, df in raw_data.items():
        print(f"Normalizing data for {symbol}...")
        norm_df = normalize_data(df, symbol)
        
        if norm_df.empty:
            print(f"Warning: Normalized dataframe for {symbol} is empty after cleaning. Skipping.")
            continue
            
        print(f"Saving {symbol} to Parquet in {args.data_dir}...")
        save_to_parquet(norm_df, symbol, args.data_dir)
        processed_count += 1
        
    print(f"Successfully processed and stored data for {processed_count} symbol(s).")

    if args.dividends:
        print(f"\nFetching dividend data...")
        dividend_data = fetch_multiple_dividends(symbols_list, args.start, args.end)

        if not dividend_data:
            print("No dividend data found for any symbol (normal for growth stocks).")
        else:
            for symbol, div_df in dividend_data.items():
                print(f"Saving dividends for {symbol} ({len(div_df)} records)...")
                save_dividends_to_parquet(div_df, symbol, args.data_dir)
            print(f"Dividend data saved for {len(dividend_data)} symbol(s).")

if __name__ == "__main__":
    main()
