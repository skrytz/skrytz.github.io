# Golden Gate Analysis - SPY Momentum Study

An interactive dashboard analyzing momentum continuation patterns in SPY using ATR-based levels.

## 🔗 Live Dashboard
[**View Interactive Dashboard**](https://skrytz.github.io/skrytz.github.io/)

## 📊 Key Findings

### Asymmetric Market Behavior Discovered
- **Positive Golden Gate**: 57.1% probability (+38.2% ATR → +61.8% ATR)
- **Negative Golden Gate**: 71.1% probability (-38.2% ATR → -61.8% ATR)
- **Critical Insight**: Negative momentum is **14% stronger** than positive momentum

### Market Psychology
Fear-driven selling creates more persistent momentum than greed-driven buying, suggesting emotional selling cascades more effectively than emotional buying.

## 🎯 What is a Golden Gate?

A **Golden Gate** is a momentum continuation pattern where:
1. Price touches an initial ATR level (38.2% of Average True Range)
2. We measure the probability it continues to an extended level (61.8% ATR) the same day

## 📈 Analysis Results (SPY 2025)

| Pattern | Initial Level | Target Level | Events | Success Rate |
|---------|---------------|--------------|---------|--------------|
| Positive | +38.2% ATR | +61.8% ATR | 42 | **57.1%** |
| Negative | -38.2% ATR | -61.8% ATR | 45 | **71.1%** |

**Data Period**: January 23 - June 9, 2025 (94 trading days)

## 🛠️ Technical Details

- **ATR Period**: 14 days
- **Level Calculation**: Fibonacci ratios (38.2%, 61.8%) applied to ATR
- **Data Source**: Yahoo Finance SPY daily OHLCV data
- **Analysis Method**: Intraday level touch detection

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
