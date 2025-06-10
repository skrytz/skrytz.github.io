"""
Test script for Stock Data Pipeline
Quick verification that the pipeline is working correctly
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
from src.stock_data_pipeline import StockDataPipeline

def test_single_ticker():
    """Test fetching data for a single ticker"""
    print("Testing single ticker (SPY)...")
    
    pipeline = StockDataPipeline()
    
    # Test with a small period to make it fast
    result = pipeline.run_pipeline("SPY", period="5d", save_filename="test_SPY.csv")
    
    if result and os.path.exists(result):
        data = pd.read_csv(result)
        print(f"✅ SPY test passed - {len(data)} records saved")
        
        # Verify expected columns
        expected_columns = ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in expected_columns if col not in data.columns]
        
        if missing_columns:
            print(f"⚠️  Warning: Missing columns: {missing_columns}")
        else:
            print("✅ All expected columns present")
        
        # Clean up test file
        os.remove(result)
        return True
    else:
        print("❌ SPY test failed")
        return False

def test_ticker_validation():
    """Test ticker validation"""
    print("\nTesting ticker validation...")
    
    pipeline = StockDataPipeline()
    
    # Test valid ticker
    valid = pipeline.validate_ticker("AAPL")
    if valid:
        print("✅ Valid ticker validation passed")
    else:
        print("❌ Valid ticker validation failed")
        return False
    
    # Test invalid ticker
    invalid = pipeline.validate_ticker("INVALID")
    if not invalid:
        print("✅ Invalid ticker validation passed")
    else:
        print("❌ Invalid ticker validation failed")
        return False
    
    return True

def test_allowed_tickers():
    """Test getting allowed tickers"""
    print("\nTesting allowed tickers...")
    
    pipeline = StockDataPipeline()
    allowed = pipeline.get_allowed_tickers()
    
    if isinstance(allowed, dict) and len(allowed) > 0:
        print(f"✅ Allowed tickers test passed - {len(allowed)} tickers available")
        
        # Check for expected tickers
        expected_tickers = ['SPY', 'AAPL', 'QQQ', 'NVDA']
        missing = [ticker for ticker in expected_tickers if ticker not in allowed]
        
        if missing:
            print(f"⚠️  Warning: Missing expected tickers: {missing}")
        else:
            print("✅ All expected tickers present")
        
        return True
    else:
        print("❌ Allowed tickers test failed")
        return False

def test_data_processing():
    """Test data processing functionality"""
    print("\nTesting data processing...")
    
    pipeline = StockDataPipeline()
    
    # Fetch raw data
    raw_data = pipeline.fetch_historical_data("AAPL", period="5d")
    
    if raw_data is not None and not raw_data.empty:
        print(f"✅ Data fetch passed - {len(raw_data)} records")
        
        # Process data
        processed_data = pipeline.process_data(raw_data, "AAPL")
        
        if processed_data is not None and not processed_data.empty:
            print(f"✅ Data processing passed - {len(processed_data)} records")
            
            # Check for calculated fields
            calculated_fields = ['daily_range', 'daily_change', 'daily_change_pct']
            missing_fields = [field for field in calculated_fields if field not in processed_data.columns]
            
            if missing_fields:
                print(f"⚠️  Warning: Missing calculated fields: {missing_fields}")
            else:
                print("✅ All calculated fields present")
            
            return True
        else:
            print("❌ Data processing failed")
            return False
    else:
        print("❌ Data fetch failed")
        return False

def test_batch_processing():
    """Test batch processing"""
    print("\nTesting batch processing...")
    
    pipeline = StockDataPipeline()
    
    # Test with a small subset
    test_tickers = ['SPY', 'AAPL']
    results = pipeline.run_multiple_tickers(test_tickers, period="5d")
    
    if isinstance(results, dict) and len(results) == len(test_tickers):
        success_count = sum(1 for result in results.values() if result is not None)
        print(f"✅ Batch processing passed - {success_count}/{len(test_tickers)} successful")
        
        # Clean up test files
        for filepath in results.values():
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
        
        return success_count > 0
    else:
        print("❌ Batch processing failed")
        return False

def run_all_tests():
    """Run all tests"""
    print("Stock Data Pipeline Test Suite")
    print("=" * 50)
    
    tests = [
        test_allowed_tickers,
        test_ticker_validation,
        test_data_processing,
        test_single_ticker,
        test_batch_processing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Pipeline is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

def main():
    """Main test function"""
    try:
        success = run_all_tests()
        
        if success:
            print("\n✅ Pipeline is ready to use!")
            print("\nNext steps:")
            print("1. Run 'python example_usage.py' to see usage examples")
            print("2. Run 'python run_pipeline.py --list' to see all allowed tickers")
            print("3. Run 'python run_pipeline.py SPY' to fetch SPY data")
        else:
            print("\n❌ Pipeline has issues. Please check the error messages above.")
            
    except Exception as e:
        print(f"❌ Test suite failed with exception: {e}")

if __name__ == "__main__":
    main()