#!/usr/bin/env python3
"""
Simple test runner to verify the carbon-aware ML project is working correctly.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported successfully."""
    try:
        from data_pipeline.carbon_intensity import get_carbon_intensity, load_config
        from scheduler.scheduler import schedule_training
        from optimization.optimizer import optimize_training_config
        from utils.logger import get_logger
        from ml_engine.train import main
        print("✅ All imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_config_loading():
    """Test that configuration can be loaded."""
    try:
        from data_pipeline.carbon_intensity import load_config
        cfg = load_config()
        assert 'carbon_api' in cfg
        assert 'train' in cfg
        assert 'model' in cfg
        print("✅ Configuration loading successful!")
        return True
    except Exception as e:
        print(f"❌ Config loading error: {e}")
        return False

def test_logger():
    """Test that logger is working."""
    try:
        from utils.logger import get_logger
        logger = get_logger("Test")
        logger.info("Test message")
        print("✅ Logger working correctly!")
        return True
    except Exception as e:
        print(f"❌ Logger error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Running Carbon-Aware ML Project Tests...\n")
    
    tests = [
        test_imports,
        test_config_loading,
        test_logger
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your carbon-aware ML project is ready to run.")
        print("\nTo run the main training script:")
        print("python ml_engine/train.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
