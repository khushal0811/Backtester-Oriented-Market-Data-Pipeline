# Market Data Pipeline

## Overview
A deterministic, reusable data pipeline designed specifically for event-driven backtesting engines. It ingests historical OHLCV market data and dividend history, enforces a strict normalization schema, stores data efficiently, and exposes a high-performance event stream interface with split-adjusted pricing.

Part of a three-repo trading system workspace:
- **This repo** — Market Data Pipeline (data ingestion, normalization, storage, event streaming)
- [Event-Driven Backtesting Engine](https://github.com/khushal0811/Event-Driven-Backtesting-Engine) — Strategy simulation engine
- [Strategy Research Terminal](https://github.com/khushal0811/strategy-research-terminal) — Full-stack research UI

## Architecture
The pipeline is designed in discrete phases to maintain modularity and correctness:
1. **Ingestion**: Fetches raw historical data using `yfinance` with `auto_adjust=True` for split-corrected, dividend-adjusted pricing. Optionally fetches dividend history.
2. **Normalization**: Enforces types, standardizes column names, converts timestamps to UTC, sorts chronologically, and cleans missing/duplicate data.
3. **Storage**: Persists data efficiently in partitioned Parquet files (one file per symbol for OHLCV, one for dividends).
4. **Event Stream**: Converts static historical DataFrames into a memory-efficient generator of chronological `MarketEvent` and `DividendEvent` instances.

## Data Schema

### OHLCV (per-symbol Parquet)
- `timestamp`: UTC timezone-aware datetime
- `symbol`: string
- `open`: float
- `high`: float
- `low`: float
- `close`: float
- `volume`: float

### Dividends (per-symbol Parquet)
- `timestamp`: UTC timezone-aware datetime
- `symbol`: string
- `dividend_per_share`: float

## Example Usage

### 1. Fetching Data via CLI
Use the provided script to download and store data:
```bash
# Fetch OHLCV only
python scripts/fetch_data.py --symbols AAPL,MSFT --start 2020-01-01 --end 2024-01-01

# Fetch OHLCV + dividend history
python scripts/fetch_data.py --symbols AAPL,MSFT --start 2020-01-01 --end 2024-01-01 --dividends

# Intraday data (dividends flag not needed — dividends are daily events)
python scripts/fetch_data.py --symbols AAPL --start 2024-01-01 --end 2024-03-01 --interval 5m
```

### 2. Loading Data
Retrieve the raw normalized dataframe for analytics:
```python
from market_data.api import load_data, load_dividend_data

df = load_data("AAPL", data_dir="data/")
print(df.head())

# Load dividend history (returns None if no dividends exist)
divs = load_dividend_data("AAPL", data_dir="data/")
```

### 3. Querying Symbol Metadata
Check data availability without loading full Parquet files:
```python
from market_data.api import get_symbol_info

info = get_symbol_info("AAPL", data_dir="data/")
# Returns: { exists, start, end, row_count, has_dividends, dividend_start, dividend_end }
```

### 4. Streaming Events
Consume the data as an ordered sequence of market events across multiple symbols:
```python
from market_data.api import stream_multi_symbol

# Stream seamlessly merges data for AAPL and MSFT chronologically
event_stream = stream_multi_symbol(["AAPL", "MSFT"], data_dir="data/")

for event in event_stream:
    print(f"[{event.timestamp}] {event.symbol}: {event.price} (Vol: {event.volume})")
```

### 5. Streaming with Dividends
For backtests that track dividend income:
```python
from market_data.api import stream_multi_symbol_with_dividends
from market_data.events import MarketEvent, DividendEvent

for event in stream_multi_symbol_with_dividends(["AAPL", "MSFT"]):
    if isinstance(event, DividendEvent):
        print(f"[{event.timestamp}] {event.symbol} dividend: ${event.dividend_per_share}/share")
    elif isinstance(event, MarketEvent):
        print(f"[{event.timestamp}] {event.symbol}: {event.price}")
```

## Folder Structure
```
.
├── market_data/          # Core pipeline package
│   ├── __init__.py
│   ├── api.py            # High-level wrapper for external use
│   ├── events.py         # Event dataclasses and generator logic
│   ├── ingestion.py      # yfinance data fetching (OHLCV + dividends)
│   ├── normalization.py  # Schema enforcement and data cleaning
│   └── storage.py        # Parquet read/write operations + metadata queries
├── scripts/
│   └── fetch_data.py     # CLI orchestrator
├── data/                 # Default output directory for Parquet files
├── Context/              # Project scope and architecture (ignored by Git)
├── pyproject.toml        # Pyrefly type checker configuration
├── requirements.txt      # Python dependencies (pinned minimum versions)
└── README.md             # Project documentation
```

## Tech Stack
- **Language**: Python 3.9+
- **Data Processing**: pandas, numpy
- **Storage**: pyarrow (Parquet)
- **Data Source**: yfinance

## API Reference

| Function | Module | Description |
|---|---|---|
| `get_symbols()` | `api.py` | List all symbols with available OHLCV data |
| `load_data()` | `api.py` | Load normalized OHLCV DataFrame |
| `load_dividend_data()` | `api.py` | Load dividend history (None if no dividends) |
| `get_symbol_info()` | `api.py` | Metadata query without loading full data |
| `stream_events()` | `api.py` | Stream MarketEvents for a single symbol |
| `stream_multi_symbol()` | `api.py` | Stream merged MarketEvents for multiple symbols |
| `stream_multi_symbol_with_dividends()` | `api.py` | Stream merged MarketEvents + DividendEvents |

## Integration with Backtesting Engines
This pipeline is explicitly built to decouple data ingestion from backtesting logic. It avoids real-time execution, WebSockets, or UI bindings. To connect it to your backtester:
1. Instantiate your engine.
2. Call `stream_multi_symbol(['TICKER1', 'TICKER2'])` for price-only simulation, or `stream_multi_symbol_with_dividends(...)` for dividend-aware backtesting.
3. Pass the resulting generator into your engine's main event loop.
4. Your engine will process `MarketEvent` and `DividendEvent` instances strictly in the order they historically occurred, ensuring deterministic and accurate simulation without lookahead bias.
