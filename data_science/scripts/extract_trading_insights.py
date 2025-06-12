#!/usr/bin/env python3
"""
Extract Actionable Trading Insights from Corrected Intraday Golden Gate Analysis
Answer questions like: "If it doesn't reach by 2pm EST, don't be hopeful"
"""

import pandas as pd
import numpy as np
import os

def analyze_corrected_gap_open_insights():
    """Analyze corrected gap-open data for actionable trading insights"""
    print("=" * 80)
    print("CORRECTED GAP-OPEN TRADING INSIGHTS")
    print("=" * 80)
    
    # Load corrected gap-open data
    gap_file = os.path.join('..', '..', 'data', 'analysis_results', 'corrected_intraday_gap_open_results.csv')
    gap_df = pd.read_csv(gap_file)
    
    print(f"Analyzing {len(gap_df)} corrected gap-open scenarios...")
    
    # Time columns for analysis (30-minute buckets)
    time_cols = ['09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00']
    
    insights = {}
    
    # Analyze by gap type
    for gap_type in ['positive', 'negative']:
        subset = gap_df[gap_df['gap_open_type'] == gap_type].copy()
        
        if len(subset) == 0:
            continue
            
        print(f"\n{gap_type.upper()} GAP-OPENS ({len(subset)} events):")
        
        # Calculate completion rates by time
        completion_rates = {}
        for time_col in time_cols:
            if time_col in subset.columns:
                completion_rate = subset[time_col].mean() * 100
                completion_rates[time_col] = completion_rate
                print(f"  {time_col}: {completion_rate:.1f}%")
        
        # Key insights for trading decisions
        print(f"\n  CRITICAL TRADING INSIGHTS:")
        
        # 2 PM EST analysis (14:00) - Key decision point
        if '14:00' in completion_rates and '16:00' in completion_rates:
            rate_2pm = completion_rates['14:00']
            rate_final = completion_rates['16:00']
            late_day_improvement = rate_final - rate_2pm
            
            print(f"  • 2:00 PM Decision Point:")
            print(f"    - Completion rate by 2:00 PM: {rate_2pm:.1f}%")
            print(f"    - Final completion rate: {rate_final:.1f}%")
            print(f"    - Late-day improvement: {late_day_improvement:+.1f}%")
            
            if late_day_improvement < 3:
                print(f"    ⚠️  RULE: If {gap_type} gap not completed by 2:00 PM, only {late_day_improvement:.1f}% additional chance")
            else:
                print(f"    ✅ RULE: {gap_type} gaps can still improve {late_day_improvement:.1f}% after 2:00 PM")
        
        # Early momentum analysis (first hour)
        if '09:30' in completion_rates and '10:30' in completion_rates:
            rate_930 = completion_rates['09:30']
            rate_1030 = completion_rates['10:30']
            early_momentum = rate_1030 - rate_930
            
            print(f"  • Early Momentum (9:30-10:30 AM):")
            print(f"    - Change in first hour: {early_momentum:+.1f}%")
            
            if early_momentum > 5:
                print(f"    ✅ RULE: {gap_type} gaps gain momentum in first hour (+{early_momentum:.1f}%)")
            elif early_momentum < -3:
                print(f"    ⚠️  RULE: {gap_type} gaps fade early (-{abs(early_momentum):.1f}% in first hour)")
        
        # Lunch hour effect (12:00-13:00)
        if '12:00' in completion_rates and '13:00' in completion_rates:
            rate_12pm = completion_rates['12:00']
            rate_1pm = completion_rates['13:00']
            lunch_effect = rate_1pm - rate_12pm
            
            print(f"  • Lunch Hour Effect (12:00-1:00 PM):")
            print(f"    - Change during lunch: {lunch_effect:+.1f}%")
            
            if abs(lunch_effect) > 2:
                direction = "accelerates" if lunch_effect > 0 else "stalls"
                print(f"    📊 RULE: {gap_type} gaps {direction} during lunch hour ({lunch_effect:+.1f}%)")
        
        # Overall success rate
        overall_success = subset['target_reached'].mean() * 100
        print(f"  • Overall Success Rate: {overall_success:.1f}%")
        
        insights[gap_type] = {
            'total_events': len(subset),
            'overall_success': overall_success,
            'completion_rates': completion_rates
        }
    
    return insights

