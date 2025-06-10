"""
Command Line Interface for Stock Data Pipeline
Easy-to-use CLI for fetching stock data
"""

import argparse
import sys
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.stock_data_pipeline import StockDataPipeline
from src.config import MAG7_TICKERS, SP500_RELATED, NASDAQ_RELATED

def main():
    parser = argparse.ArgumentParser(
        description="Stock Data Pipeline CLI - Fetch stock data for allowed tickers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_pipeline.py SPY                    # Fetch 1 year of SPY data
  python run_pipeline.py AAPL -p 6mo           # Fetch 6 months of AAPL data
  python run_pipeline.py SPY -y 2024           # Fetch SPY data for 2024
  python run_pipeline.py NVDA -y 2020          # Fetch NVDA data for 2020
  python run_pipeline.py NVDA -p 1y -o NVDA_yearly.csv  # Custom filename
  python run_pipeline.py --mag7                # Fetch all MAG7 stocks
  python run_pipeline.py --sp500               # Fetch S&P 500 related
  python run_pipeline.py --nasdaq              # Fetch NASDAQ related
  python run_pipeline.py --list                # List all allowed tickers
        """
    )
    
    # Ticker arguments
    parser.add_argument('ticker', nargs='?', help='Stock ticker symbol (e.g., SPY, AAPL, NVDA)')
    parser.add_argument('-p', '--period', default='1y',
                       choices=['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'],
                       help='Data period (default: 1y)')
    parser.add_argument('-y', '--year', type=int, help='Fetch data for specific year (e.g., 2024, 2020)')
    parser.add_argument('-o', '--output', help='Output filename (optional)')
    
    # Batch processing options
    parser.add_argument('--mag7', action='store_true', help='Fetch all MAG7 stocks')
    parser.add_argument('--sp500', action='store_true', help='Fetch S&P 500 related instruments')
    parser.add_argument('--nasdaq', action='store_true', help='Fetch NASDAQ related instruments')
    parser.add_argument('--all', action='store_true', help='Fetch all allowed tickers')
    
    # Utility options
    parser.add_argument('--list', action='store_true', help='List all allowed tickers')
    parser.add_argument('--info', help='Get information about a specific ticker')
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = StockDataPipeline()
    
    # Handle list command
    if args.list:
        print("Allowed Tickers:")
        print("=" * 50)
        
        allowed = pipeline.get_allowed_tickers()
        
        print("\nS&P 500 Related:")
        for ticker in SP500_RELATED:
            print(f"  {ticker}: {allowed[ticker]}")
        
        print("\nNASDAQ Related:")
        for ticker in NASDAQ_RELATED:
            print(f"  {ticker}: {allowed[ticker]}")
        
        print("\nMAG7 Stocks:")
        for ticker in MAG7_TICKERS:
            print(f"  {ticker}: {allowed[ticker]}")
        
        return
    
    # Handle info command
    if args.info:
        print(f"Getting information for {args.info.upper()}...")
        info = pipeline.get_ticker_info(args.info)
        if info:
            print(f"\n{info['symbol']} - {info['name']}")
            print(f"Current Price: ${info['current_price']}")
            print(f"Market Cap: {info['market_cap']}")
            print(f"Sector: {info['sector']}")
            print(f"Industry: {info['industry']}")
        else:
            print(f"❌ Failed to get information for {args.info}")
        return
    
    # Handle batch processing
    if args.mag7:
        print("Fetching MAG7 stocks...")
        results = pipeline.run_multiple_tickers(MAG7_TICKERS, period=args.period)
        print_batch_results(results)
        return
    
    if args.sp500:
        print("Fetching S&P 500 related instruments...")
        results = pipeline.run_multiple_tickers(SP500_RELATED, period=args.period)
        print_batch_results(results)
        return
    
    if args.nasdaq:
        print("Fetching NASDAQ related instruments...")
        results = pipeline.run_multiple_tickers(NASDAQ_RELATED, period=args.period)
        print_batch_results(results)
        return
    
    if args.all:
        print("Fetching all allowed tickers...")
        all_tickers = list(pipeline.get_allowed_tickers().keys())
        results = pipeline.run_multiple_tickers(all_tickers, period=args.period)
        print_batch_results(results)
        return
    
    # Handle single ticker
    if not args.ticker:
        parser.print_help()
        print("\nError: Please specify a ticker symbol or use a batch option (--mag7, --sp500, --nasdaq, --all)")
        sys.exit(1)
    
    # Check for conflicting arguments
    if args.year and args.period != '1y':
        print("Error: Cannot specify both --year and --period. Use --year for specific year or --period for relative time.")
        sys.exit(1)
    
    # Handle year-based fetching
    if args.year:
        print(f"Fetching {args.ticker.upper()} data for year {args.year}...")
        result = pipeline.run_pipeline_by_year(args.ticker, args.year, save_filename=args.output)
    else:
        print(f"Fetching {args.period} of data for {args.ticker.upper()}...")
        result = pipeline.run_pipeline(args.ticker, period=args.period, save_filename=args.output)
    
    if result:
        print(f"Success! Data saved to: {result}")
        
        # Show basic stats
        try:
            import pandas as pd
            data = pd.read_csv(result)
            print(f"\nDataset Info:")
            print(f"  Records: {len(data)}")
            print(f"  Date range: {data['date'].min()} to {data['date'].max()}")
            if 'close' in data.columns:
                print(f"  Price range: ${data['close'].min():.2f} - ${data['close'].max():.2f}")
                print(f"  Latest close: ${data['close'].iloc[-1]:.2f}")
        except Exception as e:
            print(f"Note: Could not load stats from saved file: {e}")
    else:
        print("Pipeline failed. Check logs for details.")
        sys.exit(1)

def print_batch_results(results):
    """Print results from batch processing"""
    print(f"\nBatch Processing Results:")
    print("=" * 40)
    
    success_count = 0
    total_count = len(results)
    
    for ticker, filepath in results.items():
        if filepath:
            print(f"{ticker}: Success")
            success_count += 1
        else:
            print(f"{ticker}: Failed")
    
    print(f"\nSummary: {success_count}/{total_count} successful")

if __name__ == "__main__":
    main()