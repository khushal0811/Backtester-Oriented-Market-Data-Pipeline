# Market Data Pipeline

## Overview
A deterministic, reusable data pipeline designed specifically for event-driven backtesting engines. It ingests historical OHLCV market data, enforces a strict normalization schema, stores data efficiently, and exposes a high-performance event stream interface.

## Architecture
The pipeline is designed in discrete phases to maintain modularity and correctness:
1. **Ingestion**: Fetches raw historical data using `yfinance`.
2. **Normalization**: Enforces types, standardizes column names, converts timestamps to UTC, sorts chronologically, and cleans missing/duplicate data.
3. **Storage**: Persists data efficiently in partitioned Parquet files (one file per symbol).
4. **Event Stream**: Converts static historical DataFrames into a memory-efficient generator of chronological `MarketEvent` instances.

## Data Schema
All persisted Parquet files and streaming events adhere to the following schema:
- `timestamp`: UTC timezone-aware datetime
- `symbol`: string
- `open`: float
- `high`: float
- `low`: float
- `close`: float
- `volume`: float

## Example Usage

### 1. Fetching Data via CLI
Use the provided script to download and store data:
```bash
python scripts/fetch_data.py --symbols AAPL,MSFT --start 2024-01-01 --end 2024-01-10 --interval 1d
```

### 2. Loading Data
Retrieve the raw normalized dataframe for analytics:
```python
from market_data.api import load_data

df = load_data("AAPL", data_dir="data/")
print(df.head())
```

### 3. Streaming Events
Consume the data as an ordered sequence of market events across multiple symbols:
```python
from market_data.api import stream_multi_symbol

# Stream seamlessly merges data for AAPL and MSFT chronologically
event_stream = stream_multi_symbol(["AAPL", "MSFT"], data_dir="data/")

for event in event_stream:
    print(f"[{event.timestamp}] {event.symbol}: {event.price} (Vol: {event.volume})")
```

## Folder Structure
```
.
├── market_data/          # Core pipeline package
│   ├── __init__.py
│   ├── api.py            # High-level wrapper for external use
│   ├── events.py         # Event dataclass and generator logic
│   ├── ingestion.py      # yfinance data fetching
│   ├── normalization.py  # Schema enforcement and data cleaning
│   └── storage.py        # Parquet read/write operations
├── scripts/
│   └── fetch_data.py     # CLI orchestrator
├── data/                 # Default output directory for Parquet files
├── Context/              # Project scope and architecture (ignored by Git)
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## Tech Stack
- **Language**: Python 3.9+
- **Data Processing**: pandas, numpy
- **Storage**: pyarrow (Parquet)
- **Data Source**: yfinance

## Integration with Backtesting Engines
This pipeline is explicitly built to decouple data ingestion from backtesting logic. It avoids real-time execution, WebSockets, or UI bindings. To connect it to your backtester:
1. Instantiate your engine.
2. Call `stream_multi_symbol(['TICKER1', 'TICKER2'])`.
3. Pass the resulting generator into your engine's main event loop.
4. Your engine will process `MarketEvent` instances strictly in the order they historically occurred, ensuring deterministic and accurate simulation without lookahead bias.
