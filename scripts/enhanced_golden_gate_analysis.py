#!/usr/bin/env python3
"""
Enhanced Golden Gate Analysis (2000-2025) - GAP-OPEN METHODOLOGY
Analyzes Golden Gate patterns with enhanced logic that distinguishes between:
1. Gap-open scenarios (stock opens beyond ATR levels)
2. Intraday trigger scenarios (stock touches ATR levels during trading)

New Definition:
- OPEN: Stock opens above +38.2% ATR (positive) or below -38.2% ATR (negative)
- COMPLETE: Price reaches +61.8% ATR (positive) or -61.8% ATR (negative)

Both gap-open and intraday scenarios can result in COMPLETE golden gates.
"""

import pandas as pd
import numpy as np
import os
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

def calculate_atr_levels(previous_close, atr):
    """Calculate ATR-based levels"""
    return {
        'previous_close': previous_close,
        'upper_382': previous_close + atr * 0.382,
        'upper_618': previous_close + atr * 0.618,
        'lower_382': previous_close - atr * 0.382,
        'lower_618': previous_close - atr * 0.618
    }

def check_level_touch(high, low, level):
    """Check if price touched a specific level during the day"""
    return low <= level <= high

def analyze_enhanced_golden_gate(current_day, levels):
    """
    Enhanced Golden Gate analysis with gap-open and intraday logic
    
    Returns:
    - gap_open_positive: Opened above +38.2% ATR
    - gap_open_negative: Opened below -38.2% ATR  
    - intraday_positive: Touched +38.2% during day (not gap)
    - intraday_negative: Touched -38.2% during day (not gap)
    - completed_positive: Reached +61.8% ATR
    - completed_negative: Reached -61.8% ATR
    """
    open_price = current_day['open']
    high = current_day['high']
    low = current_day['low']
    
    # Check if levels were touched during the day
    touched_upper_382 = check_level_touch(high, low, levels['upper_382'])
    touched_upper_618 = check_level_touch(high, low, levels['upper_618'])
    touched_lower_382 = check_level_touch(high, low, levels['lower_382'])
    touched_lower_618 = check_level_touch(high, low, levels['lower_618'])
    
    # Gap-open detection
    gap_open_positive = open_price > levels['upper_382']
    gap_open_negative = open_price < levels['lower_382']
    
    # Intraday trigger detection (touched but didn't gap open)
    intraday_positive = touched_upper_382 and not gap_open_positive
    intraday_negative = touched_lower_382 and not gap_open_negative
    
    # Completion detection
    completed_positive = touched_upper_618
    completed_negative = touched_lower_618
    
    return {
        'gap_open_positive': gap_open_positive,
        'gap_open_negative': gap_open_negative,
        'intraday_positive': intraday_positive,
        'intraday_negative': intraday_negative,
        'completed_positive': completed_positive,
        'completed_negative': completed_negative,
        'touched_upper_382': touched_upper_382,
        'touched_lower_382': touched_lower_382
    }

