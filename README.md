# Carbon-Aware Machine Learning 🌱

A Python framework for training machine learning models with carbon footprint awareness. This project automatically schedules ML training during low carbon intensity periods and optimizes model configurations to reduce environmental impact.

## 🌟 Features

- **Real-time Carbon Monitoring**: Fetches live carbon intensity data from ElectricityMaps API
- **Intelligent Scheduling**: Trains models only during low-carbon periods
- **Dynamic Optimization**: Adjusts training parameters based on grid carbon intensity
- **Energy Tracking**: Monitors and logs estimated energy consumption
- **Flexible Configuration**: Easy YAML-based configuration system

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- ElectricityMaps API key (optional - includes mock mode)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/pibuilt/carbonawareML.git
   cd carbonawareML
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the system**
   ```bash
   cp configs/config.example.yaml configs/config.yaml
   ```
   Edit `configs/config.yaml` with your ElectricityMaps API key.

### Usage

**Run the complete carbon-aware training pipeline:**
```bash
python main.py
```

**Test individual components:**
```bash
# Check carbon intensity
python -m data_pipeline.carbon_intensity

# Test scheduler
python -m scheduler.scheduler

# Run tests
python run_tests.py
```

## 📊 How It Works

1. **Carbon Intensity Check**: Fetches current grid carbon intensity
2. **Time Window Validation**: Ensures training happens during configured hours
3. **Go/No-Go Decision**: Compares carbon levels against thresholds
4. **Dynamic Optimization**: Adjusts batch size and precision based on carbon cost
5. **Model Training**: Executes training with optimized parameters
6. **Energy Logging**: Tracks estimated carbon footprint

## 🔧 Configuration

Edit `configs/config.yaml` to customize:

- **Carbon API**: Provider, API key, and region settings
- **Training Window**: Allowed hours for training
- **Carbon Thresholds**: Minimum and maximum acceptable carbon intensity
- **Model Parameters**: Default training configuration

