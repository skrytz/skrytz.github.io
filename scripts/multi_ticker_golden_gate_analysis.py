#!/usr/bin/env python3
"""
Multi-Ticker Golden Gate Analysis (2000-2025) - CORRECTED with Saty's exact methodology
Analyzes Golden Gate patterns for multiple tickers (SPY, QQQ) using complete IBKR datasets

IMPORTANT: Uses previous day's ATR for calculating today's levels (period_index=1 in Pine Script)
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

def analyze_ticker_data(ticker, data_file):
    """Analyze Golden Gate patterns for a specific ticker"""
    print(f"\nAnalyzing {ticker}...")
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
        total_positive_382 = 0
        total_positive_gates = 0
        total_negative_382 = 0
        total_negative_gates = 0
        total_trading_days = 0
        
        # Analyze each year
        for year in years:
            year_data = data[data['year'] == year].reset_index(drop=True)
            if len(year_data) < 2:
                continue
                
            year_result = analyze_year_subset(year_data, year, ticker)
            if year_result:
                results.append(year_result)
                total_positive_382 += year_result['positive_382_touches']
                total_positive_gates += year_result['positive_golden_gates']
                total_negative_382 += year_result['negative_382_touches']
                total_negative_gates += year_result['negative_golden_gates']
                total_trading_days += year_result['total_days']
        
        # Calculate overall statistics
        overall_positive_prob = (total_positive_gates / total_positive_382 * 100) if total_positive_382 > 0 else 0
        overall_negative_prob = (total_negative_gates / total_negative_382 * 100) if total_negative_382 > 0 else 0
        overall_difference = overall_negative_prob - overall_positive_prob
        
        return {
            'ticker': ticker,
            'total_trading_days': total_trading_days,
            'years_analyzed': len(results),
            'date_range': f"{min(r['year'] for r in results)}-{max(r['year'] for r in results)}",
            'positive_382_touches': total_positive_382,
            'positive_golden_gates': total_positive_gates,
            'positive_probability': round(overall_positive_prob, 1),
            'negative_382_touches': total_negative_382,
            'negative_golden_gates': total_negative_gates,
            'negative_probability': round(overall_negative_prob, 1),
            'negative_advantage': round(overall_difference, 1),
            'yearly_results': results
        }
        
    except Exception as e:
        print(f"  Error analyzing {ticker}: {e}")
        return None

def analyze_year_subset(year_data, year, ticker):
    """Analyze Golden Gate patterns for a specific year subset"""
    if len(year_data) < 2:
        return None
        
    positive_382_touches = 0
    positive_golden_gates = 0
    negative_382_touches = 0
    negative_golden_gates = 0
    
    for i in range(1, len(year_data)):
        current_day = year_data.iloc[i]
        previous_day = year_data.iloc[i-1]
        
        # CORRECTED: Use previous day's ATR (period_index=1 in Pine Script)
        previous_atr = previous_day['atr'] if i > 0 else current_day['atr']
        levels = calculate_atr_levels(previous_day['close'], previous_atr)
        
        # Positive analysis
        touched_positive_382 = check_level_touch(current_day['high'], current_day['low'], levels['upper_382'])
        if touched_positive_382:
            positive_382_touches += 1
            touched_positive_618 = check_level_touch(current_day['high'], current_day['low'], levels['upper_618'])
            
            # Exclude reverse patterns
            opened_above_618 = current_day['open'] > levels['upper_618']
            if opened_above_618 and touched_positive_618:
                touched_positive_618 = False
                
            if touched_positive_618:
                positive_golden_gates += 1
        
        # Negative analysis
        touched_negative_382 = check_level_touch(current_day['high'], current_day['low'], levels['lower_382'])
        if touched_negative_382:
            negative_382_touches += 1
            touched_negative_618 = check_level_touch(current_day['high'], current_day['low'], levels['lower_618'])
            
            # Exclude reverse patterns
            opened_below_618 = current_day['open'] < levels['lower_618']
            if opened_below_618 and touched_negative_618:
                touched_negative_618 = False
                
            if touched_negative_618:
                negative_golden_gates += 1
    
    return {
        'ticker': ticker,
        'year': year,
        'total_days': len(year_data) - 1,
        'positive_382_touches': positive_382_touches,
        'positive_golden_gates': positive_golden_gates,
        'positive_probability': (positive_golden_gates / positive_382_touches * 100) if positive_382_touches > 0 else 0,
        'negative_382_touches': negative_382_touches,
        'negative_golden_gates': negative_golden_gates,
        'negative_probability': (negative_golden_gates / negative_382_touches * 100) if negative_382_touches > 0 else 0,
        'start_date': year_data['date'].min(),
        'end_date': year_data['date'].max()
    }

def main():
    """Run comprehensive analysis on multiple tickers"""
    print("=" * 100)
    print("MULTI-TICKER GOLDEN GATE ANALYSIS (2000-2025)")
    print("SPY & QQQ Historical Analysis - CORRECTED with Saty's Exact Methodology")
    print("Using previous day's ATR for today's levels (period_index=1)")
    print("=" * 100)
    
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
    print("\n" + "=" * 100)
    print("MULTI-TICKER COMPARISON SUMMARY")
    print("=" * 100)
    
    print(f"{'Ticker':<8} {'Days':<8} {'Years':<7} {'Pos 382':<9} {'Pos Gates':<11} {'Pos %':<8} {'Neg 382':<9} {'Neg Gates':<11} {'Neg %':<8} {'Advantage':<10}")
    print("-" * 100)
    
    for ticker, result in all_results.items():
        print(f"{ticker:<8} {result['total_trading_days']:<8} {result['years_analyzed']:<7} "
              f"{result['positive_382_touches']:<9} {result['positive_golden_gates']:<11} "
              f"{result['positive_probability']:<7.1f}% {result['negative_382_touches']:<9} "
              f"{result['negative_golden_gates']:<11} {result['negative_probability']:<7.1f}% "
              f"{result['negative_advantage']:>+7.1f}%")
    
    # Detailed breakdown for each ticker
    for ticker, result in all_results.items():
        print(f"\n{ticker} DETAILED ANALYSIS:")
        print("=" * 80)
        print(f"Total trading days analyzed: {result['total_trading_days']:,}")
        print(f"Years covered: {result['years_analyzed']} ({result['date_range']})")
        print()
        print(f"POSITIVE GOLDEN GATE PATTERN:")
        print(f"  Days with +38.2% ATR touches: {result['positive_382_touches']:,}")
        print(f"  Days with +61.8% Golden Gate completion: {result['positive_golden_gates']:,}")
        print(f"  Positive Golden Gate Probability: {result['positive_probability']}%")
        print()
        print(f"NEGATIVE GOLDEN GATE PATTERN:")
        print(f"  Days with -38.2% ATR touches: {result['negative_382_touches']:,}")
        print(f"  Days with -61.8% Golden Gate completion: {result['negative_golden_gates']:,}")
        print(f"  Negative Golden Gate Probability: {result['negative_probability']}%")
        print()
        print(f"KEY FINDING:")
        print(f"  Negative momentum is {result['negative_advantage']} percentage points stronger")
        if result['positive_probability'] > 0:
            relative_advantage = (result['negative_probability']/result['positive_probability']-1)*100
            print(f"  This represents a {relative_advantage:.1f}% relative advantage for negative patterns")
    
    # Save results
    os.makedirs("data/analysis_results", exist_ok=True)
    
    # Save individual ticker results
    for ticker, result in all_results.items():
        yearly_df = pd.DataFrame(result['yearly_results'])
        yearly_file = f"data/analysis_results/{ticker}_golden_gate_2000_2025_corrected.csv"
        yearly_df.to_csv(yearly_file, index=False)
        print(f"\n{ticker} yearly results saved to: {yearly_file}")
    
    # Save comparison summary
    summary_data = []
    for ticker, result in all_results.items():
        summary_data.append({
            'ticker': ticker,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_trading_days': result['total_trading_days'],
            'years_analyzed': result['years_analyzed'],
            'date_range': result['date_range'],
            'positive_382_touches': result['positive_382_touches'],
            'positive_golden_gates': result['positive_golden_gates'],
            'positive_probability': result['positive_probability'],
            'negative_382_touches': result['negative_382_touches'],
            'negative_golden_gates': result['negative_golden_gates'],
            'negative_probability': result['negative_probability'],
            'negative_advantage': result['negative_advantage'],
            'methodology': 'Corrected with period_index=1 (previous day ATR)'
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_file = "data/analysis_results/multi_ticker_golden_gate_summary.csv"
    summary_df.to_csv(summary_file, index=False)
    print(f"\nMulti-ticker summary saved to: {summary_file}")
    
    print("\n" + "=" * 100)
    print("MULTI-TICKER ANALYSIS COMPLETED SUCCESSFULLY!")
    print("=" * 100)
    
    return all_results

if __name__ == "__main__":
    main()