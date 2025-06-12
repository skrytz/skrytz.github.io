# Data Science Pipeline

## Overview
This directory contains all data science work including data collection, analysis, and exploration of SPX financial data.

## Directory Structure

```
data_science/
├── README.md                   # This file
├── src/                       # Core data pipeline modules
│   ├── __init__.py
│   ├── stock_data_pipeline.py # IBKR data collection pipeline
│   └── config.py              # Configuration settings
├── scripts/                   # Data collection and analysis scripts
│   ├── fixed_spx_historical_collection.py # Main SPX data collector
│   └── enhanced_golden_gate_analysis.py   # Golden gate analysis
├── notebooks/                 # Jupyter notebooks for exploration
├── analysis/                  # Analysis modules and utilities
├── reports/                   # Generated reports and findings
└── visualizations/           # Charts, plots, and visual outputs
```

## Key Components

### Data Collection
- **SPX Historical Data**: 210,233 records (2004-2025)
- **IBKR Integration**: Real-time and historical data collection
- **Golden Gate Analysis**: Advanced market pattern analysis

### Analysis Capabilities
- Time series analysis
- Market pattern recognition
- Statistical analysis
- Data quality validation

## Usage

### Collect SPX Data
```bash
cd scripts
python fixed_spx_historical_collection.py
```

### Run Analysis
```bash
cd scripts
python enhanced_golden_gate_analysis.py
```

## Data Sources
- **Primary**: SPX 10-minute data via IBKR
- **Coverage**: March 2004 - Present
- **Quality**: Validated, no duplicates
- **Size**: 37+ MB of historical data