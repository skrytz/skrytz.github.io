#!/usr/bin/env python3
"""
Create comparison graph between Original and True Trigger methodologies
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def create_comparison_graph():
    """Create comparison graph showing Original vs True Trigger results"""
    
    # Data from both analyses
    data = {
        'SPY': {
            'original_pos': 58.0,
            'original_neg': 62.2,
            'true_pos': 52.1,
            'true_neg': 56.8,
            'excluded_pos': 629,
            'excluded_neg': 521
        },
        'QQQ': {
            'original_pos': 56.3,
            'original_neg': 60.4,
            'true_pos': 50.1,
            'true_neg': 55.9,
            'excluded_pos': 651,
            'excluded_neg': 502
        }
    }
    
    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 14))
    fig.suptitle('Golden Gate Analysis: Original vs True Trigger Methodology Comparison',
                 fontsize=16, fontweight='bold', y=0.94)
    
    # Colors
    colors = {
        'original_pos': '#27ae60',
        'original_neg': '#e74c3c', 
        'true_pos': '#2ecc71',
        'true_neg': '#c0392b',
        'excluded': '#95a5a6'
    }
    
    # 1. Success Rate Comparison - SPY
    ax1.set_title('SPY Success Rates Comparison', fontsize=13, fontweight='bold', pad=15)
    
    categories = ['Positive\nGolden Gate', 'Negative\nGolden Gate']
    original_spy = [data['SPY']['original_pos'], data['SPY']['original_neg']]
    true_spy = [data['SPY']['true_pos'], data['SPY']['true_neg']]
    
    x = np.arange(len(categories))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, original_spy, width, label='Original Method',
                    color=[colors['original_pos'], colors['original_neg']], alpha=0.8)
    bars2 = ax1.bar(x + width/2, true_spy, width, label='True Trigger Method',
                    color=[colors['true_pos'], colors['true_neg']], alpha=0.8)
    
    ax1.set_ylabel('Success Rate (%)', fontsize=12)
    ax1.set_ylim(0, 70)
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories)
    
    # Create custom legend for methodology and pattern types
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=colors['original_pos'], alpha=0.8, label='Original - Positive'),
        Patch(facecolor=colors['original_neg'], alpha=0.8, label='Original - Negative'),
        Patch(facecolor=colors['true_pos'], alpha=0.8, label='True Trigger - Positive'),
        Patch(facecolor=colors['true_neg'], alpha=0.8, label='True Trigger - Negative')
    ]
    ax1.legend(handles=legend_elements, loc='lower right', fontsize=8)
    ax1.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
    for bar in bars2:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # 2. Success Rate Comparison - QQQ
    ax2.set_title('QQQ Success Rates Comparison', fontsize=13, fontweight='bold', pad=15)
    
    original_qqq = [data['QQQ']['original_pos'], data['QQQ']['original_neg']]
    true_qqq = [data['QQQ']['true_pos'], data['QQQ']['true_neg']]
    
    bars3 = ax2.bar(x - width/2, original_qqq, width, label='Original Method',
                    color=[colors['original_pos'], colors['original_neg']], alpha=0.8)
    bars4 = ax2.bar(x + width/2, true_qqq, width, label='True Trigger Method',
                    color=[colors['true_pos'], colors['true_neg']], alpha=0.8)
    
    ax2.set_ylabel('Success Rate (%)', fontsize=12)
    ax2.set_ylim(0, 70)
    ax2.set_xticks(x)
    ax2.set_xticklabels(categories)
    
    # Create same custom legend for QQQ
    ax2.legend(handles=legend_elements, loc='lower right', fontsize=8)
    ax2.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar in bars3:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
    for bar in bars4:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # 3. Negative Advantage Comparison
    ax3.set_title('Negative Momentum Advantage Comparison', fontsize=13, fontweight='bold', pad=15)
    
    tickers = ['SPY', 'QQQ']
    original_advantage = [4.2, 4.1]  # Original advantages
    true_advantage = [4.7, 5.8]     # True trigger advantages
    
    x_adv = np.arange(len(tickers))
    
    bars5 = ax3.bar(x_adv - width/2, original_advantage, width, label='Original Method',
                    color='#3498db', alpha=0.8)
    bars6 = ax3.bar(x_adv + width/2, true_advantage, width, label='True Trigger Method',
                    color='#2980b9', alpha=0.8)
    
    ax3.set_ylabel('Negative Advantage (Percentage Points)', fontsize=12)
    ax3.set_ylim(0, 7)
    ax3.set_xticks(x_adv)
    ax3.set_xticklabels(tickers)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar in bars5:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'+{height:.1f}%', ha='center', va='bottom', fontweight='bold')
    for bar in bars6:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'+{height:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # 4. Excluded Gap Scenarios
    ax4.set_title('Excluded Gap Scenarios (True Trigger Method)', fontsize=13, fontweight='bold', pad=15)
    
    excluded_pos = [data['SPY']['excluded_pos'], data['QQQ']['excluded_pos']]
    excluded_neg = [data['SPY']['excluded_neg'], data['QQQ']['excluded_neg']]
    
    bars7 = ax4.bar(tickers, excluded_pos, label='Positive Gaps Excluded',
                    color=colors['original_pos'], alpha=0.7)
    bars8 = ax4.bar(tickers, excluded_neg, bottom=excluded_pos, label='Negative Gaps Excluded',
                    color=colors['original_neg'], alpha=0.7)
    
    ax4.set_ylabel('Number of Excluded Scenarios', fontsize=12)
    ax4.set_ylim(0, 1400)
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # Add value labels on stacked bars
    for i, ticker in enumerate(tickers):
        # Positive gaps
        ax4.text(i, excluded_pos[i]/2, str(excluded_pos[i]), 
                ha='center', va='center', fontweight='bold', color='white')
        # Negative gaps  
        ax4.text(i, excluded_pos[i] + excluded_neg[i]/2, str(excluded_neg[i]),
                ha='center', va='center', fontweight='bold', color='white')
        # Total
        total = excluded_pos[i] + excluded_neg[i]
        ax4.text(i, total + 30, f'Total: {total}',
                ha='center', va='bottom', fontweight='bold')
    
    # Add methodology explanation
    fig.text(0.5, 0.04,
             'ORIGINAL Method: Counts ANY interaction with 38.2% ATR level during trading day (including gap scenarios)\n'
             '• Example: Price opens at \\$105, 38.2% level is \\$103, day range \\$102-\\$107 → Counts as trigger\n\n'
             'TRUE TRIGGER Method: Only counts when price actually CROSSES THROUGH the 38.2% ATR level\n'
             '• Example: Price opens at \\$105, 38.2% level is \\$103, day range \\$105-\\$107 → NO trigger (never touched \\$103)',
             ha='center', va='bottom', fontsize=9, style='italic',
             bbox=dict(boxstyle="round,pad=0.8", facecolor="lightyellow", alpha=0.9))
    
    # Adjust layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.88, bottom=0.22, hspace=0.4, wspace=0.25)
    
    # Save the graph
    output_file = 'data/analysis_results/golden_gate_methodology_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nComparison graph saved to: {output_file}")
    
    # Also save as high-res version
    output_file_hires = 'data/analysis_results/golden_gate_methodology_comparison_hires.png'
    plt.savefig(output_file_hires, dpi=600, bbox_inches='tight', facecolor='white')
    print(f"High-resolution version saved to: {output_file_hires}")
    
    plt.show()
    
    return output_file

if __name__ == "__main__":
    print("Creating Golden Gate Methodology Comparison Graph...")
    create_comparison_graph()
    print("Graph creation completed!")