def analyze_ticker_data(ticker, data_file):
    """Analyze Enhanced Golden Gate patterns for a specific ticker"""
    print(f"\nAnalyzing {ticker} with ENHANCED GAP-OPEN methodology...")
    print(f"Loading: {data_file}")
    
    try:
        data = pd.read_csv(data_file)
        data['date'] = pd.to_datetime(data['date'])
        data = data.sort_values('date').reset_index(drop=True)
        
        print(f"  Loaded {len(data):,} records")
        print(f"  Date range: {data['date'].min().strftime('%Y-%m-%d')} to {data['date'].max().strftime('%Y-%m-%d')}")
        
        # Calculate ATR using corrected Pine Script methodology
        data['atr'] = calculate_atr_pine_script(data['high'], data['low'], data['close'], 14)
        data = data.dropna(subset=['atr']).reset_index(drop=True)
        
        print(f"  Using {len(data):,} records after ATR calculation")
        
        # Analyze by year for detailed breakdown
        data['year'] = data['date'].dt.year
        years = sorted(data['year'].unique())
        
        results = []
        
        # Totals for overall statistics
        total_gap_open_positive = 0
        total_gap_open_positive_complete = 0
        total_gap_open_negative = 0
        total_gap_open_negative_complete = 0
        total_intraday_positive = 0
        total_intraday_positive_complete = 0
        total_intraday_negative = 0
        total_intraday_negative_complete = 0
        total_trading_days = 0
        
        # Analyze each year
        for year in years:
            year_data = data[data['year'] == year].reset_index(drop=True)
            if len(year_data) < 2:
                continue
                
            year_result = analyze_year_subset(year_data, year, ticker)
            if year_result:
                results.append(year_result)
                total_gap_open_positive += year_result['gap_open_positive']
                total_gap_open_positive_complete += year_result['gap_open_positive_complete']
                total_gap_open_negative += year_result['gap_open_negative']
                total_gap_open_negative_complete += year_result['gap_open_negative_complete']
                total_intraday_positive += year_result['intraday_positive']
                total_intraday_positive_complete += year_result['intraday_positive_complete']
                total_intraday_negative += year_result['intraday_negative']
                total_intraday_negative_complete += year_result['intraday_negative_complete']
                total_trading_days += year_result['total_days']
        
        # Calculate overall statistics
        gap_open_positive_rate = (total_gap_open_positive_complete / total_gap_open_positive * 100) if total_gap_open_positive > 0 else 0
        gap_open_negative_rate = (total_gap_open_negative_complete / total_gap_open_negative * 100) if total_gap_open_negative > 0 else 0
        intraday_positive_rate = (total_intraday_positive_complete / total_intraday_positive * 100) if total_intraday_positive > 0 else 0
        intraday_negative_rate = (total_intraday_negative_complete / total_intraday_negative * 100) if total_intraday_negative > 0 else 0
        
        # Combined rates
        total_positive_triggers = total_gap_open_positive + total_intraday_positive
        total_positive_complete = total_gap_open_positive_complete + total_intraday_positive_complete
        total_negative_triggers = total_gap_open_negative + total_intraday_negative
        total_negative_complete = total_gap_open_negative_complete + total_intraday_negative_complete
        
        combined_positive_rate = (total_positive_complete / total_positive_triggers * 100) if total_positive_triggers > 0 else 0
        combined_negative_rate = (total_negative_complete / total_negative_triggers * 100) if total_negative_triggers > 0 else 0
        
        return {
            'ticker': ticker,
            'total_trading_days': total_trading_days,
            'years_analyzed': len(results),
            'date_range': f"{min(r['year'] for r in results)}-{max(r['year'] for r in results)}",
            
            # Gap-open statistics
            'gap_open_positive': total_gap_open_positive,
            'gap_open_positive_complete': total_gap_open_positive_complete,
            'gap_open_positive_rate': round(gap_open_positive_rate, 1),
            'gap_open_negative': total_gap_open_negative,
            'gap_open_negative_complete': total_gap_open_negative_complete,
            'gap_open_negative_rate': round(gap_open_negative_rate, 1),
            
            # Intraday statistics
            'intraday_positive': total_intraday_positive,
            'intraday_positive_complete': total_intraday_positive_complete,
            'intraday_positive_rate': round(intraday_positive_rate, 1),
            'intraday_negative': total_intraday_negative,
            'intraday_negative_complete': total_intraday_negative_complete,
            'intraday_negative_rate': round(intraday_negative_rate, 1),
            
            # Combined statistics
            'combined_positive_rate': round(combined_positive_rate, 1),
            'combined_negative_rate': round(combined_negative_rate, 1),
            'negative_advantage': round(combined_negative_rate - combined_positive_rate, 1),
            
            'yearly_results': results
        }
        
    except Exception as e:
        print(f"  Error analyzing {ticker}: {e}")
        return None

