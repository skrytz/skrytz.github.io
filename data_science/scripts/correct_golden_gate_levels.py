#!/usr/bin/env python3
"""
Correct Golden Gate Levels Calculator
Uses PREVIOUS day's close and ATR to calculate NEXT day's Golden Gate levels
This matches the enhanced_golden_gate_analysis.py methodology
"""

import pandas as pd
import numpy as np
import os

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

def calculate_atr_levels(previous_close, atr):
    """Calculate ATR-based levels using previous day's close and ATR"""
    return {
        'previous_close': previous_close,
        'trigger_upper': previous_close + atr * 0.382,
        'trigger_lower': previous_close - atr * 0.382,
        'target_upper': previous_close + atr * 0.618,
        'target_lower': previous_close - atr * 0.618
    }

def main():
    """Show correct Golden Gate levels using previous day methodology"""
    print("CORRECT GOLDEN GATE LEVELS - USING PREVIOUS DAY'S CLOSE AND ATR")
    print("=" * 80)
    
    # Load SPX data
    data_file = os.path.join('..', '..', 'data', 'ticker_data', 'SPX', '10min', 'SPX_10min_2004_to_2025.csv')
    data_10min = pd.read_csv(data_file)
    data_10min['date'] = pd.to_datetime(data_10min['date'])
    data_10min['trade_date'] = data_10min['date'].dt.date

    # Create daily bars
    daily_bars = data_10min.groupby('trade_date').agg({
        'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'
    }).reset_index()
    daily_bars = daily_bars.sort_values('trade_date').reset_index(drop=True)

    # Calculate ATR
    daily_bars['atr'] = calculate_atr_pine_script(
        daily_bars['high'], daily_bars['low'], daily_bars['close'], 14
    )

    print("Trading Day | Prev Close | Prev ATR | +38.2%  | -38.2%  | +61.8%  | -61.8%")
    print("-" * 80)

    # Show last 6 days to get 5 trading day calculations
    last_6 = daily_bars.tail(6)
    
    for i in range(1, len(last_6)):
        current_day = last_6.iloc[i]
        previous_day = last_6.iloc[i-1]
        
        # Use previous day's close and ATR for current day's levels
        levels = calculate_atr_levels(previous_day['close'], previous_day['atr'])
        
        print(f"{str(current_day['trade_date']):<11} | {previous_day['close']:>10.2f} | {previous_day['atr']:>8.2f} | {levels['trigger_upper']:>7.2f} | {levels['trigger_lower']:>7.2f} | {levels['target_upper']:>7.2f} | {levels['target_lower']:>7.2f}")

    print()
    print("This methodology uses PREVIOUS day's close and ATR to calculate")
    print("the Golden Gate levels for the CURRENT trading day.")
    print()
    print("For June 11th verification:")
    
    # Get June 11th specific calculation
    june_11_idx = None
    june_10_idx = None
    
    for i, row in last_6.iterrows():
        if str(row['trade_date']) == '2025-06-11':
            june_11_idx = i
        elif str(row['trade_date']) == '2025-06-10':
            june_10_idx = i
    
    if june_11_idx is not None and june_10_idx is not None:
        june_11_day = last_6.loc[june_11_idx]
        june_10_day = last_6.loc[june_10_idx]
        
        levels = calculate_atr_levels(june_10_day['close'], june_10_day['atr'])
        
        print(f"June 11th levels based on June 10th close ({june_10_day['close']:.2f}) and ATR ({june_10_day['atr']:.2f}):")
        print(f"  +38.2% level: {levels['trigger_upper']:.2f}")
        print(f"  -38.2% level: {levels['trigger_lower']:.2f}")
        print(f"  +61.8% level: {levels['target_upper']:.2f}")
        print(f"  -61.8% level: {levels['target_lower']:.2f}")
        print()
        print(f"Your TradingView shows +38.2% as ~6067.81")
        print(f"My calculation shows +38.2% as {levels['trigger_upper']:.2f}")
        print(f"Difference: {abs(levels['trigger_upper'] - 6067.81):.2f} points")

if __name__ == "__main__":
    main()