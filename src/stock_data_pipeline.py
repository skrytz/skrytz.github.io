"""
Stock Data Processing Pipeline - IBKR Edition
Fetches daily candle data for various stock tickers and saves to CSV files
Uses Interactive Brokers API exclusively for institutional-grade data
"""

import pandas as pd
import os
from datetime import datetime, timedelta
import logging

# IBKR imports
try:
    from ib_insync import IB, Stock, util
    IBKR_AVAILABLE = True
except ImportError:
    IBKR_AVAILABLE = False
    raise ImportError("ib_insync not installed. Install with: pip install ib_insync")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/stock_pipeline.log'),
        logging.StreamHandler()
    ]
)

class StockDataPipeline:
    # Allowed tickers
    ALLOWED_TICKERS = {
        # S&P 500 related
        'SPY': 'SPDR S&P 500 ETF Trust',
        'SPX': 'S&P 500 Index',
        'ES': 'E-mini S&P 500 Futures',
        
        # NASDAQ related  
        'QQQ': 'Invesco QQQ Trust',
        'NDX': 'NASDAQ-100 Index',
        'NQ': 'E-mini NASDAQ-100 Futures',
        
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
    
    def __init__(self, output_dir="data/ticker_data", ibkr_host='127.0.0.1', ibkr_port=7497):
        """
        Initialize the IBKR stock data pipeline
        
        Args:
            output_dir (str): Directory to save CSV files
            ibkr_host (str): IBKR Gateway/TWS host (default: localhost)
            ibkr_port (int): IBKR Gateway (7497) or TWS (7496) port
        """
        self.output_dir = output_dir
        self.ibkr_host = ibkr_host
        self.ibkr_port = ibkr_port
        self.ib = None
        self.ibkr_connected = False
        
        self.ensure_output_directory()
        logging.info("IBKR Stock Data Pipeline initialized")
        
    def ensure_output_directory(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logging.info(f"Created output directory: {self.output_dir}")
        
        # Create logs directory
        logs_dir = "data/logs"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
    
    def get_allowed_tickers(self):
        """
        Get list of allowed tickers
        
        Returns:
            dict: Dictionary of allowed tickers and their descriptions
        """
        return self.ALLOWED_TICKERS.copy()
    
    def validate_ticker(self, symbol):
        """
        Validate if the ticker is allowed
        
        Args:
            symbol (str): Stock ticker symbol
            
        Returns:
            bool: True if ticker is allowed, False otherwise
        """
        if symbol.upper() not in self.ALLOWED_TICKERS:
            allowed_list = ', '.join(self.ALLOWED_TICKERS.keys())
            logging.error(f"Ticker '{symbol}' not allowed. Allowed tickers: {allowed_list}")
            return False
        return True
    
    def connect_ibkr(self):
        """Connect to IBKR Gateway/TWS"""
        try:
            if self.ib is None:
                self.ib = IB()
            
            if not self.ibkr_connected:
                self.ib.connect(self.ibkr_host, self.ibkr_port, clientId=1)
                self.ibkr_connected = True
                logging.info(f"✅ Connected to IBKR at {self.ibkr_host}:{self.ibkr_port}")
            return True
        except Exception as e:
            logging.error(f"❌ Failed to connect to IBKR: {e}")
            logging.error("SETUP REQUIRED:")
            logging.error("1. Download and install IB Gateway or TWS")
            logging.error("2. Start IB Gateway (port 7497) or TWS (port 7496)")
            logging.error("3. Enable API connections in settings")
            logging.error("4. Make sure your IBKR account has market data permissions")
            return False
    
    def disconnect_ibkr(self):
        """Disconnect from IBKR"""
        if self.ib and self.ibkr_connected:
            try:
                self.ib.disconnect()
                self.ibkr_connected = False
                logging.info("Disconnected from IBKR")
            except:
                pass
    
    def fetch_historical_data(self, symbol, duration='2 Y', bar_size='1 day'):
        """
        Fetch historical data from IBKR
        
        Args:
            symbol (str): Stock ticker symbol
            duration (str): Data duration ('1 Y', '2 Y', '6 M', '1 M', etc.)
            bar_size (str): Bar size ('1 day', '1 hour', '5 mins', etc.)
        
        Returns:
            pd.DataFrame: Historical stock data
        """
        # Validate ticker
        if not self.validate_ticker(symbol):
            return None
        
        # Connect to IBKR
        if not self.connect_ibkr():
            return None
        
        try:
            symbol_upper = symbol.upper()
            ticker_name = self.ALLOWED_TICKERS[symbol_upper]
            logging.info(f"Fetching {duration} of {symbol_upper} ({ticker_name}) data...")
            
            # Create stock contract
            stock = Stock(symbol_upper, 'SMART', 'USD')
            
            # Qualify the contract
            qualified_contracts = self.ib.qualifyContracts(stock)
            if not qualified_contracts:
                logging.error(f"Could not qualify contract for {symbol_upper}")
                return None
            
            contract = qualified_contracts[0]
            logging.info(f"Qualified contract: {contract}")
            
            # Request historical data
            bars = self.ib.reqHistoricalData(
                contract,
                endDateTime='',
                durationStr=duration,
                barSizeSetting=bar_size,
                whatToShow='TRADES',
                useRTH=True,  # Regular trading hours only
                formatDate=1
            )
            
            if not bars:
                logging.error(f"No data received for {symbol_upper}")
                return None
            
            # Convert to DataFrame
            df = util.df(bars)
            
            if df.empty:
                logging.error(f"Empty dataframe received for {symbol_upper}")
                return None
            
            logging.info(f"✅ Successfully fetched {len(df)} records from IBKR for {symbol_upper}")
            return df
            
        except Exception as e:
            logging.error(f"Error fetching IBKR data for {symbol}: {e}")
            return None
    
    def fetch_data_by_date_range(self, symbol, start_date, end_date, bar_size='1 day'):
        """
        Fetch stock data for a specific date range
        
        Args:
            symbol (str): Stock ticker symbol
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            bar_size (str): Bar size
        
        Returns:
            pd.DataFrame: Historical stock data
        """
        # Calculate duration from date range
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        duration_days = (end_dt - start_dt).days
        
        if duration_days <= 365:
            duration = f"{duration_days} D"
        else:
            duration_years = duration_days / 365.25
            duration = f"{duration_years:.1f} Y"
        
        logging.info(f"Fetching {symbol} data from {start_date} to {end_date} (duration: {duration})")
        return self.fetch_historical_data(symbol, duration, bar_size)
    
    def fetch_data_by_year(self, symbol, year, bar_size='1 day'):
        """
        Fetch stock data for a specific year
        
        Args:
            symbol (str): Stock ticker symbol
            year (int or str): Year to fetch data for
            bar_size (str): Bar size
        
        Returns:
            pd.DataFrame: Historical stock data
        """
        try:
            year = int(year)
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            
            logging.info(f"Fetching {symbol} data for year {year}...")
            return self.fetch_data_by_date_range(symbol, start_date, end_date, bar_size)
            
        except ValueError:
            logging.error(f"Invalid year format: {year}")
            return None
    
    def process_data(self, data, symbol):
        """
        Process and clean the raw stock data from IBKR
        
        Args:
            data (pd.DataFrame): Raw stock data from IBKR
            symbol (str): Stock ticker symbol
        
        Returns:
            pd.DataFrame: Processed stock data
        """
        if data is None or data.empty:
            return None
            
        try:
            # Reset index to make Date a column
            processed_data = data.reset_index()
            
            # Rename columns for consistency
            column_mapping = {
                'date': 'date',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'volume': 'volume'
            }
            
            # Only rename columns that exist
            existing_columns = {k: v for k, v in column_mapping.items() if k in processed_data.columns}
            processed_data = processed_data.rename(columns=existing_columns)
            
            # Add symbol column
            processed_data['symbol'] = symbol.upper()
            
            # Ensure date column is datetime
            if 'date' in processed_data.columns:
                processed_data['date'] = pd.to_datetime(processed_data['date'])
            
            # Round price columns to 2 decimal places
            price_columns = ['open', 'high', 'low', 'close']
            for col in price_columns:
                if col in processed_data.columns:
                    processed_data[col] = processed_data[col].round(2)
            
            # Add additional calculated fields
            if all(col in processed_data.columns for col in ['high', 'low', 'close', 'open']):
                processed_data['daily_range'] = (processed_data['high'] - processed_data['low']).round(2)
                processed_data['daily_change'] = (processed_data['close'] - processed_data['open']).round(2)
                processed_data['daily_change_pct'] = ((processed_data['close'] - processed_data['open']) / processed_data['open'] * 100).round(2)
            
            # Reorder columns for better readability
            column_order = ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume', 'daily_range', 'daily_change', 'daily_change_pct']
            available_columns = [col for col in column_order if col in processed_data.columns]
            other_columns = [col for col in processed_data.columns if col not in column_order]
            processed_data = processed_data[available_columns + other_columns]
            
            logging.info(f"Data processing completed successfully for {symbol.upper()}")
            return processed_data
            
        except Exception as e:
            logging.error(f"Error processing data for {symbol}: {str(e)}")
            return None
    
    def save_to_csv(self, data, symbol, filename=None, period="historical"):
        """
        Save processed data to CSV file in organized folder structure
        
        Args:
            data (pd.DataFrame): Processed stock data
            symbol (str): Stock ticker symbol
            filename (str): Custom filename (optional)
            period (str): Data period for filename generation
        
        Returns:
            str: Path to saved file
        """
        if data is None or data.empty:
            logging.error("No data to save")
            return None
            
        try:
            symbol_upper = symbol.upper()
            
            # Create ticker-specific subdirectory
            ticker_dir = os.path.join(self.output_dir, symbol_upper)
            if not os.path.exists(ticker_dir):
                os.makedirs(ticker_dir)
                logging.info(f"Created ticker directory: {ticker_dir}")
            
            if filename is None:
                # Generate filename with date range information
                if 'date' in data.columns and len(data) > 0:
                    start_date = pd.to_datetime(data['date'].min()).strftime("%Y%m%d")
                    end_date = pd.to_datetime(data['date'].max()).strftime("%Y%m%d")
                    date_range = f"{start_date}_to_{end_date}"
                else:
                    # Fallback to current timestamp
                    date_range = datetime.now().strftime("%Y%m%d")
                
                filename = f"{symbol_upper}_daily_candles_{date_range}_IBKR.csv"
            
            filepath = os.path.join(ticker_dir, filename)
            data.to_csv(filepath, index=False)
            
            logging.info(f"✅ IBKR data saved to: {filepath}")
            return filepath
            
        except Exception as e:
            logging.error(f"Error saving data to CSV: {str(e)}")
            return None
    
    def run_pipeline(self, symbol, duration="2 Y", save_filename=None):
        """
        Run the complete IBKR data pipeline for a single ticker
        
        Args:
            symbol (str): Stock ticker symbol
            duration (str): Data duration to fetch
            save_filename (str): Custom filename for saved CSV
        
        Returns:
            str: Path to saved CSV file
        """
        logging.info(f"Starting IBKR data pipeline for {symbol.upper()}...")
        
        try:
            # Fetch data from IBKR
            raw_data = self.fetch_historical_data(symbol, duration=duration)
            if raw_data is None:
                logging.error(f"Pipeline failed for {symbol}: Could not fetch data from IBKR")
                return None
            
            # Process data
            processed_data = self.process_data(raw_data, symbol)
            if processed_data is None:
                logging.error(f"Pipeline failed for {symbol}: Could not process data")
                return None
            
            # Save to CSV
            filepath = self.save_to_csv(processed_data, symbol, save_filename, duration)
            if filepath is None:
                logging.error(f"Pipeline failed for {symbol}: Could not save data")
                return None
            
            logging.info(f"✅ IBKR data pipeline completed successfully for {symbol.upper()}!")
            return filepath
            
        except Exception as e:
            logging.error(f"Pipeline error for {symbol}: {e}")
            return None
        finally:
            # Always disconnect when done
            self.disconnect_ibkr()
    
    def run_multiple_tickers(self, symbols, duration="2 Y"):
        """
        Run the IBKR pipeline for multiple tickers
        
        Args:
            symbols (list): List of stock ticker symbols
            duration (str): Data duration to fetch
        
        Returns:
            dict: Dictionary mapping symbols to their saved file paths
        """
        results = {}
        
        for symbol in symbols:
            logging.info(f"Processing ticker {symbol.upper()}...")
            
            result = self.run_pipeline(symbol, duration=duration)
            
            if result:
                results[symbol.upper()] = result
                logging.info(f"✅ {symbol.upper()}: Success")
            else:
                results[symbol.upper()] = None
                logging.error(f"❌ {symbol.upper()}: Failed")
        
        return results
    
    def get_ticker_info(self, symbol):
        """
        Get basic information about a ticker from IBKR
        
        Args:
            symbol (str): Stock ticker symbol
            
        Returns:
            dict: Ticker information
        """
        if not self.validate_ticker(symbol):
            return None
        
        if not self.connect_ibkr():
            return None
            
        try:
            symbol_upper = symbol.upper()
            stock = Stock(symbol_upper, 'SMART', 'USD')
            
            qualified_contracts = self.ib.qualifyContracts(stock)
            if not qualified_contracts:
                return None
            
            contract = qualified_contracts[0]
            
            return {
                'symbol': symbol_upper,
                'name': self.ALLOWED_TICKERS[symbol_upper],
                'exchange': contract.exchange,
                'currency': contract.currency,
                'contract_id': contract.conId
            }
            
        except Exception as e:
            logging.error(f"Error getting ticker info for {symbol}: {str(e)}")
            return None

def main():
    """Main function to demonstrate the IBKR pipeline"""
    # Initialize pipeline
    pipeline = StockDataPipeline()
    
    # Show allowed tickers
    print("IBKR Stock Data Pipeline")
    print("=" * 50)
    print("Allowed Tickers:")
    for symbol, name in pipeline.get_allowed_tickers().items():
        print(f"  {symbol}: {name}")
    
    print(f"\nSetup Requirements:")
    print(f"1. Install ib_insync: pip install ib_insync")
    print(f"2. Download and start IB Gateway or TWS")
    print(f"3. Enable API connections in IB Gateway/TWS settings")
    print(f"4. Ensure market data permissions are enabled")
    
    # Example: Run pipeline for SPY
    print(f"\nRunning IBKR pipeline for SPY...")
    result = pipeline.run_pipeline("SPY", duration="1 Y")
    
    if result:
        print(f"✅ Success! IBKR data saved to: {result}")
    else:
        print("❌ Pipeline failed. Check IBKR connection and logs.")

if __name__ == "__main__":
    main()