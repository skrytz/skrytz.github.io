# Stock Data Processing Pipeline

A Python-based data processing pipeline for fetching and processing stock data for various tickers including ES/SPY/SPX, NQ/QQQ/NDX, and MAG7 stocks using Yahoo Finance as a free data source.

## Supported Tickers

### S&P 500 Related
- **SPY**: SPDR S&P 500 ETF Trust
- **SPX**: S&P 500 Index  
- **ES=F**: E-mini S&P 500 Futures

### NASDAQ Related
- **QQQ**: Invesco QQQ Trust
- **NDX**: NASDAQ-100 Index
- **NQ=F**: E-mini NASDAQ-100 Futures

### MAG7 Stocks
- **AAPL**: Apple Inc.
- **MSFT**: Microsoft Corporation
- **GOOGL**: Alphabet Inc. Class A
- **GOOG**: Alphabet Inc. Class C
- **AMZN**: Amazon.com Inc.
- **TSLA**: Tesla Inc.
- **META**: Meta Platforms Inc.
- **NVDA**: NVIDIA Corporation

## Features

- ✅ Free data source (Yahoo Finance via yfinance library)
- ✅ Fetches daily OHLCV (Open, High, Low, Close, Volume) data
- ✅ Support for multiple ticker symbols
- ✅ Flexible time periods (1 day to max historical data)
- ✅ Data processing and cleaning
- ✅ CSV export functionality
- ✅ Comprehensive logging
- ✅ Error handling and validation
- ✅ Additional calculated fields (daily range, change, change percentage)
- ✅ Batch processing for multiple tickers
- ✅ Ticker validation and restrictions

## Installation

1. **Clone or download the project files**

2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

### Basic Usage - Single Ticker

```python
from stock_data_pipeline import StockDataPipeline

# Initialize pipeline
pipeline = StockDataPipeline()

# Fetch 1 year of SPY data and save to CSV
result = pipeline.run_pipeline("SPY", period="1y", save_filename="SPY_data.csv")

if result:
    print(f"Data saved to: {result}")
```

### Batch Processing - Multiple Tickers

```python
from stock_data_pipeline import StockDataPipeline

# Initialize pipeline
pipeline = StockDataPipeline()

# Fetch data for MAG7 stocks
mag7_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA']
results = pipeline.run_multiple_tickers(mag7_tickers, period="6mo")

for ticker, filepath in results.items():
    if filepath:
        print(f"✅ {ticker}: Success - {filepath}")
    else:
        print(f"❌ {ticker}: Failed")
```

### Run the Example Script

```bash
python example_usage.py
```

This will demonstrate various usage patterns and create sample CSV files for different ticker groups.

## Data Source

The pipeline uses **Yahoo Finance** as the data source via the `yfinance` Python library. This is completely free and doesn't require API keys or registration.

### Available Data Periods

- `1d`, `5d` - Recent days
- `1mo`, `3mo`, `6mo` - Recent months  
- `1y`, `2y`, `5y`, `10y` - Recent years
- `ytd` - Year to date
- `max` - Maximum available historical data

### Data Intervals

- `1d` - Daily (recommended for this pipeline)
- `1wk` - Weekly
- `1mo` - Monthly

## Pipeline Components

### 1. StockDataPipeline Class

Main class that handles the entire data processing workflow:

```python
pipeline = StockDataPipeline(output_dir="data")
```

### 2. Key Methods

#### `run_pipeline(symbol, period, save_filename)`
Runs the complete pipeline for a single ticker from fetch to save.

```python
result = pipeline.run_pipeline("AAPL", period="1y", save_filename="AAPL_data.csv")
```

#### `run_multiple_tickers(symbols, period)`
Runs the pipeline for multiple tickers in batch.

```python
results = pipeline.run_multiple_tickers(['SPY', 'QQQ', 'AAPL'], period="6mo")
```

#### `fetch_historical_data(symbol, period, interval)`
Fetches historical data for a specified period.

```python
data = pipeline.fetch_historical_data("NVDA", period="1y", interval="1d")
```

#### `fetch_data_by_date_range(symbol, start_date, end_date)`
Fetches data for a specific date range.

```python
data = pipeline.fetch_data_by_date_range("TSLA", "2023-01-01", "2023-12-31")
```

#### `get_allowed_tickers()`
Returns dictionary of all allowed tickers and their descriptions.

```python
allowed = pipeline.get_allowed_tickers()
```