def analyze_corrected_intraday_insights():
    """Analyze corrected intraday trigger data for actionable insights"""
    print("\n" + "=" * 80)
    print("CORRECTED INTRADAY TRIGGER TRADING INSIGHTS")
    print("=" * 80)
    
    # Load corrected intraday data
    intraday_file = os.path.join('..', '..', 'data', 'analysis_results', 'corrected_intraday_trigger_results.csv')
    intraday_df = pd.read_csv(intraday_file)
    
    print(f"Analyzing {len(intraday_df)} corrected intraday trigger events...")
    
    insights = {}
    
    # Analyze by trigger type
    for trigger_type in ['positive', 'negative']:
        subset = intraday_df[intraday_df['trigger_type'] == trigger_type].copy()
        
        if len(subset) == 0:
            continue
            
        print(f"\n{trigger_type.upper()} INTRADAY TRIGGERS ({len(subset)} events):")
        
        # Convert trigger_time to hour for analysis
        subset['trigger_hour'] = pd.to_datetime(subset['trigger_time'], format='%H:%M').dt.hour
        
        # Analyze success rates by trigger hour
        hourly_success = subset.groupby('trigger_hour')['target_reached'].agg(['count', 'mean']).reset_index()
        hourly_success.columns = ['hour', 'count', 'success_rate']
        hourly_success['success_rate'] *= 100
        
        print(f"  SUCCESS RATES BY TRIGGER HOUR:")
        best_hour = None
        best_rate = 0
        worst_hour = None
        worst_rate = 100
        
        for _, row in hourly_success.iterrows():
            if row['count'] >= 50:  # Only consider hours with significant data
                print(f"  • {row['hour']:02d}:00 hour: {row['success_rate']:.1f}% ({int(row['count'])} events)")
                
                if row['success_rate'] > best_rate:
                    best_rate = row['success_rate']
                    best_hour = row['hour']
                if row['success_rate'] < worst_rate:
                    worst_rate = row['success_rate']
                    worst_hour = row['hour']
        
        if best_hour and worst_hour:
            print(f"\n  TIMING INSIGHTS:")
            print(f"  • Best trigger hour: {best_hour:02d}:00 ({best_rate:.1f}% success)")
            print(f"  • Worst trigger hour: {worst_hour:02d}:00 ({worst_rate:.1f}% success)")
            print(f"  • Timing advantage: {best_rate - worst_rate:.1f}%")
        
        # Morning vs Afternoon analysis
        morning_triggers = subset[subset['trigger_hour'] < 12]
        afternoon_triggers = subset[subset['trigger_hour'] >= 12]
        
        if len(morning_triggers) > 0 and len(afternoon_triggers) > 0:
            morning_success = morning_triggers['target_reached'].mean() * 100
            afternoon_success = afternoon_triggers['target_reached'].mean() * 100
            
            print(f"\n  MORNING vs AFTERNOON:")
            print(f"  • Morning triggers (9:30-12:00): {morning_success:.1f}% success")
            print(f"  • Afternoon triggers (12:00-16:00): {afternoon_success:.1f}% success")
            print(f"  • Morning advantage: {morning_success - afternoon_success:+.1f}%")
            
            if abs(morning_success - afternoon_success) > 5:
                better_time = "morning" if morning_success > afternoon_success else "afternoon"
                advantage = abs(morning_success - afternoon_success)
                print(f"  ⚠️  RULE: {trigger_type} triggers work {advantage:.1f}% better in {better_time}")
        
        # Overall success rate
        overall_success = subset['target_reached'].mean() * 100
        print(f"  • Overall Success Rate: {overall_success:.1f}%")
        
        insights[trigger_type] = {
            'total_events': len(subset),
            'overall_success': overall_success,
            'morning_success': morning_success if 'morning_success' in locals() else None,
            'afternoon_success': afternoon_success if 'afternoon_success' in locals() else None
        }
    
    return insights

