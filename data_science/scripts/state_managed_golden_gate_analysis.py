#!/usr/bin/env python3
"""
State-Managed Golden Gate Analysis - SPX 10-Minute Data
Implements proper OPEN/CLOSED state management:
- OPEN: When ±38.2% ATR level is first touched
- CLOSED: When ±61.8% ATR target is reached
- Maximum 2 OPEN states per day (one positive, one negative)
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, time, timedelta
import logging

def setup_logging():
    """Setup logging for the analysis"""
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'state_managed_golden_gate.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def calculate_atr_pine_script(high, low, close, period=14):
    """EXACT Pine Script ATR calculation using RMA methodology"""
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

def create_daily_bars_from_10min(data_10min):
    """Convert 10-minute data to daily bars for ATR calculation"""
    print("Converting 10-minute data to daily bars...")
    
    # Extract date only
    data_10min['trade_date'] = data_10min['date'].dt.date
    
    # Group by date and create OHLC
    daily_bars = data_10min.groupby('trade_date').agg({
        'open': 'first',
        'high': 'max', 
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).reset_index()
    
    daily_bars['date'] = pd.to_datetime(daily_bars['trade_date'])
    daily_bars = daily_bars.sort_values('date').reset_index(drop=True)
    
    print(f"Created {len(daily_bars)} daily bars from 10-minute data")
    return daily_bars

def calculate_atr_levels(previous_close, atr):
    """Calculate ATR-based levels using previous day's close and ATR"""
    return {
        'previous_close': previous_close,
        'trigger_upper': previous_close + atr * 0.382,
        'trigger_lower': previous_close - atr * 0.382,
        'target_upper': previous_close + atr * 0.618,
        'target_lower': previous_close - atr * 0.618
    }

def get_market_open_time():
    """Get market open time (9:30 AM)"""
    return time(9, 30)

def get_30min_time_buckets():
    """Get 30-minute time buckets from 9:30 AM to 4:00 PM"""
    buckets = []
    current_time = time(9, 30)  # Market open
    end_time = time(16, 0)      # Market close
    
    while current_time <= end_time:
        buckets.append(current_time)
        # Add 30 minutes
        current_datetime = datetime.combine(datetime.today(), current_time)
        current_datetime += timedelta(minutes=30)
        current_time = current_datetime.time()
    
    return buckets

