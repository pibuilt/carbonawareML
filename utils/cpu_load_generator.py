#!/usr/bin/env python3
"""
CPU Load Generator for Testing Energy Monitoring
This script generates controlled CPU load to demonstrate energy monitoring on the dashboard.
"""

import time
import threading
import multiprocessing
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.energy_monitor import EnergyTracker

def cpu_intensive_task(duration_seconds: int = 10, intensity: float = 0.7):
    """
    Generate CPU-intensive work for a specified duration.
    
    Args:
        duration_seconds: How long to run the task
        intensity: CPU intensity (0.0 to 1.0)
    """
    end_time = time.time() + duration_seconds
    
    while time.time() < end_time:
        # CPU-intensive computation
        for i in range(int(100000 * intensity)):
            _ = i ** 2 + i ** 0.5
        
        # Small break to control intensity
        time.sleep(0.01 * (1 - intensity))

def simulate_ml_training(epochs: int = 5, epoch_duration: int = 10):
    """
    Simulate ML training with varying CPU loads.
    
    Args:
        epochs: Number of training epochs
        epoch_duration: Duration of each epoch in seconds
    """
    print(f"🤖 Simulating ML Training: {epochs} epochs, {epoch_duration}s each")
    
    with EnergyTracker(sampling_interval=0.5) as monitor:
        for epoch in range(epochs):
            print(f"🔄 Epoch {epoch + 1}/{epochs}")
            
            # Simulate different phases of training
            phases = [
                ("Data Loading", 0.3, 2),
                ("Forward Pass", 0.8, 3),
                ("Backward Pass", 0.9, 3),
                ("Optimization", 0.6, 2)
            ]
            
            for phase_name, intensity, duration in phases:
                print(f"   {phase_name}... (intensity: {intensity:.1f})")
                
                # Run CPU intensive task
                cpu_intensive_task(duration, intensity)
                
                # Show current stats
                stats = monitor.get_realtime_stats()
                if stats:
                    print(f"   💡 Power: {stats.get('total_power_watts', 0):.1f}W, "
                          f"CPU: {stats.get('cpu_utilization', 0):.1f}%")
                
                time.sleep(0.5)  # Brief pause between phases
    
    # Show final summary
    summary = monitor.get_summary()
    if summary:
        print(f"\n📊 Training Complete!")
        print(f"⚡ Total Energy: {summary.get('energy', {}).get('total_kwh', 0):.6f} kWh")
        print(f"🔌 Average Power: {summary.get('power', {}).get('avg_total_watts', 0):.1f}W")
        print(f"⏱️  Duration: {summary.get('duration_seconds', 0):.1f}s")

def stress_test_cpu(duration: int = 30):
    """
    Create high CPU load using multiple processes.
    
    Args:
        duration: Duration in seconds
    """
    print(f"🔥 Starting CPU stress test for {duration} seconds...")
    print("💡 This will generate high CPU load - watch the dashboard!")
    
    cpu_count = multiprocessing.cpu_count()
    print(f"🖥️  Using {cpu_count} CPU cores")
    
    with EnergyTracker(sampling_interval=1.0) as monitor:
        # Create worker processes
        processes = []
        
        def worker():
            """Worker function for stress testing."""
            end_time = time.time() + duration
            while time.time() < end_time:
                # High-intensity computation
                for _ in range(1000000):
                    _ = 3.14159 ** 2.71828
        
        # Start worker processes (one per CPU core)
        for i in range(cpu_count):
            p = multiprocessing.Process(target=worker)
            p.start()
            processes.append(p)
            print(f"✅ Started worker process {i+1}")
        
        # Monitor progress
        start_time = time.time()
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            remaining = duration - elapsed
            
            stats = monitor.get_realtime_stats()
            if stats:
                print(f"⏱️  {remaining:.0f}s remaining - "
                      f"Power: {stats.get('total_power_watts', 0):.1f}W, "
                      f"CPU: {stats.get('cpu_utilization', 0):.1f}%")
            
            time.sleep(2)
        
        # Clean up processes
        for p in processes:
            p.terminate()
            p.join()
        
        print("🛑 Stress test completed!")
    
    # Show results
    summary = monitor.get_summary()
    if summary:
        print(f"\n📊 Stress Test Results:")
        print(f"⚡ Total Energy: {summary.get('energy', {}).get('total_kwh', 0):.6f} kWh")
        print(f"🔌 Peak Power: {summary.get('power', {}).get('peak_total_watts', 0):.1f}W")
        print(f"📈 Avg CPU Util: {summary.get('utilization', {}).get('avg_cpu_percent', 0):.1f}%")

def interactive_demo():
    """Interactive demo with user choices."""
    print("🌱 Energy Monitoring Demo")
    print("=" * 40)
    print("Choose a demo option:")
    print("1. Light Training Simulation (2 minutes)")
    print("2. Medium Training Simulation (3 minutes)")
    print("3. CPU Stress Test (30 seconds)")
    print("4. Custom CPU Load")
    print("5. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                simulate_ml_training(epochs=3, epoch_duration=8)
            elif choice == "2":
                simulate_ml_training(epochs=5, epoch_duration=10)
            elif choice == "3":
                stress_test_cpu(30)
            elif choice == "4":
                duration = int(input("Duration (seconds): "))
                intensity = float(input("Intensity (0.1-1.0): "))
                cpu_intensive_task(duration, intensity)
            elif choice == "5":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Demo interrupted by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Energy Monitoring Demo")
    parser.add_argument("--mode", choices=["interactive", "light", "medium", "stress"], 
                       default="interactive", help="Demo mode")
    parser.add_argument("--duration", type=int, default=30, help="Duration in seconds")
    
    args = parser.parse_args()
    
    if args.mode == "interactive":
        interactive_demo()
    elif args.mode == "light":
        simulate_ml_training(epochs=3, epoch_duration=8)
    elif args.mode == "medium":
        simulate_ml_training(epochs=5, epoch_duration=10)
    elif args.mode == "stress":
        stress_test_cpu(args.duration)