def generate_actionable_rules(gap_insights, intraday_insights):
    """Generate actionable trading rules based on corrected insights"""
    print("\n" + "=" * 80)
    print("ACTIONABLE TRADING RULES - CORRECTED ANALYSIS")
    print("=" * 80)
    
    rules = []
    
    print("\n🎯 GAP-OPEN TRADING RULES:")
    
    for gap_type in ['positive', 'negative']:
        if gap_type in gap_insights:
            data = gap_insights[gap_type]
            rates = data['completion_rates']
            
            print(f"\n{gap_type.upper()} Gap-Opens:")
            
            # Rule 1: 2 PM cutoff rule
            if '14:00' in rates and '16:00' in rates:
                rate_2pm = rates['14:00']
                rate_final = rates['16:00']
                improvement = rate_final - rate_2pm
                
                if improvement < 3:
                    rule = f"RULE: {gap_type} gaps - if not completed by 2:00 PM ({rate_2pm:.1f}%), only {improvement:.1f}% additional chance"
                    print(f"   ⚠️  {rule}")
                    rules.append(rule)
                else:
                    rule = f"RULE: {gap_type} gaps can still improve {improvement:.1f}% after 2:00 PM"
                    print(f"   ✅ {rule}")
                    rules.append(rule)
            
            # Rule 2: Overall success guidance
            overall = data['overall_success']
            if overall > 70:
                rule = f"RULE: {gap_type} gap-opens have {overall:.1f}% success - high probability trades"
                print(f"   ✅ {rule}")
            elif overall < 50:
                rule = f"RULE: {gap_type} gap-opens have {overall:.1f}% success - use tight stops"
                print(f"   ⚠️  {rule}")
            else:
                rule = f"RULE: {gap_type} gap-opens have {overall:.1f}% success - moderate probability"
                print(f"   📊 {rule}")
            rules.append(rule)
    
    print(f"\n🎯 INTRADAY TRIGGER RULES:")
    
    for trigger_type in ['positive', 'negative']:
        if trigger_type in intraday_insights:
            data = intraday_insights[trigger_type]
            
            print(f"\n{trigger_type.upper()} Intraday Triggers:")
            
            # Rule 3: Morning vs afternoon timing
            if data['morning_success'] and data['afternoon_success']:
                morning = data['morning_success']
                afternoon = data['afternoon_success']
                advantage = morning - afternoon
                
                if abs(advantage) > 5:
                    better_time = "morning" if advantage > 0 else "afternoon"
                    rule = f"RULE: {trigger_type} triggers work {abs(advantage):.1f}% better in {better_time}"
                    print(f"   ⏰ {rule}")
                    rules.append(rule)
            
            # Rule 4: Overall success rate guidance
            overall = data['overall_success']
            if overall < 45:
                rule = f"RULE: {trigger_type} intraday triggers have {overall:.1f}% success - low probability, use tight stops"
                print(f"   ⚠️  {rule}")
            elif overall > 55:
                rule = f"RULE: {trigger_type} intraday triggers have {overall:.1f}% success - good probability"
                print(f"   ✅ {rule}")
            else:
                rule = f"RULE: {trigger_type} intraday triggers have {overall:.1f}% success - moderate probability"
                print(f"   📊 {rule}")
            rules.append(rule)
    
    print(f"\n📈 SUMMARY:")
    print(f"   • Generated {len(rules)} actionable trading rules")
    print(f"   • Based on corrected methodology using previous day's close and ATR")
    print(f"   • Gap-open events: {sum(d['total_events'] for d in gap_insights.values())}")
    print(f"   • Intraday trigger events: {sum(d['total_events'] for d in intraday_insights.values())}")
    
    return rules

def main():
    """Run complete corrected insights analysis"""
    print("CORRECTED INTRADAY GOLDEN GATE INSIGHTS ANALYZER")
    print("Using PREVIOUS day's close and ATR for CURRENT day's Golden Gate levels")
    print("Extracting actionable trading insights from 21 years of SPX data")
    
    # Analyze corrected gap-open insights
    gap_insights = analyze_corrected_gap_open_insights()
    
    # Analyze corrected intraday trigger insights
    intraday_insights = analyze_corrected_intraday_insights()
    
    # Generate actionable trading rules
    trading_rules = generate_actionable_rules(gap_insights, intraday_insights)
    
    print(f"\n{'='*80}")
    print("CORRECTED ANALYSIS COMPLETE - ACTIONABLE INSIGHTS EXTRACTED")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()