def analyze_state_managed_scenarios(data_10min, daily_bars):
    """
    Analyze scenarios with proper state management:
    - OPEN: When ±38.2% is first touched (max 2 states per day)
    - CLOSED: When ±61.8% target is reached
    """
    print("\nAnalyzing State-Managed Golden Gate Scenarios...")
    
    # Calculate ATR for daily bars
    daily_bars['atr'] = calculate_atr_pine_script(
        daily_bars['high'], daily_bars['low'], daily_bars['close'], 14
    )
    
    # Remove first 14 days for proper ATR calculation
    daily_bars = daily_bars.iloc[14:].reset_index(drop=True)
    
    print(f"Using {len(daily_bars)} days after ATR warm-up")
    
    gap_open_results = []
    intraday_results = []
    time_buckets = get_30min_time_buckets()
    
    # Start from index 1 to have previous day data
    for i in range(1, len(daily_bars)):
        current_day = daily_bars.iloc[i]
        previous_day = daily_bars.iloc[i-1]
        
        # Calculate levels using previous day's close and ATR
        levels = calculate_atr_levels(previous_day['close'], previous_day['atr'])
        
        # Get current day's 10-minute data
        current_date = current_day['trade_date']
        day_10min = data_10min[data_10min['date'].dt.date == current_date].copy()
        
        if len(day_10min) == 0:
            continue
            
        day_10min = day_10min.sort_values('date').reset_index(drop=True)
        
        # Check for gap-open at market open (9:30 AM)
        market_open_data = day_10min[day_10min['date'].dt.time == get_market_open_time()]
        
        if len(market_open_data) == 0:
            continue
            
        open_price = market_open_data.iloc[0]['open']
        
        # Initialize state tracking
        positive_state_open = False
        negative_state_open = False
        positive_state_closed = False
        negative_state_closed = False
        
        # Check for gap-open scenarios
        gap_open_type = None
        if open_price > levels['trigger_upper']:
            gap_open_type = 'positive'
            positive_state_open = True
        elif open_price < levels['trigger_lower']:
            gap_open_type = 'negative'
            negative_state_open = True
        
        # Track gap-open completion if applicable
        if gap_open_type is not None:
            target_level = levels['target_upper'] if gap_open_type == 'positive' else levels['target_lower']
            completion_times = {}
            target_reached = False
            target_time = None
            
            for bucket_time in time_buckets:
                bucket_data = day_10min[day_10min['date'].dt.time <= bucket_time]
                
                if len(bucket_data) == 0:
                    completion_times[bucket_time.strftime('%H:%M')] = False
                    continue
                
                if gap_open_type == 'positive':
                    reached = bucket_data['high'].max() >= target_level
                else:
                    reached = bucket_data['low'].min() <= target_level
                
                completion_times[bucket_time.strftime('%H:%M')] = reached
                
                # Record first completion time
                if reached and not target_reached:
                    target_reached = True
                    target_time = bucket_time.strftime('%H:%M')
                    if gap_open_type == 'positive':
                        positive_state_closed = True
                    else:
                        negative_state_closed = True
            
            gap_open_results.append({
                'date': current_date,
                'gap_open_type': gap_open_type,
                'open_price': open_price,
                'previous_close': levels['previous_close'],
                'previous_atr': previous_day['atr'],
                'trigger_level': levels['trigger_upper'] if gap_open_type == 'positive' else levels['trigger_lower'],
                'target_level': target_level,
                'target_reached': target_reached,
                'target_time': target_time,
                **completion_times
            })
        
        # Process intraday triggers with state management
        for idx, row in day_10min.iterrows():
            current_time = row['date'].time()
            
            # Skip if we're at market open (already handled above)
            if current_time == get_market_open_time():
                continue
            
            # Check for positive trigger (only if not already open or closed)
            if (not positive_state_open and not positive_state_closed and 
                row['high'] >= levels['trigger_upper']):
                
                positive_state_open = True
                trigger_time = current_time
                
                # Track completion from this point
                remaining_data = day_10min[day_10min['date'] > row['date']]
                completion_by_remaining_time = {}
                target_reached = False
                target_completion_time = None
                
                trigger_datetime = datetime.combine(datetime.today(), trigger_time)
                
                for bucket_time in time_buckets:
                    bucket_datetime = datetime.combine(datetime.today(), bucket_time)
                    
                    # Only consider buckets after trigger time
                    if bucket_datetime <= trigger_datetime:
                        continue
                    
                    # Calculate remaining time in hours
                    remaining_minutes = (bucket_datetime - trigger_datetime).total_seconds() / 60
                    remaining_hours = remaining_minutes / 60
                    
                    # Get data up to this bucket time
                    bucket_data = remaining_data[remaining_data['date'].dt.time <= bucket_time]
                    
                    if len(bucket_data) == 0:
                        completion_by_remaining_time[f'{remaining_hours:.1f}h'] = False
                        continue
                    
                    reached = bucket_data['high'].max() >= levels['target_upper']
                    completion_by_remaining_time[f'{remaining_hours:.1f}h'] = reached
                    
                    # Record first completion
                    if reached and not target_reached:
                        target_reached = True
                        target_completion_time = f'{remaining_hours:.1f}h'
                        positive_state_closed = True
                        break
                
                intraday_results.append({
                    'date': current_date,
                    'trigger_time': trigger_time.strftime('%H:%M'),
                    'trigger_type': 'positive',
                    'trigger_price': row['high'],
                    'previous_close': levels['previous_close'],
                    'previous_atr': previous_day['atr'],
                    'trigger_level': levels['trigger_upper'],
                    'target_level': levels['target_upper'],
                    'target_reached': target_reached,
                    'completion_time': target_completion_time,
                    **completion_by_remaining_time
                })
            
            # Check for negative trigger (only if not already open or closed)
            if (not negative_state_open and not negative_state_closed and 
                row['low'] <= levels['trigger_lower']):
                
                negative_state_open = True
                trigger_time = current_time
                
                # Track completion from this point
                remaining_data = day_10min[day_10min['date'] > row['date']]
                completion_by_remaining_time = {}
                target_reached = False
                target_completion_time = None
                
                trigger_datetime = datetime.combine(datetime.today(), trigger_time)
                
                for bucket_time in time_buckets:
                    bucket_datetime = datetime.combine(datetime.today(), bucket_time)
                    
                    # Only consider buckets after trigger time
                    if bucket_datetime <= trigger_datetime:
                        continue
                    
                    # Calculate remaining time in hours
                    remaining_minutes = (bucket_datetime - trigger_datetime).total_seconds() / 60
                    remaining_hours = remaining_minutes / 60
                    
                    # Get data up to this bucket time
                    bucket_data = remaining_data[remaining_data['date'].dt.time <= bucket_time]
                    
                    if len(bucket_data) == 0:
                        completion_by_remaining_time[f'{remaining_hours:.1f}h'] = False
                        continue
                    
                    reached = bucket_data['low'].min() <= levels['target_lower']
                    completion_by_remaining_time[f'{remaining_hours:.1f}h'] = reached
                    
                    # Record first completion
                    if reached and not target_reached:
                        target_reached = True
                        target_completion_time = f'{remaining_hours:.1f}h'
                        negative_state_closed = True
                        break
                
                intraday_results.append({
                    'date': current_date,
                    'trigger_time': trigger_time.strftime('%H:%M'),
                    'trigger_type': 'negative',
                    'trigger_price': row['low'],
                    'previous_close': levels['previous_close'],
                    'previous_atr': previous_day['atr'],
                    'trigger_level': levels['trigger_lower'],
                    'target_level': levels['target_lower'],
                    'target_reached': target_reached,
                    'completion_time': target_completion_time,
                    **completion_by_remaining_time
                })
            
            # Check if targets are reached (close open states)
            if positive_state_open and not positive_state_closed:
                if row['high'] >= levels['target_upper']:
                    positive_state_closed = True
            
            if negative_state_open and not negative_state_closed:
                if row['low'] <= levels['target_lower']:
                    negative_state_closed = True
    
    return pd.DataFrame(gap_open_results), pd.DataFrame(intraday_results)

