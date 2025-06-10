"""
SPY Data Processing Pipeline
Fetches daily candle data for SPY ETF and saves to CSV files
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
        logging.FileHandler('spy_pipeline.log'),
        logging.StreamHandler()
    ]
)

class SPYDataPipeline:
    def __init__(self, output_dir="data"):
        """
        Initialize the SPY data pipeline
        
        Args:
            output_dir (str): Directory to save CSV files
        """
        self.symbol = "SPY"
        self.output_dir = output_dir
        self.ensure_output_directory()
        
    def ensure_output_directory(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logging.info(f"Created output directory: {self.output_dir}")
    
    def fetch_historical_data(self, period="1y", interval="1d"):
        """
        Fetch historical SPY data from Yahoo Finance
        
        Args:
            period (str): Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval (str): Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
        Returns:
            pd.DataFrame: Historical stock data
        """
        try:
            logging.info(f"Fetching {period} of {self.symbol} data with {interval} interval...")
            
            # Create ticker object
            ticker = yf.Ticker(self.symbol)
            
            # Fetch historical data
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                logging.error("No data retrieved from Yahoo Finance")
                return None
                
            logging.info(f"Successfully fetched {len(data)} records")
            return data
            
        except Exception as e:
            logging.error(f"Error fetching data: {str(e)}")
            return None
    
    def fetch_data_by_date_range(self, start_date, end_date, interval="1d"):
        """
        Fetch SPY data for a specific date range
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            interval (str): Data interval
        
        Returns:
            pd.DataFrame: Historical stock data
        """
        try:
            logging.info(f"Fetching {self.symbol} data from {start_date} to {end_date}...")
            
            ticker = yf.Ticker(self.symbol)
            data = ticker.history(start=start_date, end=end_date, interval=interval)
            
            if data.empty:
                logging.error("No data retrieved for the specified date range")
                return None
                
            logging.info(f"Successfully fetched {len(data)} records")
            return data
            
        except Exception as e:
            logging.error(f"Error fetching data by date range: {str(e)}")
            return None
    
    def process_data(self, data):
        """
        Process and clean the raw stock data
        
        Args:
            data (pd.DataFrame): Raw stock data
        
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
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            }
            
            # Only rename columns that exist
            existing_columns = {k: v for k, v in column_mapping.items() if k in processed_data.columns}
            processed_data = processed_data.rename(columns=existing_columns)
            
            # Ensure date column is datetime
            if 'date' in processed_data.columns:
                processed_data['date'] = pd.to_datetime(processed_data['date'])
            
            # Round price columns to 2 decimal places
            price_columns = ['open', 'high', 'low', 'close']
            for col in price_columns:
                if col in processed_data.columns:
                    processed_data[col] = processed_data[col].round(2)
            
            # Add additional calculated fields
            if all(col in processed_data.columns for col in ['high', 'low', 'close']):
                processed_data['daily_range'] = (processed_data['high'] - processed_data['low']).round(2)
                processed_data['daily_change'] = (processed_data['close'] - processed_data['open']).round(2)
                processed_data['daily_change_pct'] = ((processed_data['close'] - processed_data['open']) / processed_data['open'] * 100).round(2)
            
            logging.info("Data processing completed successfully")
            return processed_data
            
        except Exception as e:
            logging.error(f"Error processing data: {str(e)}")
            return None
    
    def save_to_csv(self, data, filename=None):
        """
        Save processed data to CSV file
        
        Args:
            data (pd.DataFrame): Processed stock data
            filename (str): Custom filename (optional)
        
        Returns:
            str: Path to saved file
        """
        if data is None or data.empty:
            logging.error("No data to save")
            return None
            
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"SPY_daily_data_{timestamp}.csv"
            
            filepath = os.path.join(self.output_dir, filename)
            data.to_csv(filepath, index=False)
            
            logging.info(f"Data saved to: {filepath}")
            return filepath
            
        except Exception as e:
            logging.error(f"Error saving data to CSV: {str(e)}")
            return None
    
    def run_pipeline(self, period="1y", save_filename=None):
        """
        Run the complete data pipeline
        
        Args:
            period (str): Data period to fetch
            save_filename (str): Custom filename for saved CSV
        
        Returns:
            str: Path to saved CSV file
        """
        logging.info("Starting SPY data pipeline...")
        
        # Fetch data
        raw_data = self.fetch_historical_data(period=period)
        if raw_data is None:
            logging.error("Pipeline failed: Could not fetch data")
            return None
        
        # Process data
        processed_data = self.process_data(raw_data)
        if processed_data is None:
            logging.error("Pipeline failed: Could not process data")
            return None
        
        # Save to CSV
        filepath = self.save_to_csv(processed_data, save_filename)
        if filepath is None:
            logging.error("Pipeline failed: Could not save data")
            return None
        
        logging.info("SPY data pipeline completed successfully!")
        return filepath

def main():
    """Main function to run the pipeline"""
    # Initialize pipeline
    pipeline = SPYDataPipeline()
    
    # Run pipeline for 1 year of data
    result = pipeline.run_pipeline(period="1y", save_filename="SPY_daily_1year.csv")
    
    if result:
        print(f"Pipeline completed successfully! Data saved to: {result}")
    else:
        print("Pipeline failed. Check logs for details.")

if __name__ == "__main__":
    main()