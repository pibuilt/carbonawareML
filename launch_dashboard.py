#!/usr/bin/env python3
"""
Launch script for the Carbon-Aware ML Dashboard.
"""

import sys
import os
import subprocess

def main():
    """Launch the Streamlit dashboard."""
    print("🌱 Starting Carbon-Aware ML Dashboard...")
    
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Dashboard file path
    dashboard_path = os.path.join(current_dir, "dashboard", "streamlit_app.py")
    
    if not os.path.exists(dashboard_path):
        print(f"❌ Dashboard file not found: {dashboard_path}")
        return
    
    print(f"📊 Launching dashboard from: {dashboard_path}")
    print("🌐 Dashboard will open in your default browser")
    print("⏹️  Press Ctrl+C to stop the dashboard")
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            dashboard_path,
            "--theme.base", "light",
            "--theme.primaryColor", "#00C851",
            "--theme.backgroundColor", "#FFFFFF"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        print("\n💡 Make sure you have installed the requirements:")
        print("   pip install streamlit plotly")

if __name__ == "__main__":
    main()