def main():
    """Run State-Managed Golden Gate Analysis"""
    setup_logging()
    
    print("=" * 120)
    print("STATE-MANAGED GOLDEN GATE ANALYSIS - SPX 10-MINUTE DATA")
    print("Proper OPEN/CLOSED state management: Max 2 OPEN states per day")
    print("=" * 120)
    
    # Load SPX 10-minute data
    data_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'ticker_data', 'SPX', '10min', 'SPX_10min_2004_to_2025.csv')
    
    if not os.path.exists(data_file):
        print(f"Error: SPX data file not found at {data_file}")
        return
    
    print(f"Loading SPX 10-minute data from: {data_file}")
    data_10min = pd.read_csv(data_file)
    data_10min['date'] = pd.to_datetime(data_10min['date'])
    
    print(f"Loaded {len(data_10min):,} 10-minute bars")
    print(f"Date range: {data_10min['date'].min()} to {data_10min['date'].max()}")
    
    # Create daily bars for ATR calculation
    daily_bars = create_daily_bars_from_10min(data_10min)
    
    # Run State-Managed Analysis
    gap_open_results, intraday_results = analyze_state_managed_scenarios(data_10min, daily_bars)
    print(f"Found {len(gap_open_results)} gap-open scenarios")
    print(f"Found {len(intraday_results)} intraday trigger scenarios")
    
    # Save results
    results_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'analysis_results')
    os.makedirs(results_dir, exist_ok=True)
    
    # Save detailed results
    gap_open_file = os.path.join(results_dir, 'state_managed_gap_open_results.csv')
    intraday_file = os.path.join(results_dir, 'state_managed_intraday_results.csv')
    
    gap_open_results.to_csv(gap_open_file, index=False)
    intraday_results.to_csv(intraday_file, index=False)
    
    print(f"\nResults saved:")
    print(f"Gap-Open Results: {gap_open_file}")
    print(f"Intraday Results: {intraday_file}")
    
    # Print summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS - STATE-MANAGED ANALYSIS")
    print("=" * 80)
    
    # Gap-Open Summary
    print("\nGAP-OPEN ANALYSIS:")
    for gap_type in ['positive', 'negative']:
        gap_subset = gap_open_results[gap_open_results['gap_open_type'] == gap_type]
        if len(gap_subset) > 0:
            success_rate = gap_subset['target_reached'].mean() * 100
            print(f"\n{gap_type.upper()} Gap-Opens:")
            print(f"  Total Events: {len(gap_subset)}")
            print(f"  Completions: {gap_subset['target_reached'].sum()}")
            print(f"  Success Rate: {success_rate:.1f}%")
    
    # Intraday Summary
    print("\nINTRADAY TRIGGER ANALYSIS (State-Managed):")
    for trigger_type in ['positive', 'negative']:
        trigger_subset = intraday_results[intraday_results['trigger_type'] == trigger_type]
        if len(trigger_subset) > 0:
            success_rate = trigger_subset['target_reached'].mean() * 100
            print(f"\n{trigger_type.upper()} Triggers:")
            print(f"  Total Events: {len(trigger_subset)}")
            print(f"  Completions: {trigger_subset['target_reached'].sum()}")
            print(f"  Success Rate: {success_rate:.1f}%")
    
    # Compare with original analysis
    print("\n" + "=" * 80)
    print("COMPARISON WITH ORIGINAL ANALYSIS")
    print("=" * 80)
    
    # Load original results for comparison
    original_intraday_file = os.path.join(results_dir, 'corrected_intraday_trigger_results.csv')
    if os.path.exists(original_intraday_file):
        original_intraday = pd.read_csv(original_intraday_file)
        print(f"\nOriginal Intraday Events: {len(original_intraday)}")
        print(f"State-Managed Intraday Events: {len(intraday_results)}")
        print(f"Reduction: {len(original_intraday) - len(intraday_results)} events ({((len(original_intraday) - len(intraday_results)) / len(original_intraday) * 100):.1f}%)")
        
        # Success rate comparison
        original_success = original_intraday['target_reached'].mean() * 100
        state_managed_success = intraday_results['target_reached'].mean() * 100 if len(intraday_results) > 0 else 0
        print(f"\nOriginal Success Rate: {original_success:.1f}%")
        print(f"State-Managed Success Rate: {state_managed_success:.1f}%")
        print(f"Improvement: {state_managed_success - original_success:.1f} percentage points")
    
    print("\n" + "=" * 80)
    print("STATE-MANAGED ANALYSIS COMPLETE")
    print("Maximum 2 OPEN states per day (one positive, one negative)")
    print("Proper OPEN/CLOSED state management implemented")
    print("=" * 80)

if __name__ == "__main__":
    main()