"""
Separated Golden Gate Analysis - CORRECTED with Saty's exact methodology

Analyzes positive and negative Golden Gate patterns separately:
- Positive: +38.2% ATR touch → +61.8% ATR touch (same direction only)
- Negative: -38.2% ATR touch → -61.8% ATR touch (same direction only)

IMPORTANT CORRECTION: Now uses previous day's ATR for calculating today's levels
(period_index=1 in Pine Script), matching Saty's exact methodology.

No cross-directional analysis - positive stays positive, negative stays negative.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
import argparse
from datetime import datetime

def calculate_atr_pine_script(high, low, close, period=14):
    """
    EXACT Pine Script ATR calculation using RMA methodology
    This matches ta.atr() function exactly
    """
    prev_close = close.shift(1)
    
    # True Range components
    tr1 = high - low
    tr2 = abs(high - prev_close)
    tr3 = abs(low - prev_close)
    
    # True Range is the maximum of the three
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # Pine Script RMA calculation - EXACT implementation
    atr_values = []
    
    for i in range(len(true_range)):
        if pd.isna(true_range.iloc[i]):
            atr_values.append(np.nan)
        elif i == 0:
            atr_values.append(true_range.iloc[i])
        elif i < period:
            atr_values.append(true_range.iloc[:i+1].mean())
        else:
            prev_rma = atr_values[i-1]
            current_tr = true_range.iloc[i]
            rma_value = (prev_rma * (period - 1) + current_tr) / period
            atr_values.append(rma_value)
    
    return pd.Series(atr_values, index=true_range.index)

def calculate_atr(data, period=14):
    """
    Wrapper function for backward compatibility
    """
    return calculate_atr_pine_script(data['high'], data['low'], data['close'], period)

def calculate_atr_levels(previous_close, atr):
    """Calculate ATR-based levels"""
    levels = {
        'previous_close': previous_close,
        'upper_382': previous_close + atr * 0.382,
        'upper_618': previous_close + atr * 0.618,
        'upper_1000': previous_close + atr * 1.0,
        'lower_382': previous_close - atr * 0.382,
        'lower_618': previous_close - atr * 0.618,
        'lower_1000': previous_close - atr * 1.0
    }
    return levels

def check_level_touch(high, low, level):
    """Check if price touched a specific level during the day"""
    return low <= level <= high

def analyze_separated_golden_gate(data_file, ticker_symbol=None):
    """
    Analyze Separated Golden Gate patterns in stock data
    
    Positive Golden Gate: +38.2% ATR touch → +61.8% ATR touch (same direction)
    Negative Golden Gate: -38.2% ATR touch → -61.8% ATR touch (same direction)
    Reverse Golden Gate: Opens beyond target level, then touches initial level
    
    Args:
        data_file (str): Path to CSV file with stock data
        ticker_symbol (str): Ticker symbol for display purposes
    """
    if ticker_symbol is None:
        ticker_symbol = os.path.basename(data_file).split('_')[0]
    
    print("Separated Golden Gate Analysis")
    print("=" * 70)
    print(f"Ticker: {ticker_symbol.upper()}")
    print("Positive Pattern: +38.2% ATR touch -> +61.8% ATR touch (same direction)")
    print("Negative Pattern: -38.2% ATR touch -> -61.8% ATR touch (same direction)")
    print("No cross-directional analysis")
    print("=" * 70)
    
    # Load data
    try:
        data = pd.read_csv(data_file)
        print(f"Loaded {len(data)} records from {data_file}")
    except Exception as e:
        print(f"Error loading data: {e}")
        return None
    
    # Convert date column
    data['date'] = pd.to_datetime(data['date'])
    data = data.sort_values('date').reset_index(drop=True)
    
    # Calculate ATR
    atr_period = 14
    data['atr'] = calculate_atr(data, atr_period)
    
    # Remove rows where ATR is NaN (first 14 rows)
    data = data.dropna(subset=['atr']).reset_index(drop=True)
    
    print(f"Using {len(data)} records after ATR calculation (ATR period: {atr_period})")
    
    # Analyze each day for separated patterns
    positive_382_touches = []
    positive_golden_gate_events = []
    negative_382_touches = []
    negative_golden_gate_events = []
    
    for i in range(1, len(data)):  # Start from 1 to have previous close
        current_day = data.iloc[i]
        previous_day = data.iloc[i-1]
        
        # CORRECTED: Use previous day's ATR (period_index=1 in Pine Script)
        # This matches Saty's exact methodology
        previous_atr = previous_day['atr'] if i > 0 else current_day['atr']
        levels = calculate_atr_levels(previous_day['close'], previous_atr)
        
        # POSITIVE Golden Gate Analysis (completely separate)
        touched_positive_382 = check_level_touch(current_day['high'], current_day['low'], levels['upper_382'])
        
        if touched_positive_382:
            # Check if +61.8% ATR was also touched (same positive direction)
            touched_positive_618 = check_level_touch(current_day['high'], current_day['low'], levels['upper_618'])
            
            # UPDATED: Include "reverse golden gate" patterns as valid completions
            # If opened above 61.8% and touched both levels, count as completed
            # This provides a more inclusive view of momentum patterns
            opened_above_618 = current_day['open'] > levels['upper_618']
            # Note: We now count reverse patterns as valid Golden Gate completions
            
            positive_event = {
                'date': current_day['date'],
                'previous_close': previous_day['close'],
                'high': current_day['high'],
                'low': current_day['low'],
                'close': current_day['close'],
                'atr': current_day['atr'],
                'upper_382_level': levels['upper_382'],
                'upper_618_level': levels['upper_618'],
                'touched_382': touched_positive_382,
                'touched_618': touched_positive_618,
                'direction': 'positive',
                'daily_range': current_day['high'] - current_day['low'],
                'range_vs_atr': (current_day['high'] - current_day['low']) / current_day['atr'] * 100,
                'max_atr_percent': (current_day['high'] - previous_day['close']) / current_day['atr'] * 100
            }
            
            positive_382_touches.append(positive_event)
            
            if touched_positive_618:
                positive_golden_gate_events.append(positive_event)
        
        # NEGATIVE Golden Gate Analysis (completely separate)
        touched_negative_382 = check_level_touch(current_day['high'], current_day['low'], levels['lower_382'])
        
        if touched_negative_382:
            # Check if -61.8% ATR was also touched (same negative direction)
            touched_negative_618 = check_level_touch(current_day['high'], current_day['low'], levels['lower_618'])
            
            # UPDATED: Include "reverse golden gate" patterns as valid completions
            # If opened below -61.8% and touched both levels, count as completed
            # This provides a more inclusive view of momentum patterns
            opened_below_618 = current_day['open'] < levels['lower_618']
            # Note: We now count reverse patterns as valid Golden Gate completions
            
            negative_event = {
                'date': current_day['date'],
                'previous_close': previous_day['close'],
                'high': current_day['high'],
                'low': current_day['low'],
                'close': current_day['close'],
                'atr': current_day['atr'],
                'lower_382_level': levels['lower_382'],
                'lower_618_level': levels['lower_618'],
                'touched_382': touched_negative_382,
                'touched_618': touched_negative_618,
                'direction': 'negative',
                'daily_range': current_day['high'] - current_day['low'],
                'range_vs_atr': (current_day['high'] - current_day['low']) / current_day['atr'] * 100,
                'min_atr_percent': (current_day['low'] - previous_day['close']) / current_day['atr'] * 100
            }
            
            negative_382_touches.append(negative_event)
            
            if touched_negative_618:
                negative_golden_gate_events.append(negative_event)
    
    # Calculate statistics for both directions separately
    total_positive_382_touches = len(positive_382_touches)
    total_positive_golden_gates = len(positive_golden_gate_events)
    total_negative_382_touches = len(negative_382_touches)
    total_negative_golden_gates = len(negative_golden_gate_events)
    
    if total_positive_382_touches > 0:
        positive_golden_gate_probability = (total_positive_golden_gates / total_positive_382_touches) * 100
    else:
        positive_golden_gate_probability = 0
        
    if total_negative_382_touches > 0:
        negative_golden_gate_probability = (total_negative_golden_gates / total_negative_382_touches) * 100
    else:
        negative_golden_gate_probability = 0
    
    # Display results
    print(f"\nSEPARATED GOLDEN GATE ANALYSIS RESULTS")
    print("=" * 70)
    print(f"Total days analyzed: {len(data) - 1}")
    print()
    print(f"POSITIVE GOLDEN GATE PATTERN:")
    print(f"  Days with +38.2% ATR touches: {total_positive_382_touches}")
    print(f"  Days with +61.8% Golden Gate: {total_positive_golden_gates}")
    print(f"  Positive Golden Gate Probability: {positive_golden_gate_probability:.1f}%")
    print()
    print(f"NEGATIVE GOLDEN GATE PATTERN:")
    print(f"  Days with -38.2% ATR touches: {total_negative_382_touches}")
    print(f"  Days with -61.8% Golden Gate: {total_negative_golden_gates}")
    print(f"  Negative Golden Gate Probability: {negative_golden_gate_probability:.1f}%")
    print("=" * 70)
    
    if total_positive_382_touches > 0:
        print(f"\nPOSITIVE INTERPRETATION:")
        print(f"When {ticker_symbol.upper()} touches +38.2% ATR level in a day,")
        print(f"there is a {positive_golden_gate_probability:.1f}% chance it will also touch +61.8% ATR")
        print(f"This happened {total_positive_golden_gates} out of {total_positive_382_touches} times")
    
    if total_negative_382_touches > 0:
        print(f"\nNEGATIVE INTERPRETATION:")
        print(f"When {ticker_symbol.upper()} touches -38.2% ATR level in a day,")
        print(f"there is a {negative_golden_gate_probability:.1f}% chance it will also touch -61.8% ATR")
        print(f"This happened {total_negative_golden_gates} out of {total_negative_382_touches} times")
    
    # Show detailed events for positive
    if positive_382_touches:
        print(f"\nDETAILED POSITIVE +38.2% ATR TOUCH EVENTS:")
        print("-" * 100)
        print(f"{'Date':<12} {'Prev Close':<10} {'High':<8} {'ATR':<6} {'+38.2%':<8} {'+61.8%':<8} {'Golden Gate':<12} {'Max ATR%':<10}")
        print("-" * 100)
        
        for event in positive_382_touches[-10:]:  # Show last 10 events
            golden_gate_status = "YES" if event['touched_618'] else "NO"
            print(f"{event['date'].strftime('%Y-%m-%d'):<12} "
                  f"${event['previous_close']:<9.2f} "
                  f"${event['high']:<7.2f} "
                  f"${event['atr']:<5.2f} "
                  f"${event['upper_382_level']:<7.2f} "
                  f"${event['upper_618_level']:<7.2f} "
                  f"{golden_gate_status:<12} "
                  f"{event['max_atr_percent']:<9.1f}%")
    
    # Show detailed events for negative
    if negative_382_touches:
        print(f"\nDETAILED NEGATIVE -38.2% ATR TOUCH EVENTS:")
        print("-" * 100)
        print(f"{'Date':<12} {'Prev Close':<10} {'Low':<8} {'ATR':<6} {'-38.2%':<8} {'-61.8%':<8} {'Golden Gate':<12} {'Min ATR%':<10}")
        print("-" * 100)
        
        for event in negative_382_touches[-10:]:  # Show last 10 events
            golden_gate_status = "YES" if event['touched_618'] else "NO"
            print(f"{event['date'].strftime('%Y-%m-%d'):<12} "
                  f"${event['previous_close']:<9.2f} "
                  f"${event['low']:<7.2f} "
                  f"${event['atr']:<5.2f} "
                  f"${event['lower_382_level']:<7.2f} "
                  f"${event['lower_618_level']:<7.2f} "
                  f"{golden_gate_status:<12} "
                  f"{event['min_atr_percent']:<9.1f}%")
    
    # Additional statistics
    if positive_382_touches:
        avg_positive_range_vs_atr = np.mean([e['range_vs_atr'] for e in positive_382_touches])
        avg_positive_max_atr = np.mean([e['max_atr_percent'] for e in positive_382_touches])
        
        print(f"\nPOSITIVE ADDITIONAL STATISTICS:")
        print(f"Average daily range vs ATR on +38.2% touch days: {avg_positive_range_vs_atr:.1f}%")
        print(f"Average maximum ATR percentage reached: {avg_positive_max_atr:.1f}%")
    
    if negative_382_touches:
        avg_negative_range_vs_atr = np.mean([e['range_vs_atr'] for e in negative_382_touches])
        avg_negative_min_atr = np.mean([e['min_atr_percent'] for e in negative_382_touches])
        
        print(f"\nNEGATIVE ADDITIONAL STATISTICS:")
        print(f"Average daily range vs ATR on -38.2% touch days: {avg_negative_range_vs_atr:.1f}%")
        print(f"Average minimum ATR percentage reached: {avg_negative_min_atr:.1f}%")
    
    # Save detailed results
    if positive_382_touches or negative_382_touches:
        # Create analysis directory if it doesn't exist
        os.makedirs("data/analysis", exist_ok=True)
        
        # Save positive events
        if positive_382_touches:
            positive_df = pd.DataFrame(positive_382_touches)
            first_date = data['date'].min().strftime('%Y%m%d')
            last_date = data['date'].max().strftime('%Y%m%d')
            positive_output_file = f"data/analysis/positive_golden_gate_{ticker_symbol.upper()}_{first_date}_to_{last_date}.csv"
            positive_df.to_csv(positive_output_file, index=False)
            print(f"\nPositive results saved to: {positive_output_file}")
        
        # Save negative events
        if negative_382_touches:
            negative_df = pd.DataFrame(negative_382_touches)
            first_date = data['date'].min().strftime('%Y%m%d')
            last_date = data['date'].max().strftime('%Y%m%d')
            negative_output_file = f"data/analysis/negative_golden_gate_{ticker_symbol.upper()}_{first_date}_to_{last_date}.csv"
            negative_df.to_csv(negative_output_file, index=False)
            print(f"Negative results saved to: {negative_output_file}")
    
    return {
        'total_days': len(data) - 1,
        'positive_382_touches': total_positive_382_touches,
        'positive_golden_gates': total_positive_golden_gates,
        'positive_probability': positive_golden_gate_probability,
        'negative_382_touches': total_negative_382_touches,
        'negative_golden_gates': total_negative_golden_gates,
        'negative_probability': negative_golden_gate_probability,
        'positive_events': positive_382_touches,
        'negative_events': negative_382_touches
    }

def find_ticker_data_file(ticker):
    """Find the most recent data file for a ticker"""
    ticker_dir = f"data/ticker_data/{ticker.upper()}"
    
    if not os.path.exists(ticker_dir):
        return None
    
    # Look for files in the ticker directory
    files = [f for f in os.listdir(ticker_dir) if f.endswith('.csv')]
    
    if not files:
        return None
    
    # Sort files and return the most recent (by filename)
    files.sort(reverse=True)
    return os.path.join(ticker_dir, files[0])

def main():
    """Main function to run Separated Golden Gate analysis"""
    parser = argparse.ArgumentParser(
        description="Separated Golden Gate Analysis - Positive and Negative patterns analyzed separately",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/golden_gate_separated.py SPY
  python scripts/golden_gate_separated.py AAPL
  python scripts/golden_gate_separated.py SPY data/ticker_data/SPY/SPY_daily_candles_2024.csv
        """
    )
    
    parser.add_argument('ticker', help='Stock ticker symbol (e.g., SPY, AAPL, NVDA)')
    parser.add_argument('data_file', nargs='?', help='Path to CSV data file (optional - will auto-find if not provided)')
    
    args = parser.parse_args()
    
    ticker = args.ticker.upper()
    data_file = args.data_file
    
    # If no data file provided, try to find it automatically
    if not data_file:
        data_file = find_ticker_data_file(ticker)
        
        if not data_file:
            print(f"No data file found for {ticker}")
            print(f"Expected location: data/ticker_data/{ticker}/")
            print("Please provide a data file path or ensure ticker data exists.")
            return
        
        print(f"Auto-found data file: {data_file}")
    
    # Check if file exists
    if not os.path.exists(data_file):
        print(f"Data file not found: {data_file}")
        return
    
    # Run analysis
    results = analyze_separated_golden_gate(data_file, ticker)
    
    if results:
        print(f"\nSeparated Golden Gate analysis completed for {ticker}!")
        print(f"Positive Golden Gate: {results['positive_probability']:.1f}% probability")
        print(f"Negative Golden Gate: {results['negative_probability']:.1f}% probability")
        print(f"Patterns are analyzed completely separately - no cross-directional analysis")
        
        if results['positive_382_touches'] == 0 and results['negative_382_touches'] == 0:
            print(f"WARNING: No ±38.2% ATR touches found in the data period.")
            print(f"This could indicate low volatility or insufficient data.")

if __name__ == "__main__":
    main()