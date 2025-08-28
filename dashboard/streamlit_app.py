"""
Carbon-Aware ML Dashboard
A Streamlit web interface for monitoring and controlling carbon-aware ML training.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import time
import threading
from datetime import datetime, timedelta
import json
from typing import Dict, List

# Local imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.energy_monitor import EnergyMonitor, EnergyTracker
from utils.carbon_calculator import CarbonCalculator, CarbonAwareTrainingSession
from data_pipeline.carbon_intensity import get_carbon_intensity, load_config
from scheduler.scheduler import schedule_training
from utils.logger import get_logger

# Configure page
st.set_page_config(
    page_title="Carbon-Aware ML Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'energy_monitor' not in st.session_state:
    st.session_state.energy_monitor = None
if 'monitoring_active' not in st.session_state:
    st.session_state.monitoring_active = False
if 'training_history' not in st.session_state:
    st.session_state.training_history = []

# Initialize components
@st.cache_resource
def get_carbon_calculator():
    """Get cached carbon calculator instance."""
    return CarbonCalculator()

def get_current_carbon_intensity():
    """Get current carbon intensity with caching."""
    return get_carbon_intensity()

def get_training_recommendation():
    """Get current training recommendation."""
    return schedule_training()

# Sidebar Configuration
st.sidebar.title("🌱 Carbon-Aware ML")
st.sidebar.markdown("---")

# Configuration section
st.sidebar.subheader("⚙️ Configuration")
config = load_config()

# Carbon intensity settings
st.sidebar.markdown("**Carbon Intensity Thresholds**")
min_ci = st.sidebar.slider(
    "Minimum (Optimal)", 
    50, 300, 
    config['train']['min_carbon_intensity'],
    help="Below this threshold, training is optimal"
)

max_ci = st.sidebar.slider(
    "Maximum (Acceptable)", 
    200, 800, 
    config['train']['max_carbon_intensity'],
    help="Above this threshold, training should be avoided"
)

# Time window settings
st.sidebar.markdown("**Training Time Window**")
earliest_hour = st.sidebar.slider("Earliest Hour", 0, 23, config['train']['earliest_start_hour'])
latest_hour = st.sidebar.slider("Latest Hour", 0, 23, config['train']['latest_start_hour'])

# Auto-refresh settings
st.sidebar.markdown("**Dashboard Settings**")
auto_refresh = st.sidebar.checkbox("Auto-refresh", value=True)
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 5, 60, 10)

# Main Dashboard
st.title("🌱 Carbon-Aware Machine Learning Dashboard")
st.markdown("Monitor and control your ML training with real-time carbon footprint awareness")

# Real-time metrics row
col1, col2, col3, col4 = st.columns(4)

# Get current metrics
current_ci = get_current_carbon_intensity()
training_ok = get_training_recommendation()
current_time = datetime.now()

with col1:
    if current_ci is not None:
        # Color code based on thresholds
        if current_ci < min_ci:
            ci_color = "🟢"
            ci_status = "Optimal"
        elif current_ci < max_ci:
            ci_color = "🟡"
            ci_status = "Acceptable"
        else:
            ci_color = "🔴"
            ci_status = "High"
        
        st.metric(
            label=f"{ci_color} Carbon Intensity",
            value=f"{current_ci:.0f} gCO2eq/kWh",
            help=f"Status: {ci_status}"
        )
    else:
        st.metric(
            label="⚪ Carbon Intensity",
            value="N/A",
            help="Unable to fetch current data"
        )

with col2:
    training_status = "✅ Go" if training_ok else "⏸️ Wait"
    training_color = "normal" if training_ok else "inverse"
    st.metric(
        label="Training Recommendation",
        value=training_status,
        help="Based on carbon intensity and time window"
    )

with col3:
    current_hour = current_time.hour
    in_window = earliest_hour <= current_hour <= latest_hour
    window_status = "✅ Open" if in_window else "🔒 Closed"
    st.metric(
        label="Time Window",
        value=window_status,
        help=f"Current hour: {current_hour}, Window: {earliest_hour}-{latest_hour}"
    )

with col4:
    # Energy monitoring status
    if st.session_state.monitoring_active:
        st.metric(
            label="Energy Monitor",
            value="🔋 Active",
            help="Real-time energy monitoring is running"
        )
    else:
        st.metric(
            label="Energy Monitor",
            value="⭕ Inactive",
            help="Energy monitoring is stopped"
        )

st.markdown("---")

# Tab layout
tab1, tab2, tab3, tab4 = st.tabs(["📊 Real-time Monitoring", "🎯 Training Control", "📈 Analytics", "⚙️ Settings"])

with tab1:
    st.subheader("Real-time Carbon & Energy Monitoring")
    
    # Real-time charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Carbon Intensity Trend**")
        # Create sample data for demonstration
        if current_ci is not None:
            times = [datetime.now() - timedelta(minutes=x) for x in range(60, 0, -5)]
            # Simulate some variation around current value
            import random
            ci_values = [current_ci + random.randint(-20, 20) for _ in times]
            
            fig_ci = go.Figure()
            fig_ci.add_trace(go.Scatter(
                x=times,
                y=ci_values,
                mode='lines+markers',
                name='Carbon Intensity',
                line=dict(color='green' if current_ci < min_ci else 'orange' if current_ci < max_ci else 'red')
            ))
            
            # Add threshold lines
            fig_ci.add_hline(y=min_ci, line_dash="dash", line_color="green", 
                           annotation_text="Optimal Threshold")
            fig_ci.add_hline(y=max_ci, line_dash="dash", line_color="red", 
                           annotation_text="Max Threshold")
            
            fig_ci.update_layout(
                xaxis_title="Time",
                yaxis_title="gCO2eq/kWh",
                height=300,
                showlegend=False
            )
            st.plotly_chart(fig_ci, use_container_width=True)
        else:
            st.info("Carbon intensity data unavailable")
    
    with col2:
        st.markdown("**Energy Consumption**")
        if st.session_state.monitoring_active and st.session_state.energy_monitor:
            try:
                stats = st.session_state.energy_monitor.get_realtime_stats()
                if stats:
                    # Create energy consumption chart
                    fig_energy = go.Figure()
                    
                    # Power breakdown
                    categories = ['CPU', 'GPU', 'Total']
                    values = [
                        stats.get('cpu_power_watts', 0),
                        stats.get('gpu_power_watts', 0),
                        stats.get('total_power_watts', 0)
                    ]
                    
                    fig_energy.add_trace(go.Bar(
                        x=categories,
                        y=values,
                        marker_color=['lightblue', 'lightgreen', 'lightcoral']
                    ))
                    
                    fig_energy.update_layout(
                        xaxis_title="Component",
                        yaxis_title="Power (Watts)",
                        height=300,
                        showlegend=False
                    )
                    st.plotly_chart(fig_energy, use_container_width=True)
                    
                    # Show current stats
                    st.markdown("**Current Statistics:**")
                    st.write(f"• CPU Power: {stats.get('cpu_power_watts', 0):.1f}W")
                    st.write(f"• GPU Power: {stats.get('gpu_power_watts', 0):.1f}W")
                    st.write(f"• CPU Utilization: {stats.get('cpu_utilization', 0):.1f}%")
                    st.write(f"• GPU Utilization: {stats.get('gpu_utilization', 0):.1f}%")
                else:
                    st.info("No energy data available yet")
            except Exception as e:
                st.error(f"Error getting energy stats: {e}")
        else:
            st.info("Energy monitoring not active. Start monitoring to see real-time data.")

with tab2:
    st.subheader("Training Control Center")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**Energy Monitoring Control**")
        
        col_start, col_stop = st.columns(2)
        
        with col_start:
            if st.button("🔋 Start Energy Monitoring", disabled=st.session_state.monitoring_active):
                try:
                    st.session_state.energy_monitor = EnergyMonitor(sampling_interval=1.0)
                    st.session_state.energy_monitor.start_monitoring()
                    st.session_state.monitoring_active = True
                    st.success("Energy monitoring started!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to start monitoring: {e}")
        
        with col_stop:
            if st.button("⏹️ Stop Energy Monitoring", disabled=not st.session_state.monitoring_active):
                try:
                    if st.session_state.energy_monitor:
                        summary = st.session_state.energy_monitor.stop_monitoring()
                        st.session_state.monitoring_active = False
                        
                        # Calculate carbon footprint
                        calculator = get_carbon_calculator()
                        footprint = calculator.calculate_footprint(summary)
                        
                        # Store in history
                        st.session_state.training_history.append({
                            'timestamp': datetime.now(),
                            'duration_hours': summary.get('duration_hours', 0),
                            'energy_kwh': summary.get('energy', {}).get('total_kwh', 0),
                            'co2_kg': footprint.total_co2_kg,
                            'avg_power_watts': summary.get('power', {}).get('avg_total_watts', 0)
                        })
                        
                        st.success(f"Monitoring stopped! Carbon footprint: {footprint.total_co2_kg:.6f} kg CO2")
                        st.rerun()
                except Exception as e:
                    st.error(f"Failed to stop monitoring: {e}")
        
        # Training simulation
        st.markdown("**Simulated Training Session**")
        if st.button("🚀 Start Simulated Training", disabled=st.session_state.monitoring_active):
            if not training_ok:
                st.warning("⚠️ Training not recommended due to high carbon intensity or time window restrictions!")
                if st.button("🔴 Force Start Training"):
                    st.info("Starting training despite recommendations...")
            else:
                with st.spinner("Running simulated training session..."):
                    # Simulate training with energy tracking
                    try:
                        with CarbonAwareTrainingSession("Dashboard Training", sampling_interval=0.5) as monitor:
                            progress_bar = st.progress(0)
                            for i in range(10):
                                time.sleep(0.5)
                                progress_bar.progress((i + 1) / 10)
                                # Simulate some computation
                                _ = sum(x**2 for x in range(1000))
                        
                        # Get results
                        session = CarbonAwareTrainingSession("Dashboard Training")
                        footprint = session.get_carbon_footprint()
                        if footprint:
                            st.success(f"Training completed! Carbon footprint: {footprint.total_co2_kg:.6f} kg CO2")
                            
                            # Show equivalents
                            equivalents = session.get_equivalents()
                            with st.expander("🌍 Environmental Impact"):
                                for key, value in equivalents.items():
                                    st.write(f"• {key.replace('_', ' ').title()}: {value}")
                        
                    except Exception as e:
                        st.error(f"Training simulation failed: {e}")
    
    with col2:
        st.markdown("**Quick Actions**")
        
        if st.button("🔄 Refresh Carbon Data"):
            st.rerun()
        
        if st.button("📊 Check Training Recommendation"):
            rec = get_training_recommendation()
            if rec:
                st.success("✅ Training recommended!")
            else:
                st.warning("⏸️ Training not recommended")
        
        st.markdown("**Carbon Budget**")
        daily_budget = st.number_input("Daily CO2 Budget (kg)", value=0.1, step=0.01)
        
        # Calculate today's usage
        today_usage = sum(
            session['co2_kg'] for session in st.session_state.training_history
            if session['timestamp'].date() == datetime.now().date()
        )
        
        budget_used = (today_usage / daily_budget) * 100 if daily_budget > 0 else 0
        
        st.metric(
            label="Budget Used Today",
            value=f"{budget_used:.1f}%",
            delta=f"{today_usage:.6f} kg CO2"
        )
        
        # Budget progress bar
        st.progress(min(budget_used / 100, 1.0))

with tab3:
    st.subheader("Training Analytics & History")
    
    if st.session_state.training_history:
        # Convert to DataFrame
        df = pd.DataFrame(st.session_state.training_history)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Carbon Footprint Over Time**")
            fig_history = go.Figure()
            fig_history.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['co2_kg'],
                mode='lines+markers',
                name='CO2 Emissions (kg)'
            ))
            fig_history.update_layout(
                xaxis_title="Time",
                yaxis_title="CO2 Emissions (kg)",
                height=300
            )
            st.plotly_chart(fig_history, use_container_width=True)
        
        with col2:
            st.markdown("**Energy vs Carbon Intensity**")
            if current_ci:
                fig_scatter = go.Figure()
                fig_scatter.add_trace(go.Scatter(
                    x=df['energy_kwh'],
                    y=df['co2_kg'],
                    mode='markers',
                    marker=dict(size=df['duration_hours']*20, opacity=0.6)
                ))
                fig_scatter.update_layout(
                    xaxis_title="Energy Consumption (kWh)",
                    yaxis_title="CO2 Emissions (kg)",
                    height=300
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Summary statistics
        st.markdown("**Session Summary**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Sessions", len(df))
        with col2:
            st.metric("Total Energy", f"{df['energy_kwh'].sum():.4f} kWh")
        with col3:
            st.metric("Total CO2", f"{df['co2_kg'].sum():.4f} kg")
        with col4:
            st.metric("Avg Power", f"{df['avg_power_watts'].mean():.1f} W")
        
        # Detailed history table
        with st.expander("📋 Detailed Session History"):
            st.dataframe(df, use_container_width=True)
        
    else:
        st.info("No training history available. Run some training sessions to see analytics.")

with tab4:
    st.subheader("System Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Current Configuration**")
        st.json(config)
        
        if st.button("💾 Export Configuration"):
            config_json = json.dumps(config, indent=2)
            st.download_button(
                label="Download config.yaml",
                data=config_json,
                file_name="config.yaml",
                mime="application/json"
            )
    
    with col2:
        st.markdown("**System Information**")
        
        # Get system info
        if st.session_state.energy_monitor:
            summary = st.session_state.energy_monitor.get_summary()
            system_info = summary.get('system', {})
        else:
            system_info = {}
        
        st.write(f"**Platform:** {system_info.get('platform', 'Unknown')}")
        st.write(f"**GPU Available:** {system_info.get('gpu_available', 'Unknown')}")
        st.write(f"**CPU TDP:** {system_info.get('cpu_tdp_watts', 'Unknown')} W")
        
        # Test connections
        st.markdown("**Connection Tests**")
        if st.button("🧪 Test Carbon API"):
            with st.spinner("Testing carbon intensity API..."):
                ci = get_current_carbon_intensity()
                if ci is not None:
                    st.success(f"✅ API working! Current CI: {ci} gCO2eq/kWh")
                else:
                    st.error("❌ API connection failed")

# Auto-refresh functionality
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "🌱 **Carbon-Aware ML Dashboard** | "
    "Built for sustainable AI training | "
    f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)
