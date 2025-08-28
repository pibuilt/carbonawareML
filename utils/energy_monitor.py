"""
Real-time energy monitoring for CPU and GPU during ML training.
Tracks power consumption and provides accurate energy usage metrics.
"""

import time
import threading
import psutil
import platform
from typing import Dict, Optional, List
from dataclasses import dataclass
from utils.logger import get_logger

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

try:
    import nvidia_ml_py3 as nvml
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False

logger = get_logger("EnergyMonitor")

@dataclass
class EnergyMeasurement:
    """Single energy measurement point."""
    timestamp: float
    cpu_power_watts: float
    gpu_power_watts: float
    total_power_watts: float
    cpu_utilization: float
    gpu_utilization: float
    memory_usage_gb: float

class EnergyMonitor:
    """Real-time energy monitoring for ML training."""
    
    def __init__(self, sampling_interval: float = 1.0):
        """
        Initialize energy monitor.
        
        Args:
            sampling_interval: Time between measurements in seconds
        """
        self.sampling_interval = sampling_interval
        self.measurements: List[EnergyMeasurement] = []
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Initialize GPU monitoring
        self.gpu_available = self._init_gpu_monitoring()
        
        # CPU power estimation coefficients (rough estimates)
        self.cpu_tdp = self._estimate_cpu_tdp()
        
        logger.info(f"Energy monitor initialized. GPU available: {self.gpu_available}")
        logger.info(f"Estimated CPU TDP: {self.cpu_tdp}W")
    
    def _init_gpu_monitoring(self) -> bool:
        """Initialize GPU monitoring libraries."""
        if not GPU_AVAILABLE:
            logger.warning("GPUtil not available. Install with: pip install gputil")
            return False
            
        if NVML_AVAILABLE:
            try:
                nvml.nvmlInit()
                device_count = nvml.nvmlDeviceGetCount()
                logger.info(f"NVIDIA GPU monitoring initialized. Found {device_count} GPU(s)")
                return True
            except Exception as e:
                logger.warning(f"NVML initialization failed: {e}")
        
        # Fallback to GPUtil
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                logger.info(f"GPU monitoring via GPUtil. Found {len(gpus)} GPU(s)")
                return True
        except Exception as e:
            logger.warning(f"GPU monitoring initialization failed: {e}")
        
        return False
    
    def _estimate_cpu_tdp(self) -> float:
        """Estimate CPU Thermal Design Power (TDP)."""
        try:
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Rough TDP estimation based on CPU characteristics
            if cpu_freq:
                base_freq_ghz = cpu_freq.current / 1000
                # Simple heuristic: ~15-25W per core for modern CPUs
                estimated_tdp = cpu_count * (15 + (base_freq_ghz - 2.0) * 5)
                return max(35, min(estimated_tdp, 200))  # Clamp between 35-200W
            else:
                # Fallback based on core count
                return cpu_count * 20
        except Exception:
            return 65  # Conservative default
    
    def _get_cpu_power(self) -> tuple[float, float]:
        """
        Estimate CPU power consumption.
        
        Returns:
            (power_watts, utilization_percent)
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            # Power scales roughly with utilization
            estimated_power = self.cpu_tdp * (cpu_percent / 100.0)
            return estimated_power, cpu_percent
        except Exception as e:
            logger.error(f"Error getting CPU power: {e}")
            return 0.0, 0.0
    
    def _get_gpu_power(self) -> tuple[float, float]:
        """
        Get GPU power consumption.
        
        Returns:
            (power_watts, utilization_percent)
        """
        if not self.gpu_available:
            return 0.0, 0.0
        
        try:
            total_power = 0.0
            total_util = 0.0
            gpu_count = 0
            
            if NVML_AVAILABLE:
                # Use NVIDIA ML for accurate power readings
                device_count = nvml.nvmlDeviceGetCount()
                for i in range(device_count):
                    handle = nvml.nvmlDeviceGetHandleByIndex(i)
                    
                    # Get power consumption in milliwatts
                    power_mw = nvml.nvmlDeviceGetPowerUsage(handle)
                    power_w = power_mw / 1000.0
                    
                    # Get utilization
                    util = nvml.nvmlDeviceGetUtilizationRates(handle)
                    gpu_util = util.gpu
                    
                    total_power += power_w
                    total_util += gpu_util
                    gpu_count += 1
                    
            else:
                # Fallback to GPUtil (less accurate)
                gpus = GPUtil.getGPUs()
                for gpu in gpus:
                    # GPUtil doesn't provide power, estimate based on utilization
                    estimated_power = 250 * (gpu.load if gpu.load else 0)  # Assume 250W max
                    total_power += estimated_power
                    total_util += (gpu.load * 100 if gpu.load else 0)
                    gpu_count += 1
            
            avg_util = total_util / gpu_count if gpu_count > 0 else 0.0
            return total_power, avg_util
            
        except Exception as e:
            logger.error(f"Error getting GPU power: {e}")
            return 0.0, 0.0
    
    def _get_memory_usage(self) -> float:
        """Get system memory usage in GB."""
        try:
            memory = psutil.virtual_memory()
            return memory.used / (1024**3)  # Convert to GB
        except Exception:
            return 0.0
    
    def _monitor_loop(self):
        """Main monitoring loop running in separate thread."""
        logger.info("Energy monitoring started")
        
        while self.monitoring:
            try:
                timestamp = time.time()
                
                # Get power measurements
                cpu_power, cpu_util = self._get_cpu_power()
                gpu_power, gpu_util = self._get_gpu_power()
                total_power = cpu_power + gpu_power
                memory_usage = self._get_memory_usage()
                
                # Create measurement
                measurement = EnergyMeasurement(
                    timestamp=timestamp,
                    cpu_power_watts=cpu_power,
                    gpu_power_watts=gpu_power,
                    total_power_watts=total_power,
                    cpu_utilization=cpu_util,
                    gpu_utilization=gpu_util,
                    memory_usage_gb=memory_usage
                )
                
                self.measurements.append(measurement)
                
                # Log periodically
                if len(self.measurements) % 10 == 0:
                    logger.debug(f"Power: CPU={cpu_power:.1f}W, GPU={gpu_power:.1f}W, "
                               f"Total={total_power:.1f}W, CPU%={cpu_util:.1f}, GPU%={gpu_util:.1f}")
                
                time.sleep(self.sampling_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.sampling_interval)
    
    def start_monitoring(self):
        """Start energy monitoring in background thread."""
        if self.monitoring:
            logger.warning("Monitoring already started")
            return
        
        self.monitoring = True
        self.measurements.clear()
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Energy monitoring started")
    
    def stop_monitoring(self) -> Dict:
        """Stop monitoring and return summary statistics."""
        if not self.monitoring:
            logger.warning("Monitoring not running")
            return {}
        
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        
        logger.info("Energy monitoring stopped")
        return self.get_summary()
    
    def get_summary(self) -> Dict:
        """Get summary statistics of energy consumption."""
        if not self.measurements:
            return {}
        
        # Calculate duration
        duration_seconds = self.measurements[-1].timestamp - self.measurements[0].timestamp
        duration_hours = duration_seconds / 3600
        
        # Calculate average power consumption
        avg_cpu_power = sum(m.cpu_power_watts for m in self.measurements) / len(self.measurements)
        avg_gpu_power = sum(m.gpu_power_watts for m in self.measurements) / len(self.measurements)
        avg_total_power = sum(m.total_power_watts for m in self.measurements) / len(self.measurements)
        
        # Calculate energy consumption (power * time)
        total_energy_kwh = avg_total_power * duration_hours / 1000  # Convert to kWh
        cpu_energy_kwh = avg_cpu_power * duration_hours / 1000
        gpu_energy_kwh = avg_gpu_power * duration_hours / 1000
        
        # Calculate peak power
        peak_total_power = max(m.total_power_watts for m in self.measurements)
        peak_cpu_power = max(m.cpu_power_watts for m in self.measurements)
        peak_gpu_power = max(m.gpu_power_watts for m in self.measurements)
        
        # Average utilization
        avg_cpu_util = sum(m.cpu_utilization for m in self.measurements) / len(self.measurements)
        avg_gpu_util = sum(m.gpu_utilization for m in self.measurements) / len(self.measurements)
        
        summary = {
            'duration_seconds': duration_seconds,
            'duration_hours': duration_hours,
            'measurements_count': len(self.measurements),
            'energy': {
                'total_kwh': total_energy_kwh,
                'cpu_kwh': cpu_energy_kwh,
                'gpu_kwh': gpu_energy_kwh
            },
            'power': {
                'avg_total_watts': avg_total_power,
                'avg_cpu_watts': avg_cpu_power,
                'avg_gpu_watts': avg_gpu_power,
                'peak_total_watts': peak_total_power,
                'peak_cpu_watts': peak_cpu_power,
                'peak_gpu_watts': peak_gpu_power
            },
            'utilization': {
                'avg_cpu_percent': avg_cpu_util,
                'avg_gpu_percent': avg_gpu_util
            },
            'system': {
                'cpu_tdp_watts': self.cpu_tdp,
                'gpu_available': self.gpu_available,
                'platform': platform.platform()
            }
        }
        
        return summary
    
    def get_realtime_stats(self) -> Dict:
        """Get current real-time statistics."""
        if not self.measurements:
            return {}
        
        latest = self.measurements[-1]
        return {
            'timestamp': latest.timestamp,
            'cpu_power_watts': latest.cpu_power_watts,
            'gpu_power_watts': latest.gpu_power_watts,
            'total_power_watts': latest.total_power_watts,
            'cpu_utilization': latest.cpu_utilization,
            'gpu_utilization': latest.gpu_utilization,
            'memory_usage_gb': latest.memory_usage_gb
        }

# Context manager for easy usage
class EnergyTracker:
    """Context manager for tracking energy during ML training."""
    
    def __init__(self, sampling_interval: float = 1.0):
        self.monitor = EnergyMonitor(sampling_interval)
        self.summary = {}
    
    def __enter__(self):
        self.monitor.start_monitoring()
        return self.monitor
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.summary = self.monitor.stop_monitoring()
        return False
    
    def get_summary(self) -> Dict:
        """Get the final energy summary."""
        return self.summary

if __name__ == "__main__":
    # Test the energy monitor
    print("Testing Energy Monitor...")
    
    with EnergyTracker(sampling_interval=0.5) as monitor:
        print("Monitoring for 10 seconds...")
        time.sleep(10)
        
        # Show real-time stats
        stats = monitor.get_realtime_stats()
        print(f"Current power: {stats.get('total_power_watts', 0):.1f}W")
    
    # Show final summary
    summary = monitor.get_summary()
    print("\nEnergy Summary:")
    print(f"Duration: {summary.get('duration_seconds', 0):.1f}s")
    print(f"Total Energy: {summary.get('energy', {}).get('total_kwh', 0):.6f} kWh")
    print(f"Average Power: {summary.get('power', {}).get('avg_total_watts', 0):.1f}W")