#### `get_ticker_info(symbol)`
Gets basic information about a ticker.

```python
info = pipeline.get_ticker_info("AAPL")
```

## Output Data Format

The CSV files contain the following columns:

| Column | Description |
|--------|-------------|
| `date` | Trading date |
| `symbol` | Stock ticker symbol |
| `open` | Opening price |
| `high` | Highest price |
| `low` | Lowest price |
| `close` | Closing price |
| `volume` | Trading volume |
| `daily_range` | High - Low |
| `daily_change` | Close - Open |
| `daily_change_pct` | Daily change percentage |

## Examples

### Example 1: Single Ticker (SPY)

```python
from stock_data_pipeline import StockDataPipeline

pipeline = StockDataPipeline()
result = pipeline.run_pipeline("SPY", period="1y", save_filename="SPY_1year.csv")
```

### Example 2: MAG7 Stocks Batch Processing

```python
pipeline = StockDataPipeline()

mag7_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA']
results = pipeline.run_multiple_tickers(mag7_tickers, period="6mo")
```

### Example 3: Index ETFs and Futures

```python
pipeline = StockDataPipeline()

index_tickers = ['SPY', 'QQQ', 'ES=F', 'NQ=F']
results = pipeline.run_multiple_tickers(index_tickers, period="3mo")
```

### Example 4: Specific Date Range

```python
pipeline = StockDataPipeline()

# Fetch NVDA data for specific date range
raw_data = pipeline.fetch_data_by_date_range("NVDA", "2023-01-01", "2023-12-31")
processed_data = pipeline.process_data(raw_data, "NVDA")
pipeline.save_to_csv(processed_data, "NVDA", "NVDA_2023.csv")
```

## Configuration

Modify [`config.py`](config.py) to customize:

- Allowed tickers list
- Output directory
- Default time periods
- Decimal places for rounding
- Logging settings
- File naming conventions
- Ticker groupings (MAG7, S&P 500 related, etc.)

## Ticker Validation

The pipeline includes strict ticker validation. Only the predefined list of tickers is allowed:

- **S&P 500 Related**: SPY, SPX, ES=F
- **NASDAQ Related**: QQQ, NDX, NQ=F  
- **MAG7 Stocks**: AAPL, MSFT, GOOGL, GOOG, AMZN, TSLA, META, NVDA

Attempting to use any other ticker will result in an error message listing the allowed tickers.

## Logging

The pipeline creates detailed logs in `stock_pipeline.log` including:

- Data fetch operations for each ticker
- Processing steps
- Error messages
- File save operations
- Validation failures

## Error Handling

The pipeline includes comprehensive error handling for:

- Invalid ticker symbols
- Network connectivity issues
- Invalid date ranges
- Data processing errors
- File I/O operations

## File Structure

```
├── stock_data_pipeline.py    # Main pipeline class
├── spy_data_pipeline.py      # Legacy SPY-only pipeline (deprecated)
├── config.py                # Configuration settings
├── example_usage.py         # Usage examples
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── data/                   # Output directory (created automatically)
└── stock_pipeline.log      # Log file (created automatically)
```

## Batch Processing Examples

### Process All MAG7 Stocks

```python
from config import MAG7_TICKERS
pipeline = StockDataPipeline()
results = pipeline.run_multiple_tickers(MAG7_TICKERS, period="1y")
```

### Process S&P 500 Related Instruments

```python
from config import SP500_RELATED
pipeline = StockDataPipeline()
results = pipeline.run_multiple_tickers(SP500_RELATED, period="6mo")
```

### Process NASDAQ Related Instruments

```python
from config import NASDAQ_RELATED
pipeline = StockDataPipeline()
results = pipeline.run_multiple_tickers(NASDAQ_RELATED, period="3mo")
```

## Troubleshooting

### Common Issues

1. **Ticker not allowed**: Check the allowed tickers list in the error message
2. **No data retrieved**: Check internet connection and verify ticker symbol
3. **Import errors**: Ensure all dependencies are installed via `pip install -r requirements.txt`
4. **Permission errors**: Check write permissions for the output directory

### Getting Help

Check the log file `stock_pipeline.log` for detailed error messages and debugging information.

## License

This project is open source and available under the MIT License.

## Disclaimer

This tool is for educational and research purposes. The data is provided by Yahoo Finance and the accuracy is not guaranteed. Always verify financial data from official sources before making investment decisions.