def analyze_year_subset(year_data, year, ticker):
    """Analyze Enhanced Golden Gate patterns for a specific year subset"""
    if len(year_data) < 2:
        return None
    
    # Counters for different scenarios
    gap_open_positive = 0
    gap_open_positive_complete = 0
    gap_open_negative = 0
    gap_open_negative_complete = 0
    intraday_positive = 0
    intraday_positive_complete = 0
    intraday_negative = 0
    intraday_negative_complete = 0
    
    for i in range(1, len(year_data)):
        current_day = year_data.iloc[i]
        previous_day = year_data.iloc[i-1]
        
        # Use previous day's ATR (period_index=1 in Pine Script)
        previous_atr = previous_day['atr'] if i > 0 else current_day['atr']
        levels = calculate_atr_levels(previous_day['close'], previous_atr)
        
        # Analyze the day with enhanced logic
        analysis = analyze_enhanced_golden_gate(current_day, levels)
        
        # Count gap-open scenarios
        if analysis['gap_open_positive']:
            gap_open_positive += 1
            if analysis['completed_positive']:
                gap_open_positive_complete += 1
                
        if analysis['gap_open_negative']:
            gap_open_negative += 1
            if analysis['completed_negative']:
                gap_open_negative_complete += 1
        
        # Count intraday scenarios
        if analysis['intraday_positive']:
            intraday_positive += 1
            if analysis['completed_positive']:
                intraday_positive_complete += 1
                
        if analysis['intraday_negative']:
            intraday_negative += 1
            if analysis['completed_negative']:
                intraday_negative_complete += 1
    
    return {
        'ticker': ticker,
        'year': year,
        'total_days': len(year_data) - 1,
        
        # Gap-open results
        'gap_open_positive': gap_open_positive,
        'gap_open_positive_complete': gap_open_positive_complete,
        'gap_open_positive_rate': (gap_open_positive_complete / gap_open_positive * 100) if gap_open_positive > 0 else 0,
        'gap_open_negative': gap_open_negative,
        'gap_open_negative_complete': gap_open_negative_complete,
        'gap_open_negative_rate': (gap_open_negative_complete / gap_open_negative * 100) if gap_open_negative > 0 else 0,
        
        # Intraday results
        'intraday_positive': intraday_positive,
        'intraday_positive_complete': intraday_positive_complete,
        'intraday_positive_rate': (intraday_positive_complete / intraday_positive * 100) if intraday_positive > 0 else 0,
        'intraday_negative': intraday_negative,
        'intraday_negative_complete': intraday_negative_complete,
        'intraday_negative_rate': (intraday_negative_complete / intraday_negative * 100) if intraday_negative > 0 else 0,
        
        'start_date': year_data['date'].min(),
        'end_date': year_data['date'].max()
    }

