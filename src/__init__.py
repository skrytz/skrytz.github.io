"""
Stock Data Pipeline Package

A comprehensive pipeline for fetching and processing stock data
for ES/SPY/SPX, NQ/QQQ/NDX, and MAG7 stocks.
"""

from .stock_data_pipeline import StockDataPipeline
from .config import *

__version__ = "1.0.0"
__author__ = "Stock Data Pipeline Team"

__all__ = [
    "StockDataPipeline",
    "ALLOWED_TICKERS",
    "MAG7_TICKERS",
    "SP500_RELATED",
    "NASDAQ_RELATED"
]