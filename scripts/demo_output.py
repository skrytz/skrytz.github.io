"""
Demo script showing what the Stock Data Pipeline output would look like
This runs without external dependencies to demonstrate the expected behavior
"""

import os
from datetime import datetime, timedelta
import random

def simulate_stock_data(symbol, days=252):
    """Simulate stock data for demonstration"""
    
    # Starting values (approximate real values)
    start_prices = {
        'SPY': 400.0,
        'AAPL': 150.0,
        'MSFT': 300.0,
        'GOOGL': 2500.0,
        'AMZN': 3000.0,
        'TSLA': 800.0,
        'META': 200.0,
        'NVDA': 400.0,
        'QQQ': 350.0
    }
    
    base_price = start_prices.get(symbol, 100.0)
    data = []
    
    current_date = datetime.now() - timedelta(days=days)
    
    for i in range(days):
        # Simulate daily price movement
        daily_change = random.uniform(-0.05, 0.05)  # -5% to +5% daily change
        
        if i == 0:
            open_price = base_price
        else:
            open_price = data[i-1]['close'] * (1 + random.uniform(-0.02, 0.02))
        
        high = open_price * (1 + random.uniform(0, 0.03))
        low = open_price * (1 - random.uniform(0, 0.03))
        close = open_price * (1 + daily_change)
        
        # Ensure high >= max(open, close) and low <= min(open, close)
        high = max(high, open_price, close)
        low = min(low, open_price, close)
        
        volume = random.randint(1000000, 50000000)
        
        daily_range = high - low
        daily_change_val = close - open_price
        daily_change_pct = (daily_change_val / open_price) * 100
        
        data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'symbol': symbol,
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'volume': volume,
            'daily_range': round(daily_range, 2),
            'daily_change': round(daily_change_val, 2),
            'daily_change_pct': round(daily_change_pct, 2)
        })
        
        current_date += timedelta(days=1)
    
    return data

def create_demo_csv(symbol, data, filename):
    """Create a demo CSV file"""
    
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    filepath = os.path.join('data', filename)
    
    # Write CSV header and data
    with open(filepath, 'w') as f:
        # Write header
        f.write('date,symbol,open,high,low,close,volume,daily_range,daily_change,daily_change_pct\n')
        
        # Write data
        for row in data:
            f.write(f"{row['date']},{row['symbol']},{row['open']},{row['high']},{row['low']},{row['close']},{row['volume']},{row['daily_range']},{row['daily_change']},{row['daily_change_pct']}\n")
    
    return filepath

def demo_single_ticker():
    """Demo single ticker processing"""
    print("=== Demo: Single Ticker (SPY) ===")
    print("Simulating: pipeline.run_pipeline('SPY', period='1y')")
    print()
    
    # Simulate fetching data
    print("📡 Fetching 1y of SPY (SPDR S&P 500 ETF Trust) data with 1d interval...")
    data = simulate_stock_data('SPY', days=252)
    print(f"✅ Successfully fetched {len(data)} records for SPY")
    
    # Simulate processing
    print("🔄 Data processing completed successfully for SPY")
    
    # Simulate saving
    filename = f"SPY_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = create_demo_csv('SPY', data, filename)
    print(f"💾 Data saved to: {filepath}")
    
    # Show sample data
    print(f"\n📊 Sample data (first 5 rows):")
    print("Date       | Symbol | Open    | High    | Low     | Close   | Volume    | Range | Change | Change%")
    print("-" * 95)
    for i in range(min(5, len(data))):
        row = data[i]
        print(f"{row['date']} | {row['symbol']:6} | ${row['open']:6.2f} | ${row['high']:6.2f} | ${row['low']:6.2f} | ${row['close']:6.2f} | {row['volume']:8,} | ${row['daily_range']:4.2f} | ${row['daily_change']:5.2f} | {row['daily_change_pct']:5.2f}%")
    
    # Show statistics
    closes = [row['close'] for row in data]
    print(f"\n📈 Price Statistics:")
    print(f"   Highest close: ${max(closes):.2f}")
    print(f"   Lowest close:  ${min(closes):.2f}")
    print(f"   Average close: ${sum(closes)/len(closes):.2f}")
    print(f"   Latest close:  ${closes[-1]:.2f}")
    
    return filepath

