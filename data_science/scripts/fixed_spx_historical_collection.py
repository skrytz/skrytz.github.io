#!/usr/bin/env python3
"""
SPX Historical Data Collection Script
Collects 10-minute SPX data using correct IBKR endDateTime methodology
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta
import time
import logging

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from stock_data_pipeline import StockDataPipeline

def setup_logging():
    """Setup logging for the historical data collection"""
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'spx_collection.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def collect_spx_historical_data():
    """
    Collect SPX 10-minute data using proper IBKR methodology
    """
    print("SPX Historical Data Collection")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = StockDataPipeline()
    
    # Configuration
    symbol = "SPX"
    bar_size = "10 mins"
    
    # Output file path
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'ticker_data', 'SPX', '10min')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'SPX_10min_collection.csv')
    
    print(f"Target file: {output_file}")
    print(f"Symbol: {symbol}")
    print(f"Bar Size: {bar_size}")
    print(f"Extended Hours: YES")
    print()
    
    # Date range setup
    start_date = datetime(2020, 1, 1)
    end_date = datetime.now()
    current_date = start_date
    
    batch_count = 0
    total_records = 0
    file_created = False
    
    print("Starting historical data collection...")
    print(f"Working FORWARD from {start_date.strftime('%Y-%m-%d')} to present")
    print("Using proper IBKR endDateTime methodology")
    print()
    
    while current_date < end_date:
        batch_count += 1
        batch_end = min(current_date + timedelta(days=30), end_date)  # 30-day chunks
        
        # Format end date for IBKR (YYYYMMDD HH:MM:SS format)
        ibkr_end_date = batch_end.strftime("%Y%m%d 23:59:59")
        duration = "30 D"
        
        print(f"Batch {batch_count}: {current_date.strftime('%Y-%m-%d')} to {batch_end.strftime('%Y-%m-%d')}")
        print(f"  IBKR endDateTime: {ibkr_end_date}")
        
        try:
            # Collect data for this batch using proper endDateTime
            raw_data = pipeline.fetch_historical_data(
                symbol=symbol, 
                duration=duration, 
                bar_size=bar_size,
                end_date=ibkr_end_date
            )
            
            if raw_data is not None and not raw_data.empty:
                # Process the data
                processed_data = pipeline.process_data(raw_data, symbol)
                
                if processed_data is not None and not processed_data.empty:
                    # Convert dates and filter to exact range
                    processed_data['date'] = pd.to_datetime(processed_data['date'])
                    
                    # Remove timezone info for filtering
                    if processed_data['date'].dt.tz is not None:
                        processed_data['date'] = processed_data['date'].dt.tz_localize(None)
                    
                    # Filter to exact date range
                    mask = (processed_data['date'] >= current_date) & (processed_data['date'] < batch_end)
                    batch_data = processed_data[mask]
                    
                    if not batch_data.empty:
                        # Remove duplicates and sort
                        batch_data = batch_data.drop_duplicates(subset=['date']).sort_values('date').reset_index(drop=True)
                        
                        # Save to file
                        if not file_created:
                            # Create file with headers
                            batch_data.to_csv(output_file, index=False)
                            file_created = True
                            print(f"  SUCCESS: {len(batch_data)} records - FILE CREATED")
                        else:
                            # Append without headers
                            batch_data.to_csv(output_file, mode='a', header=False, index=False)
                            print(f"  SUCCESS: {len(batch_data)} records - APPENDED")
                        
                        total_records += len(batch_data)
                        print(f"  Total records so far: {total_records}")
                        
                        # Show date range of this batch
                        print(f"  Date range: {batch_data['date'].min()} to {batch_data['date'].max()}")
                    else:
                        print(f"  No data in date range (filtered out)")
                else:
                    print(f"  FAILED: Could not process data")
            else:
                print(f"  FAILED: No data received from IBKR")
                
        except Exception as e:
            print(f"  ERROR: {e}")
            logging.error(f"Batch {batch_count} failed: {e}")
        
        # Move to next batch
        current_date = batch_end
        
        # Rate limiting
        if batch_count % 5 == 0:
            print(f"  Pausing for 30 seconds (rate limiting)...")
            time.sleep(30)
        else:
            time.sleep(3)  # Pause between requests
    
    # Final summary
    if file_created:
        print(f"\nSUCCESS!")
        print(f"Total records collected: {total_records}")
        print(f"File saved: {output_file}")
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file) / (1024*1024)
            print(f"File size: {file_size:.1f} MB")
            
            # Show sample of final data
            final_data = pd.read_csv(output_file)
            print(f"Final date range: {final_data['date'].min()} to {final_data['date'].max()}")
            print(f"Total unique records: {len(final_data)}")
            print(f"\nSample data (first 5 rows):")
            print(final_data[['date', 'open', 'high', 'low', 'close', 'volume']].head())
        
        return output_file
    else:
        print("FAILED: No data collected")
        return None

if __name__ == "__main__":
    setup_logging()
    
    print("SPX Historical Data Collection Script")
    print("This will collect 10-minute SPX data")
    print("Using proper IBKR endDateTime methodology")
    print()
    print("Starting automatic collection...")
    
    result = collect_spx_historical_data()
    if result:
        print(f"\nSPX historical data collection completed successfully!")
        print(f"Data saved to: {result}")
    else:
        print(f"\nSPX historical data collection failed!")