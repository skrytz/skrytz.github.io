# Setup Instructions for Stock Data Pipeline

## Python Installation Issue

The system currently doesn't have Python properly installed or configured. Here's how to fix this:

## Option 1: Install Python from Python.org (Recommended)

1. **Download Python:**
   - Go to https://www.python.org/downloads/
   - Download Python 3.9 or newer for Windows
   - **Important:** During installation, check "Add Python to PATH"

2. **Verify Installation:**
   ```cmd
   python --version
   pip --version
   ```

3. **Install Dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

4. **Run the Pipeline:**
   ```cmd
   python stock_data_pipeline.py
   ```

## Option 2: Use Anaconda/Miniconda

1. **Download Anaconda:**
   - Go to https://www.anaconda.com/products/distribution
   - Download and install Anaconda for Windows

2. **Open Anaconda Prompt and run:**
   ```cmd
   cd "C:\Users\Orest\Desktop\Programming\Data"
   pip install -r requirements.txt
   python stock_data_pipeline.py
   ```

## Quick Test Commands

Once Python is installed, you can test the pipeline with these commands:

### List all available tickers:
```cmd
python run_pipeline.py --list
```

### Fetch SPY data for 1 year:
```cmd
python run_pipeline.py SPY -p 1y
```

### Fetch all MAG7 stocks for 6 months:
```cmd
python run_pipeline.py --mag7 -p 6mo
```

### Run comprehensive examples:
```cmd
python example_usage.py
```

### Test the pipeline:
```cmd
python test_pipeline.py
```

## What the Pipeline Does

The pipeline will:
1. Fetch stock data from Yahoo Finance (free, no API key needed)
2. Process and clean the data
3. Add calculated fields (daily range, change, change %)
4. Save to CSV files in the `data/` directory

## Expected Output

When working, you'll see output like:
```
2024-01-01 10:00:00 - INFO - Fetching 1y of SPY (SPDR S&P 500 ETF Trust) data with 1d interval...
2024-01-01 10:00:02 - INFO - Successfully fetched 252 records for SPY
2024-01-01 10:00:02 - INFO - Data processing completed successfully for SPY
2024-01-01 10:00:02 - INFO - Data saved to: data/SPY_daily_data_20240101_100002.csv
✅ Success! Data saved to: data/SPY_daily_data_20240101_100002.csv
```

## Troubleshooting

If you continue to have issues:
1. Make sure Python is added to your system PATH
2. Try running commands from Command Prompt (cmd) instead of PowerShell
3. Restart your computer after installing Python
4. Use the full path to python.exe if needed