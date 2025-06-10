"""
Stock Data Processing Pipeline
Fetches daily candle data for various stock tickers and saves to CSV files
Supports ES/SPY/SPX, NQ/QQQ/NDX, and MAG7 stocks
"""

import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta
import logging

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
    
    def __init__(self, output_dir="data/ticker_data"):
        """
        Initialize the stock data pipeline
        
        Args:
            output_dir (str): Directory to save CSV files
        """
        self.output_dir = output_dir
        self.ensure_output_directory()
        
    def ensure_output_directory(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logging.info(f"Created output directory: {self.output_dir}")
    
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
    
    def fetch_historical_data(self, symbol, period="1y", interval="1d"):
        """
        Fetch historical stock data from Yahoo Finance
        
        Args:
            symbol (str): Stock ticker symbol
            period (str): Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval (str): Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
        Returns:
            pd.DataFrame: Historical stock data
        """
        # Validate ticker
        if not self.validate_ticker(symbol):
            return None
            
        try:
            symbol_upper = symbol.upper()
            ticker_name = self.ALLOWED_TICKERS[symbol_upper]
            logging.info(f"Fetching {period} of {symbol_upper} ({ticker_name}) data with {interval} interval...")
            
            # Create ticker object
            ticker = yf.Ticker(symbol_upper)
            
            # Fetch historical data
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                logging.error(f"No data retrieved from Yahoo Finance for {symbol_upper}")
                return None
                
            logging.info(f"Successfully fetched {len(data)} records for {symbol_upper}")
            return data
            
        except Exception as e:
            logging.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def fetch_data_by_date_range(self, symbol, start_date, end_date, interval="1d"):
        """
        Fetch stock data for a specific date range
        
        Args:
            symbol (str): Stock ticker symbol
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            interval (str): Data interval
        
        Returns:
            pd.DataFrame: Historical stock data
        """
        # Validate ticker
        if not self.validate_ticker(symbol):
            return None
            
        try:
            symbol_upper = symbol.upper()
            ticker_name = self.ALLOWED_TICKERS[symbol_upper]
            logging.info(f"Fetching {symbol_upper} ({ticker_name}) data from {start_date} to {end_date}...")
            
            ticker = yf.Ticker(symbol_upper)
            data = ticker.history(start=start_date, end=end_date, interval=interval)
            
            if data.empty:
                logging.error(f"No data retrieved for {symbol_upper} in the specified date range")
                return None
                
            logging.info(f"Successfully fetched {len(data)} records for {symbol_upper}")
            return data
            
        except Exception as e:
            logging.error(f"Error fetching data by date range for {symbol}: {str(e)}")
            return None
    
    def fetch_data_by_year(self, symbol, year, interval="1d"):
        """
        Fetch stock data for a specific year
        
        Args:
            symbol (str): Stock ticker symbol
            year (int or str): Year to fetch data for (e.g., 2024, 2020)
            interval (str): Data interval
        
        Returns:
            pd.DataFrame: Historical stock data
        """
        try:
            year = int(year)
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            
            logging.info(f"Fetching {symbol.upper()} data for year {year}...")
            return self.fetch_data_by_date_range(symbol, start_date, end_date, interval)
            
        except ValueError:
            logging.error(f"Invalid year format: {year}. Please provide a valid year (e.g., 2024)")
            return None
        except Exception as e:
            logging.error(f"Error fetching data for year {year}: {str(e)}")
            return None
    
    def process_data(self, data, symbol):
        """
        Process and clean the raw stock data
        
        Args:
            data (pd.DataFrame): Raw stock data
            symbol (str): Stock ticker symbol
        
        Returns:
            pd.DataFrame: Processed stock data
        """
        if data is None or data.empty:
            return None
            
        try:
            # Reset index to make Date a column
            processed_data = data.reset_index()
            
            # Rename columns for clarity
            column_mapping = {
                'Date': 'date',
                'Datetime': 'date',  # For some data sources
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
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
    
    def save_to_csv(self, data, symbol, filename=None, period="1y"):
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
                
                filename = f"{symbol_upper}_daily_candles_{date_range}_{period}.csv"
            
            filepath = os.path.join(ticker_dir, filename)
            data.to_csv(filepath, index=False)
            
            logging.info(f"Data saved to: {filepath}")
            return filepath
            
        except Exception as e:
            logging.error(f"Error saving data to CSV: {str(e)}")
            return None
    
    def run_pipeline(self, symbol, period="1y", save_filename=None):
        """
        Run the complete data pipeline for a single ticker
        
        Args:
            symbol (str): Stock ticker symbol
            period (str): Data period to fetch
            save_filename (str): Custom filename for saved CSV
        
        Returns:
            str: Path to saved CSV file
        """
        logging.info(f"Starting data pipeline for {symbol.upper()}...")
        
        # Fetch data
        raw_data = self.fetch_historical_data(symbol, period=period)
        if raw_data is None:
            logging.error(f"Pipeline failed for {symbol}: Could not fetch data")
            return None
        
        # Process data
        processed_data = self.process_data(raw_data, symbol)
        if processed_data is None:
            logging.error(f"Pipeline failed for {symbol}: Could not process data")
            return None
        
        # Save to CSV with period information
        filepath = self.save_to_csv(processed_data, symbol, save_filename, period)
        if filepath is None:
            logging.error(f"Pipeline failed for {symbol}: Could not save data")
            return None
        
        logging.info(f"Data pipeline completed successfully for {symbol.upper()}!")
        return filepath
    
    def run_pipeline_by_year(self, symbol, year, save_filename=None):
        """
        Run the complete data pipeline for a single ticker for a specific year
        
        Args:
            symbol (str): Stock ticker symbol
            year (int or str): Year to fetch data for
            save_filename (str): Custom filename for saved CSV
        
        Returns:
            str: Path to saved CSV file
        """
        logging.info(f"Starting data pipeline for {symbol.upper()} for year {year}...")
        
        # Fetch data by year
        raw_data = self.fetch_data_by_year(symbol, year)
        if raw_data is None:
            logging.error(f"Pipeline failed for {symbol}: Could not fetch data for year {year}")
            return None
        
        # Process data
        processed_data = self.process_data(raw_data, symbol)
        if processed_data is None:
            logging.error(f"Pipeline failed for {symbol}: Could not process data")
            return None
        
        # Save to CSV with year information
        if save_filename is None:
            save_filename = f"{symbol.upper()}_daily_candles_{year}.csv"
        
        filepath = self.save_to_csv(processed_data, symbol, save_filename, str(year))
        if filepath is None:
            logging.error(f"Pipeline failed for {symbol}: Could not save data")
            return None
        
        logging.info(f"Data pipeline completed successfully for {symbol.upper()} for year {year}!")
        return filepath
    
    def run_multiple_tickers(self, symbols, period="1y"):
        """
        Run the pipeline for multiple tickers
        
        Args:
            symbols (list): List of stock ticker symbols
            period (str): Data period to fetch
        
        Returns:
            dict: Dictionary mapping symbols to their saved file paths
        """
        results = {}
        
        for symbol in symbols:
            logging.info(f"Processing ticker {symbol.upper()}...")
            
            # Let the pipeline generate the filename automatically with date range
            result = self.run_pipeline(symbol, period=period, save_filename=None)
            
            if result:
                results[symbol.upper()] = result
                logging.info(f"✅ {symbol.upper()}: Success")
            else:
                results[symbol.upper()] = None
                logging.error(f"❌ {symbol.upper()}: Failed")
        
        return results
    
    def get_ticker_info(self, symbol):
        """
        Get basic information about a ticker
        
        Args:
            symbol (str): Stock ticker symbol
            
        Returns:
            dict: Ticker information
        """
        if not self.validate_ticker(symbol):
            return None
            
        try:
            symbol_upper = symbol.upper()
            ticker = yf.Ticker(symbol_upper)
            info = ticker.info
            
            return {
                'symbol': symbol_upper,
                'name': self.ALLOWED_TICKERS[symbol_upper],
                'current_price': info.get('currentPrice', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A')
            }
            
        except Exception as e:
            logging.error(f"Error getting ticker info for {symbol}: {str(e)}")
            return None

def main():
    """Main function to demonstrate the pipeline"""
    # Initialize pipeline
    pipeline = StockDataPipeline()
    
    # Show allowed tickers
    print("Allowed Tickers:")
    for symbol, name in pipeline.get_allowed_tickers().items():
        print(f"  {symbol}: {name}")
    
    # Example: Run pipeline for SPY
    print(f"\nRunning pipeline for SPY...")
    result = pipeline.run_pipeline("SPY", period="1y", save_filename="SPY_1year.csv")
    
    if result:
        print(f"Success! Data saved to: {result}")
    else:
        print("Pipeline failed. Check logs for details.")

if __name__ == "__main__":
    main()