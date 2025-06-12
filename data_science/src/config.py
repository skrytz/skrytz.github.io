"""
Configuration file for the stock data pipeline
"""

# IBKR Connection Settings
IBKR_HOST = '127.0.0.1'
IBKR_PORT = 7496
IBKR_CLIENT_ID = 1

# Data Settings
DEFAULT_DURATION = '1 Y'
DEFAULT_BAR_SIZE = '1 day'

# File Paths
DATA_DIR = '../data'
TICKER_DATA_DIR = '../data/ticker_data'
ANALYSIS_RESULTS_DIR = '../data/analysis_results'