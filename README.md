# Golden Gate Analysis - SPY Momentum Study

An interactive dashboard analyzing momentum continuation patterns in SPY using ATR-based levels inspired by Saty's ATR methodology.

## 🔗 Live Dashboard
[**View Interactive Dashboard**](https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/)

## 📊 Key Findings

### Asymmetric Market Behavior Discovered
- **Positive Golden Gate**: 57.1% probability (+38.2% ATR → +61.8% ATR)
- **Negative Golden Gate**: 71.1% probability (-38.2% ATR → -61.8% ATR)
- **Critical Insight**: Negative momentum is **14% stronger** than positive momentum

### Market Psychology
Fear-driven selling creates more persistent momentum than greed-driven buying, suggesting emotional selling cascades more effectively than emotional buying.

## 🎯 What is a Golden Gate?

A **Golden Gate** is a momentum continuation pattern that measures the probability of extended price movement within the same trading day. The concept is built on Saty's ATR (Average True Range) level methodology.

### The Golden Gate Pattern Definition:
1. **Initial Trigger**: Price touches a specific ATR-based level (38.2% of ATR from previous close)
2. **Continuation Target**: We measure if price continues to an extended level (61.8% of ATR) the same day
3. **Directional Separation**: Positive and negative patterns are analyzed completely separately

### Why "Golden Gate"?
The name represents the "gateway" or threshold that, once crossed, indicates a higher probability of continued momentum in the same direction - like crossing the Golden Gate Bridge, once you're on it, you're likely to complete the journey to the other side.

## 🔬 Deep Dive: ATR Methodology

### What is ATR (Average True Range)?
ATR measures market volatility by calculating the average of true ranges over a specified period (typically 14 days). It was developed by J. Welles Wilder Jr.

**True Range is the largest of:**
1. Current High - Current Low
2. |Current High - Previous Close|
3. |Current Low - Previous Close|

**ATR = Average of True Range over 14 periods**

### Saty's ATR Level System
Based on Saty Mahajan's methodology, ATR levels use Fibonacci ratios to create volatility-adjusted support and resistance levels:

#### Core ATR Levels (from previous close):
- **±23.6% ATR**: Trigger levels (entry signals)
- **±38.2% ATR**: Initial momentum levels
- **±50.0% ATR**: Intermediate levels
- **±61.8% ATR**: Key target levels (Golden Gate target)
- **±78.6% ATR**: Extended levels
- **±100% ATR**: Full ATR levels
- **±123.6% ATR**: Extension levels
- **±161.8% ATR**: Major extension levels

#### Why These Percentages?
These are **Fibonacci retracement ratios** applied to volatility:
- **38.2%** and **61.8%** are the most significant Fibonacci levels
- **23.6%** acts as an early warning/trigger level
- **78.6%** represents strong momentum continuation
- **100%** is a full ATR move (complete daily range)

### Golden Gate Specific Logic

#### Positive Golden Gate:
```
Previous Close: $590.00
ATR: $10.00

+38.2% ATR Level: $590.00 + ($10.00 × 0.382) = $593.82
+61.8% ATR Level: $590.00 + ($10.00 × 0.618) = $596.18

Golden Gate Event: If price touches $593.82, what's the probability it reaches $596.18 the same day?
```

#### Negative Golden Gate:
```
Previous Close: $590.00
ATR: $10.00

-38.2% ATR Level: $590.00 - ($10.00 × 0.382) = $586.18
-61.8% ATR Level: $590.00 - ($10.00 × 0.618) = $583.82

Golden Gate Event: If price touches $586.18, what's the probability it reaches $583.82 the same day?
```

## 📈 Analysis Results (SPY 2025)

| Pattern | Initial Level | Target Level | Touch Events | Golden Gates | Success Rate |
|---------|---------------|--------------|--------------|--------------|--------------|
| Positive | +38.2% ATR | +61.8% ATR | 42 | 24 | **57.1%** |
| Negative | -38.2% ATR | -61.8% ATR | 45 | 32 | **71.1%** |

**Data Period**: January 23 - June 9, 2025 (94 trading days)

### Statistical Significance
- **Total Analysis Days**: 94 trading days
- **Combined ATR Touch Events**: 87 events
- **Combined Golden Gate Events**: 56 events
- **Overall Pattern Reliability**: High frequency provides statistical confidence

## 🛠️ Technical Implementation

### Data Processing Pipeline:
1. **Load OHLCV Data**: Daily SPY data from Yahoo Finance
2. **Calculate ATR**: 14-period rolling average of true ranges
3. **Generate Levels**: Apply Fibonacci ratios to ATR from previous close
4. **Detect Touches**: Check if daily high/low touched specific levels
5. **Measure Continuation**: Track if initial touch led to extended touch same day

### Level Touch Detection:
```python
def check_level_touch(high, low, level):
    """Check if price touched a specific level during the day"""
    return low <= level <= high
```

### ATR Calculation:
```python
def calculate_atr(data, period=14):
    """Calculate ATR (Average True Range)"""
    high = data['high']
    low = data['low'] 
    close = data['close']
    
    # Calculate True Range components
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    
    # True Range is the maximum of the three
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # ATR is the rolling average
    atr = true_range.rolling(window=period).mean()
    
    return atr
```

## 💡 Trading Implications

1. **Short-side momentum** strategies may have higher success rates
2. **Risk management** should account for stronger downward continuation
3. **Position sizing** may warrant different approaches for directional trades
4. **Stop losses** on long positions may need to be tighter due to stronger negative momentum

## 🔬 Methodology

The analysis uses Average True Range (ATR) to create volatility-adjusted levels:
- **ATR**: 14-period average of daily true ranges
- **Levels**: Previous close ± (ATR × Fibonacci ratio)
- **Golden Gate Event**: Initial level touch → Extended level touch same day

## 📁 Repository Contents

- `index.html` - Interactive dashboard with charts and analysis
- `golden_gate_analysis.py` - Python analysis script
- `data/` - Sample CSV data files with results

## 🙏 Attribution

Golden Gate concept inspired by **Saty's ATR Levels** methodology.  
Visit: [satyland.com](https://satyland.com/)

## ⚠️ Disclaimer

**Educational research only. Not financial advice.**  
Trading involves substantial risk. Consult qualified advisors before investing.  
Author not responsible for trading losses.

---

*Built with HTML, CSS, JavaScript, and Chart.js*