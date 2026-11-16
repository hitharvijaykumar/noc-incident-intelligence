"""
Page 2: Live Infrastructure Telemetry Monitoring.
"""
import streamlit as st
import pandas as pd
import time

from frontend.components.styling import apply_noc_theme, render_kpi_card
from frontend.components.charts import create_time_series_chart
from frontend.components.simulation_controls import render_simulation_controls
from frontend.api_client import fetch_devices, fetch_device_metrics

apply_noc_theme()
render_simulation_controls()

st.markdown("## 📊 Live Infrastructure Telemetry")
st.markdown('<div style="color:#94a3b8; font-size:0.9rem; margin-top:-10px;">High-Frequency Telemetry Stream & Threshold SLA Monitoring</div>', unsafe_allow_html=True)

# Device Filter and Options
devices = fetch_devices()
if not devices:
    st.warning("No monitored devices found. Ensure the backend is active.")
    st.stop()

col_filt1, col_filt2, col_filt3 = st.columns([2, 1, 1])

with col_filt1:
    device_options = {f"{d['id']} — {d['hostname']} ({d['device_type'].upper()})": d['id'] for d in devices}
    selected_label = st.selectbox("Select Monitored Device", list(device_options.keys()), key="live_dev_select")
    selected_device_id = device_options[selected_label]

with col_filt2:
    points_limit = st.selectbox("Time Window (Samples)", [20, 50, 100, 200], index=1, key="live_points_limit")

with col_filt3:
    auto_refresh = st.checkbox("Live Auto-Refresh (3s)", value=True, key="live_auto_refresh")

# Fetch Device Telemetry
metrics = fetch_device_metrics(selected_device_id, limit=points_limit)
df = pd.DataFrame(metrics)

if df.empty:
    st.info(f"Awaiting telemetry history for device {selected_device_id}...")
    if auto_refresh:
        time.sleep(3)
        st.rerun()
    st.stop()

# Time column formatting
df["time"] = pd.to_datetime(df["timestamp"]).dt.strftime("%H:%M:%S")

# Latest snapshot values
latest = df.iloc[-1]

# Metric Highlights Banner
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(render_kpi_card("Current CPU", f"{latest.get('cpu_utilization', 0):.1f}%", f"Uptime: {latest.get('server_uptime', 0):.1f}h", "#38bdf8"), unsafe_allow_html=True)
with c2:
    st.markdown(render_kpi_card("Current RAM", f"{latest.get('memory_utilization', 0):.1f}%", f"Threads: {latest.get('process_count', 0)}", "#a855f7"), unsafe_allow_html=True)
with c3:
    st.markdown(render_kpi_card("Disk Storage", f"{latest.get('disk_utilization', 0):.1f}%", "Block usage", "#f59e0b"), unsafe_allow_html=True)
with c4:
    st.markdown(render_kpi_card("Latency", f"{latest.get('network_latency', 0):.1f} ms", f"Resp: {latest.get('response_time', 0):.1f}ms", "#3b82f6"), unsafe_allow_html=True)
with c5:
    st.markdown(render_kpi_card("Packet Loss", f"{latest.get('packet_loss', 0):.2f}%", f"BW: {latest.get('bandwidth_utilization', 0):.1f}%", "#ef4444" if latest.get('packet_loss', 0) > 1 else "#10b981"), unsafe_allow_html=True)

st.markdown("---")

# Time-series Charts Grid
row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    fig_cpu = create_time_series_chart(
        df, "time", "cpu_utilization", "CPU Utilization (%)", "%",
        warning_thresh=70.0, critical_thresh=85.0, line_color="#38bdf8"
    )
    st.plotly_chart(fig_cpu, use_container_width=True)

with row1_col2:
    fig_mem = create_time_series_chart(
        df, "time", "memory_utilization", "Memory Utilization (%)", "%",
        warning_thresh=75.0, critical_thresh=90.0, line_color="#a855f7"
    )
    st.plotly_chart(fig_mem, use_container_width=True)

row2_col1, row2_col2 = st.columns(2)
with row2_col1:
    fig_lat = create_time_series_chart(
        df, "time", "network_latency", "Network Latency (ms)", "ms",
        warning_thresh=100.0, critical_thresh=200.0, line_color="#f59e0b"
    )
    st.plotly_chart(fig_lat, use_container_width=True)

with row2_col2:
    fig_loss = create_time_series_chart(
        df, "time", "packet_loss", "Packet Loss (%)", "%",
        warning_thresh=1.0, critical_thresh=5.0, line_color="#ef4444"
    )
    st.plotly_chart(fig_loss, use_container_width=True)

row3_col1, row3_col2 = st.columns(2)
with row3_col1:
    fig_disk = create_time_series_chart(
        df, "time", "disk_utilization", "Disk Capacity Utilization (%)", "%",
        warning_thresh=80.0, critical_thresh=90.0, line_color="#10b981"
    )
    st.plotly_chart(fig_disk, use_container_width=True)

with row3_col2:
    fig_bw = create_time_series_chart(
        df, "time", "bandwidth_utilization", "Network Bandwidth Utilization (%)", "%",
        warning_thresh=85.0, critical_thresh=95.0, line_color="#6366f1"
    )
    st.plotly_chart(fig_bw, use_container_width=True)

if auto_refresh:
    time.sleep(3)
    st.rerun()