def main():
    """Run ENHANCED GAP-OPEN analysis on multiple tickers"""
    print("=" * 120)
    print("ENHANCED GOLDEN GATE ANALYSIS (2000-2025)")
    print("SPY & QQQ Historical Analysis - GAP-OPEN METHODOLOGY")
    print("Distinguishes between gap-open scenarios and intraday triggers")
    print("OPEN: Stock opens beyond ±38.2% ATR | COMPLETE: Reaches ±61.8% ATR")
    print("=" * 120)
    
    # Define tickers and their data files
    tickers = {
        'SPY': 'data/ticker_data/SPY/SPY_2000_to_present_IBKR.csv',
        'QQQ': 'data/ticker_data/QQQ/QQQ_2000_to_present_IBKR.csv'
    }
    
    all_results = {}
    
    # Analyze each ticker
    for ticker, data_file in tickers.items():
        if not os.path.exists(data_file):
            print(f"Data file not found for {ticker}: {data_file}")
            continue
            
        result = analyze_ticker_data(ticker, data_file)
        if result:
            all_results[ticker] = result
    
    if not all_results:
        print("No data could be analyzed!")
        return
    
    # Display comparison results
    print("\n" + "=" * 140)
    print("ENHANCED GAP-OPEN METHODOLOGY COMPARISON SUMMARY")
    print("=" * 140)
    
    print(f"{'Ticker':<8} {'Days':<8} {'Gap+ Trig':<10} {'Gap+ Comp':<10} {'Gap+ %':<8} {'Gap- Trig':<10} {'Gap- Comp':<10} {'Gap- %':<8} {'Intra+ Trig':<11} {'Intra+ Comp':<11} {'Intra+ %':<9} {'Intra- Trig':<11} {'Intra- Comp':<11} {'Intra- %':<9}")
    print("-" * 140)
    
    for ticker, result in all_results.items():
        print(f"{ticker:<8} {result['total_trading_days']:<8} "
              f"{result['gap_open_positive']:<10} {result['gap_open_positive_complete']:<10} "
              f"{result['gap_open_positive_rate']:<7.1f}% {result['gap_open_negative']:<10} "
              f"{result['gap_open_negative_complete']:<10} {result['gap_open_negative_rate']:<7.1f}% "
              f"{result['intraday_positive']:<11} {result['intraday_positive_complete']:<11} "
              f"{result['intraday_positive_rate']:<8.1f}% {result['intraday_negative']:<11} "
              f"{result['intraday_negative_complete']:<11} {result['intraday_negative_rate']:<8.1f}%")
    
    # Combined rates summary
    print("\n" + "=" * 80)
    print("COMBINED RATES SUMMARY")
    print("=" * 80)
    print(f"{'Ticker':<8} {'Combined Pos %':<15} {'Combined Neg %':<15} {'Neg Advantage':<15}")
    print("-" * 80)
    
    for ticker, result in all_results.items():
        print(f"{ticker:<8} {result['combined_positive_rate']:<14.1f}% "
              f"{result['combined_negative_rate']:<14.1f}% "
              f"{result['negative_advantage']:>+12.1f}%")
    
    # Detailed breakdown for each ticker
    for ticker, result in all_results.items():
        print(f"\n{ticker} ENHANCED GOLDEN GATE ANALYSIS:")
        print("=" * 100)
        print(f"Total trading days analyzed: {result['total_trading_days']:,}")
        print(f"Years covered: {result['years_analyzed']} ({result['date_range']})")
        print()
        
        print(f"GAP-OPEN SCENARIOS:")
        print(f"  Positive gap-opens (opened above +38.2% ATR): {result['gap_open_positive']:,}")
        print(f"  Positive gap-open completions (reached +61.8%): {result['gap_open_positive_complete']:,}")
        print(f"  Positive gap-open completion rate: {result['gap_open_positive_rate']}%")
        print()
        print(f"  Negative gap-opens (opened below -38.2% ATR): {result['gap_open_negative']:,}")
        print(f"  Negative gap-open completions (reached -61.8%): {result['gap_open_negative_complete']:,}")
        print(f"  Negative gap-open completion rate: {result['gap_open_negative_rate']}%")
        print()
        
        print(f"INTRADAY TRIGGER SCENARIOS:")
        print(f"  Positive intraday triggers (touched +38.2% during day): {result['intraday_positive']:,}")
        print(f"  Positive intraday completions (reached +61.8%): {result['intraday_positive_complete']:,}")
        print(f"  Positive intraday completion rate: {result['intraday_positive_rate']}%")
        print()
        print(f"  Negative intraday triggers (touched -38.2% during day): {result['intraday_negative']:,}")
        print(f"  Negative intraday completions (reached -61.8%): {result['intraday_negative_complete']:,}")
        print(f"  Negative intraday completion rate: {result['intraday_negative_rate']}%")
        print()
        
        print(f"COMBINED ANALYSIS:")
        print(f"  Overall positive completion rate: {result['combined_positive_rate']}%")
        print(f"  Overall negative completion rate: {result['combined_negative_rate']}%")
        print(f"  Negative momentum advantage: {result['negative_advantage']} percentage points")
        
        if result['combined_positive_rate'] > 0:
            relative_advantage = (result['combined_negative_rate']/result['combined_positive_rate']-1)*100
            print(f"  Relative negative advantage: {relative_advantage:.1f}%")
        
        # Gap vs Intraday comparison
        gap_pos_rate = result['gap_open_positive_rate']
        intra_pos_rate = result['intraday_positive_rate']
        gap_neg_rate = result['gap_open_negative_rate']
        intra_neg_rate = result['intraday_negative_rate']
        
        print()
        print(f"GAP-OPEN vs INTRADAY COMPARISON:")
        if gap_pos_rate > 0 and intra_pos_rate > 0:
            pos_diff = gap_pos_rate - intra_pos_rate
            print(f"  Positive: Gap-open {gap_pos_rate:.1f}% vs Intraday {intra_pos_rate:.1f}% (Gap advantage: {pos_diff:+.1f}%)")
        if gap_neg_rate > 0 and intra_neg_rate > 0:
            neg_diff = gap_neg_rate - intra_neg_rate
            print(f"  Negative: Gap-open {gap_neg_rate:.1f}% vs Intraday {intra_neg_rate:.1f}% (Gap advantage: {neg_diff:+.1f}%)")
    
    # Save results
    os.makedirs("data/analysis_results", exist_ok=True)
    
    # Save individual ticker results
    for ticker, result in all_results.items():
        yearly_df = pd.DataFrame(result['yearly_results'])
        yearly_file = f"data/analysis_results/{ticker}_enhanced_golden_gate_2000_2025.csv"
        yearly_df.to_csv(yearly_file, index=False)
        print(f"\n{ticker} enhanced yearly results saved to: {yearly_file}")
    
    # Save comparison summary
    summary_data = []
    for ticker, result in all_results.items():
        summary_data.append({
            'ticker': ticker,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'methodology': 'Enhanced Gap-Open Analysis',
            'total_trading_days': result['total_trading_days'],
            'years_analyzed': result['years_analyzed'],
            'date_range': result['date_range'],
            
            # Gap-open data
            'gap_open_positive': result['gap_open_positive'],
            'gap_open_positive_complete': result['gap_open_positive_complete'],
            'gap_open_positive_rate': result['gap_open_positive_rate'],
            'gap_open_negative': result['gap_open_negative'],
            'gap_open_negative_complete': result['gap_open_negative_complete'],
            'gap_open_negative_rate': result['gap_open_negative_rate'],
            
            # Intraday data
            'intraday_positive': result['intraday_positive'],
            'intraday_positive_complete': result['intraday_positive_complete'],
            'intraday_positive_rate': result['intraday_positive_rate'],
            'intraday_negative': result['intraday_negative'],
            'intraday_negative_complete': result['intraday_negative_complete'],
            'intraday_negative_rate': result['intraday_negative_rate'],
            
            # Combined data
            'combined_positive_rate': result['combined_positive_rate'],
            'combined_negative_rate': result['combined_negative_rate'],
            'negative_advantage': result['negative_advantage']
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_file = "data/analysis_results/enhanced_golden_gate_summary.csv"
    summary_df.to_csv(summary_file, index=False)
    print(f"\nEnhanced Golden Gate summary saved to: {summary_file}")
    
    print("\n" + "=" * 120)
    print("ENHANCED GAP-OPEN GOLDEN GATE ANALYSIS COMPLETED SUCCESSFULLY!")
    print("This analysis distinguishes between gap-open and intraday trigger scenarios")
    print("=" * 120)
    
    return all_results

if __name__ == "__main__":
    main()