def demo_mag7_batch():
    """Demo MAG7 batch processing"""
    print("\n=== Demo: MAG7 Batch Processing ===")
    print("Simulating: pipeline.run_multiple_tickers(['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA'], period='6mo')")
    print()
    
    mag7_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA']
    results = {}
    
    for ticker in mag7_tickers:
        print(f"📡 Processing {ticker}...")
        data = simulate_stock_data(ticker, days=126)  # ~6 months
        filename = f"{ticker}_6mo_demo.csv"
        filepath = create_demo_csv(ticker, data, filename)
        results[ticker] = filepath
        print(f"✅ {ticker}: {len(data)} records saved to {filename}")
    
    print(f"\n🎉 Batch Processing Results:")
    print(f"   Successfully processed {len(results)}/{len(mag7_tickers)} tickers")
    
    return results

def demo_allowed_tickers():
    """Demo showing allowed tickers"""
    print("\n=== Demo: Allowed Tickers ===")
    print("Simulating: pipeline.get_allowed_tickers()")
    print()
    
    allowed_tickers = {
        'SPY': 'SPDR S&P 500 ETF Trust',
        'SPX': 'S&P 500 Index',
        'ES=F': 'E-mini S&P 500 Futures',
        'QQQ': 'Invesco QQQ Trust',
        'NDX': 'NASDAQ-100 Index',
        'NQ=F': 'E-mini NASDAQ-100 Futures',
        'AAPL': 'Apple Inc.',
        'MSFT': 'Microsoft Corporation',
        'GOOGL': 'Alphabet Inc. Class A',
        'GOOG': 'Alphabet Inc. Class C',
        'AMZN': 'Amazon.com Inc.',
        'TSLA': 'Tesla Inc.',
        'META': 'Meta Platforms Inc.',
        'NVDA': 'NVIDIA Corporation'
    }
    
    print("S&P 500 Related:")
    sp500_related = ['SPY', 'SPX', 'ES=F']
    for ticker in sp500_related:
        print(f"  {ticker}: {allowed_tickers[ticker]}")
    
    print("\nNASDAQ Related:")
    nasdaq_related = ['QQQ', 'NDX', 'NQ=F']
    for ticker in nasdaq_related:
        print(f"  {ticker}: {allowed_tickers[ticker]}")
    
    print("\nMAG7 Stocks:")
    mag7 = ['AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'TSLA', 'META', 'NVDA']
    for ticker in mag7:
        print(f"  {ticker}: {allowed_tickers[ticker]}")

def demo_validation():
    """Demo ticker validation"""
    print("\n=== Demo: Ticker Validation ===")
    print("Simulating: pipeline.validate_ticker('INVALID')")
    print()
    
    print("❌ Ticker 'INVALID' not allowed. Allowed tickers: SPY, SPX, ES=F, QQQ, NDX, NQ=F, AAPL, MSFT, GOOGL, GOOG, AMZN, TSLA, META, NVDA")
    print("✅ Ticker 'AAPL' validation passed")

def main():
    """Run the demo"""
    print("🚀 Stock Data Pipeline Demo")
    print("=" * 60)
    print("This demo shows what the pipeline would do when Python is properly installed")
    print("=" * 60)
    
    try:
        # Run demos
        demo_allowed_tickers()
        demo_validation()
        demo_single_ticker()
        demo_mag7_batch()
        
        print("\n" + "=" * 60)
        print("🎉 Demo completed!")
        print("\n📁 Demo files created in the 'data/' directory")
        print("💡 To run the real pipeline:")
        print("   1. Install Python (see setup_instructions.md)")
        print("   2. Run: pip install -r requirements.txt")
        print("   3. Run: python stock_data_pipeline.py")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    main()