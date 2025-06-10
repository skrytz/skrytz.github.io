"""
Fetch SPY historical data from 2000 to 2024
This script will fetch data for each year and overwrite existing files
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.stock_data_pipeline import StockDataPipeline
import time

def fetch_spy_historical_data():
    """Fetch SPY data from 2000 to 2024"""
    print("Fetching SPY historical data from 2000 to 2024...")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = StockDataPipeline()
    
    # Years to fetch
    start_year = 2000
    end_year = 2024
    
    successful_years = []
    failed_years = []
    
    for year in range(start_year, end_year + 1):
        print(f"\nFetching SPY data for {year}...")
        
        try:
            # Fetch data for the year
            result = pipeline.run_pipeline_by_year("SPY", year)
            
            if result:
                print(f"{year}: Success - {result}")
                successful_years.append(year)
                
                # Small delay to be respectful to the API
                time.sleep(0.5)
            else:
                print(f"{year}: Failed")
                failed_years.append(year)
                
        except Exception as e:
            print(f"{year}: Error - {str(e)}")
            failed_years.append(year)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total years processed: {end_year - start_year + 1}")
    print(f"Successful: {len(successful_years)}")
    print(f"Failed: {len(failed_years)}")
    
    if successful_years:
        print(f"\nSuccessful years: {', '.join(map(str, successful_years))}")
    
    if failed_years:
        print(f"\nFailed years: {', '.join(map(str, failed_years))}")
    
    print(f"\nAll SPY data files saved in: ticker_data/SPY/")
    
    return successful_years, failed_years

if __name__ == "__main__":
    successful, failed = fetch_spy_historical_data()
    
    if len(successful) > 0:
        print(f"\nSuccessfully fetched {len(successful)} years of SPY data!")
    
    if len(failed) > 0:
        print(f"\n{len(failed)} years failed to fetch. Check logs for details.")