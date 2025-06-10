"""
Configuration settings for Stock Data Pipeline
"""

# Allowed tickers and their descriptions
ALLOWED_TICKERS = {
    # S&P 500 related
    'SPY': 'SPDR S&P 500 ETF Trust',
    'SPX': 'S&P 500 Index',
    'ES=F': 'E-mini S&P 500 Futures',
    
    # NASDAQ related  
    'QQQ': 'Invesco QQQ Trust',
    'NDX': 'NASDAQ-100 Index',
    'NQ=F': 'E-mini NASDAQ-100 Futures',
    
    # MAG7 stocks
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft Corporation',
    'GOOGL': 'Alphabet Inc. Class A',
    'GOOG': 'Alphabet Inc. Class C',
    'AMZN': 'Amazon.com Inc.',
    'TSLA': 'Tesla Inc.',
    'META': 'Meta Platforms Inc.',
    'NVDA': 'NVIDIA Corporation'
}

# Data source settings
DEFAULT_PERIOD = "1y"  # 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
DEFAULT_INTERVAL = "1d"  # 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo

# Output settings
OUTPUT_DIR = "data/ticker_data"
LOG_FILE = "data/logs/stock_pipeline.log"

# Data processing settings
PRICE_DECIMAL_PLACES = 2
PERCENTAGE_DECIMAL_PLACES = 2

# File naming
DEFAULT_FILENAME_PREFIX = "daily_data"
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# MAG7 stock grouping for convenience
MAG7_TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'TSLA', 'META', 'NVDA']

# Index-related groupings
SP500_RELATED = ['SPY', 'SPX', 'ES=F']
NASDAQ_RELATED = ['QQQ', 'NDX', 'NQ=F']

# Common time periods for batch processing
COMMON_PERIODS = ['1mo', '3mo', '6mo', '1y', '2y']