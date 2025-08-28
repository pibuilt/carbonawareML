#!/usr/bin/env python3
"""
Main entry point for the Carbon-Aware ML project.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point for the Carbon-Aware ML project."""
    try:
        from ml_engine.train import main as train_main
        print("🌱 Starting Carbon-Aware ML Training System...")
        train_main()
    except KeyboardInterrupt:
        print("\n⏹️  Training interrupted by user")
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
