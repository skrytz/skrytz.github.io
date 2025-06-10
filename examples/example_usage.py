"""
Example usage of the Stock Data Pipeline
Demonstrates fetching data for various tickers including ES/SPY/SPX, NQ/QQQ/NDX, and MAG7 stocks
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.stock_data_pipeline import StockDataPipeline
from datetime import datetime, timedelta
import pandas as pd

def example_single_ticker():
    """Basic usage example - fetch 1 year of SPY data"""
    print("=== Single Ticker Example (SPY) ===")
    
    # Initialize pipeline
    pipeline = StockDataPipeline()
    
    # Run pipeline for 1 year of SPY data
    result = pipeline.run_pipeline("SPY", period="1y", save_filename="SPY_example.csv")
    
    if result:
        print(f"✅ Success! Data saved to: {result}")
        
        # Load and display first few rows
        data = pd.read_csv(result)
        print(f"\nDataset shape: {data.shape}")
        print("\nFirst 5 rows:")
        print(data.head())
        print("\nColumn info:")
        print(data.dtypes)
    else:
        print("❌ Pipeline failed")

def example_mag7_stocks():
    """Example fetching all MAG7 stocks"""
    print("\n=== MAG7 Stocks Example ===")
    
    pipeline = StockDataPipeline()
    
    # MAG7 tickers
    mag7_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA']
    
    print(f"Fetching 6 months of data for MAG7 stocks: {', '.join(mag7_tickers)}")
    
    # Fetch data for all MAG7 stocks
    results = pipeline.run_multiple_tickers(mag7_tickers, period="6mo")
    
    print(f"\nResults:")
    for ticker, filepath in results.items():
        if filepath:
            data = pd.read_csv(filepath)
            print(f"✅ {ticker}: {len(data)} records saved to {filepath}")
        else:
            print(f"❌ {ticker}: Failed")

def example_index_etfs():
    """Example fetching index ETFs and futures"""
    print("\n=== Index ETFs and Futures Example ===")
    
    pipeline = StockDataPipeline()
    
    # Index-related tickers
    index_tickers = ['SPY', 'QQQ', 'ES=F', 'NQ=F']
    
    print(f"Fetching 3 months of data for: {', '.join(index_tickers)}")
    
    results = pipeline.run_multiple_tickers(index_tickers, period="3mo")
    
    print(f"\nResults:")
    for ticker, filepath in results.items():
        if filepath:
            data = pd.read_csv(filepath)
            latest_close = data['close'].iloc[-1] if 'close' in data.columns else 'N/A'
            print(f"✅ {ticker}: {len(data)} records, Latest close: ${latest_close}")
        else:
            print(f"❌ {ticker}: Failed")

def example_date_range():
    """Example using specific date range"""
    print("\n=== Date Range Example (NVDA) ===")
    
    pipeline = StockDataPipeline()
    
    # Fetch NVDA data for the last 90 days
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    
    print(f"Fetching NVDA data from {start_date} to {end_date}")
    
    # Fetch data by date range
    raw_data = pipeline.fetch_data_by_date_range("NVDA", start_date, end_date)
    
    if raw_data is not None:
        # Process the data
        processed_data = pipeline.process_data(raw_data, "NVDA")
        
        if processed_data is not None:
            # Save to CSV
            filepath = pipeline.save_to_csv(processed_data, "NVDA", "NVDA_90days.csv")
            
            if filepath:
                print(f"✅ Success! Data saved to: {filepath}")
                print(f"Records fetched: {len(processed_data)}")
                
                # Show some statistics
                if 'close' in processed_data.columns:
                    print(f"\nNVDA Price Statistics (90 days):")
                    print(f"Highest close: ${processed_data['close'].max():.2f}")
                    print(f"Lowest close: ${processed_data['close'].min():.2f}")
                    print(f"Average close: ${processed_data['close'].mean():.2f}")
                    print(f"Latest close: ${processed_data['close'].iloc[-1]:.2f}")
            else:
                print("❌ Failed to save data")
        else:
            print("❌ Failed to process data")
    else:
        print("❌ Failed to fetch data")

def example_ticker_info():
    """Example getting ticker information"""
    print("\n=== Ticker Information Example ===")
    
    pipeline = StockDataPipeline()
    
    # Get info for a few tickers
    tickers = ['AAPL', 'SPY', 'QQQ', 'TSLA']
    
    for ticker in tickers:
        info = pipeline.get_ticker_info(ticker)
        if info:
            print(f"\n{ticker} ({info['name']}):")
            print(f"  Current Price: ${info['current_price']}")
            print(f"  Market Cap: {info['market_cap']}")
            print(f"  Sector: {info['sector']}")
        else:
            print(f"❌ Failed to get info for {ticker}")

def example_all_allowed_tickers():
    """Example showing all allowed tickers"""
    print("\n=== All Allowed Tickers ===")
    
    pipeline = StockDataPipeline()
    
    allowed_tickers = pipeline.get_allowed_tickers()
    
    print("S&P 500 Related:")
    for ticker, name in allowed_tickers.items():
        if any(x in ticker for x in ['SPY', 'SPX', 'ES']):
            print(f"  {ticker}: {name}")
    
    print("\nNASDAQ Related:")
    for ticker, name in allowed_tickers.items():
        if any(x in ticker for x in ['QQQ', 'NDX', 'NQ']):
            print(f"  {ticker}: {name}")
    
    print("\nMAG7 Stocks:")
    mag7 = ['AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'TSLA', 'META', 'NVDA']
    for ticker in mag7:
        if ticker in allowed_tickers:
            print(f"  {ticker}: {allowed_tickers[ticker]}")

def example_invalid_ticker():
    """Example showing what happens with invalid ticker"""
    print("\n=== Invalid Ticker Example ===")
    
    pipeline = StockDataPipeline()
    
    # Try to fetch data for an invalid ticker
    print("Attempting to fetch data for 'INVALID' ticker...")
    result = pipeline.run_pipeline("INVALID", period="1mo")
    
    if result:
        print(f"✅ Unexpected success: {result}")
    else:
        print("❌ Expected failure - ticker not allowed")

def main():
    """Run all examples"""
    print("Stock Data Pipeline Examples")
    print("=" * 60)
    
    try:
        # Show all allowed tickers first
        example_all_allowed_tickers()
        
        # Run examples
        example_single_ticker()
        example_mag7_stocks()
        example_index_etfs()
        example_date_range()
        example_ticker_info()
        example_invalid_ticker()
        
        print("\n" + "=" * 60)
        print("All examples completed!")
        
    except Exception as e:
        print(f"Error running examples: {str(e)}")

if __name__ == "__main__":
    main()