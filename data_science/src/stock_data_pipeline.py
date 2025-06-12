#!/usr/bin/env python3
"""
Stock Data Pipeline for IBKR Historical Data Collection
Restored after accidental deletion
"""

import pandas as pd
from datetime import datetime
import time
import logging
from ib_insync import *

class StockDataPipeline:
    def __init__(self, host='127.0.0.1', port=7496, client_id=1):
        """Initialize the IBKR connection"""
        self.ib = IB()
        self.host = host
        self.port = port
        self.client_id = client_id
        self.connected = False
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Connect to IBKR
        self.connect()
    
    def connect(self):
        """Connect to IBKR TWS/Gateway"""
        try:
            self.logger.info(f"Connecting to {self.host}:{self.port} with clientId {self.client_id}...")
            self.ib.connect(self.host, self.port, clientId=self.client_id)
            self.connected = True
            self.logger.info(f"Connected to IBKR at {self.host}:{self.port}")
        except Exception as e:
            self.logger.error(f"Failed to connect to IBKR: {e}")
            self.connected = False
    
    def fetch_historical_data(self, symbol, duration='1 Y', bar_size='1 day', end_date=''):
        """Fetch historical data from IBKR"""
        if not self.connected:
            self.logger.error("Not connected to IBKR")
            return None
        
        try:
            # Create contract
            if symbol == 'SPX':
                contract = Index('SPX', 'CBOE')
            else:
                contract = Stock(symbol, 'SMART', 'USD')
            
            self.logger.info(f"Fetching {duration} of {symbol} data...")
            
            # Request historical data
            bars = self.ib.reqHistoricalData(
                contract,
                endDateTime=end_date,
                durationStr=duration,
                barSizeSetting=bar_size,
                whatToShow='TRADES',
                useRTH=False,  # Include extended hours
                formatDate=1
            )
            
            if bars:
                self.logger.info(f"Successfully fetched {len(bars)} records from IBKR for {symbol}")
                # Convert to DataFrame
                df = util.df(bars)
                return df
            else:
                self.logger.error(f"No data received for {symbol}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    def process_data(self, df, symbol):
        """Process the raw IBKR data"""
        if df is None or df.empty:
            return None
        
        try:
            # Rename columns to match our format
            df = df.rename(columns={
                'date': 'date',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'volume': 'volume',
                'average': 'average',
                'barCount': 'barCount'
            })
            
            # Add symbol column
            df['symbol'] = symbol
            
            # Calculate additional metrics
            df['daily_range'] = df['high'] - df['low']
            df['daily_change'] = df['close'] - df['open']
            df['daily_change_pct'] = (df['daily_change'] / df['open']) * 100
            
            # Add index column
            df['index'] = range(len(df))
            
            # Reorder columns
            columns = ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume', 
                      'daily_range', 'daily_change', 'daily_change_pct', 'index', 'average', 'barCount']
            df = df[columns]
            
            self.logger.info(f"Data processing completed successfully for {symbol}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error processing data for {symbol}: {e}")
            return None
    
    def disconnect(self):
        """Disconnect from IBKR"""
        if self.connected:
            self.ib.disconnect()
            self.connected = False
            self.logger.info("Disconnected from IBKR")