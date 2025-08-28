#!/usr/bin/env python3
"""
Simple demo script to showcase carbon-aware ML capabilities.
"""

import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_carbon_intensity():
    """Demo carbon intensity fetching."""
    print("🌍 Testing Carbon Intensity API...")
    try:
        from data_pipeline.carbon_intensity import get_carbon_intensity
        ci = get_carbon_intensity()
        if ci:
            print(f"✅ Current carbon intensity: {ci} gCO2eq/kWh")
            if ci < 300:
                print("🟢 Low carbon intensity - Good time for training!")
            elif ci < 500:
                print("🟡 Moderate carbon intensity - Acceptable for training")
            else:
                print("🔴 High carbon intensity - Consider waiting")
        else:
            print("⚠️  Could not fetch carbon intensity (using mock mode)")
    except Exception as e:
        print(f"❌ Error: {e}")

def demo_energy_monitoring():
    """Demo energy monitoring."""
    print("\n⚡ Testing Energy Monitoring...")
    try:
        from utils.energy_monitor import EnergyTracker
        
        print("Starting energy monitoring for 3 seconds...")
        with EnergyTracker(sampling_interval=0.5) as monitor:
            # Simulate some work
            for i in range(3):
                print(f"  Working... {i+1}/3")
                # Light computation to generate some CPU activity
                _ = sum(x**2 for x in range(100000))
                time.sleep(1)
        
        # Get summary
        summary = monitor.get_summary()
        if summary:
            energy_kwh = summary.get('energy', {}).get('total_kwh', 0)
            avg_power = summary.get('power', {}).get('avg_total_watts', 0)
            print(f"✅ Energy consumed: {energy_kwh:.6f} kWh")
            print(f"✅ Average power: {avg_power:.1f} W")
        else:
            print("⚠️  No energy data collected")
            
    except Exception as e:
        print(f"❌ Energy monitoring error: {e}")

def demo_carbon_calculation():
    """Demo carbon footprint calculation."""
    print("\n🧮 Testing Carbon Footprint Calculation...")
    try:
        from utils.carbon_calculator import CarbonAwareTrainingSession
        
        print("Running carbon-aware training simulation...")
        with CarbonAwareTrainingSession("Demo Training", sampling_interval=0.5) as session:
            # Simulate ML training
            print("  Training epoch 1/3...")
            _ = sum(x**2 for x in range(200000))
            time.sleep(1)
            
            print("  Training epoch 2/3...")
            _ = sum(x**3 for x in range(200000))
            time.sleep(1)
            
            print("  Training epoch 3/3...")
            _ = sum(x**0.5 for x in range(1, 200000))
            time.sleep(1)
        
        # Get carbon footprint
        training_session = CarbonAwareTrainingSession("Demo Training")
        footprint = training_session.get_carbon_footprint()
        if footprint:
            print(f"✅ Carbon footprint: {footprint.total_co2_grams:.2f}g CO2")
            print(f"✅ Energy used: {footprint.energy_kwh:.6f} kWh")
            print(f"✅ Duration: {footprint.duration_hours:.4f} hours")
            
            # Show equivalents
            equivalents = training_session.get_equivalents()
            print("🌍 Environmental equivalents:")
            for key, value in list(equivalents.items())[:3]:  # Show first 3
                print(f"   • {key.replace('_', ' ').title()}: {value}")
        else:
            print("⚠️  Could not calculate carbon footprint")
            
    except Exception as e:
        print(f"❌ Carbon calculation error: {e}")

def demo_scheduler():
    """Demo training scheduler."""
    print("\n⏰ Testing Training Scheduler...")
    try:
        from scheduler.scheduler import schedule_training
        
        recommendation = schedule_training()
        if recommendation:
            print("✅ Training is RECOMMENDED right now!")
            print("   ✓ Time window is open")
            print("   ✓ Carbon intensity is acceptable")
        else:
            print("⏸️  Training is NOT recommended right now")
            print("   Check time window and carbon intensity thresholds")
            
    except Exception as e:
        print(f"❌ Scheduler error: {e}")

def main():
    """Run the complete demo."""
    print("🌱 Carbon-Aware ML System Demo")
    print("=" * 50)
    
    # Run all demos
    demo_carbon_intensity()
    demo_energy_monitoring()
    demo_carbon_calculation()
    demo_scheduler()
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed!")
    print("\n💡 Next steps:")
    print("   • Run full training: python ml_engine/train.py")
    print("   • Launch dashboard: python launch_dashboard.py")
    print("   • Run tests: python -m pytest tests/")

if __name__ == "__main__":
    main()
