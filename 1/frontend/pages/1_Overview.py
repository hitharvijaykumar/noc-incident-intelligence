"""
Page 1: NOC Operations Overview Dashboard.
"""
import streamlit as st
import pandas as pd
import time

from frontend.components.styling import apply_noc_theme, get_severity_badge, get_status_badge
from frontend.components.metrics import render_top_kpis
from frontend.components.charts import (
    create_time_series_chart, create_donut_chart
)
from frontend.components.simulation_controls import render_simulation_controls
from frontend.api_client import (
    fetch_monitoring_summary, fetch_analytics_summary,
    fetch_monitoring_history, fetch_incidents, fetch_devices
)

apply_noc_theme()
render_simulation_controls()

# Page Header
col_title, col_ctrl = st.columns([4, 1])
with col_title:
    st.markdown("## 🌐 NOC Operations Overview")
    st.markdown('<div style="color:#94a3b8; font-size:0.9rem; margin-top:-10px;">Enterprise Cluster Health, Global Telemetry & Incident Intelligence</div>', unsafe_allow_html=True)

with col_ctrl:
    auto_refresh = st.checkbox("Auto Refresh (5s)", value=False, key="overview_auto_refresh")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

# 1. Fetch Summary Data
summary = fetch_monitoring_summary()
analytics = fetch_analytics_summary()
devices = fetch_devices()
incidents = fetch_incidents(limit=10)
history = fetch_monitoring_history(limit=60)

# Render Top KPIs
render_top_kpis(summary, analytics)

st.markdown("---")

# 2. Charts Row: Trends & Severity Breakdown
col_charts, col_donut = st.columns([3, 1])

with col_charts:
    df_hist = pd.DataFrame(history)
    if not df_hist.empty and "timestamp" in df_hist.columns:
        df_hist["time"] = pd.to_datetime(df_hist["timestamp"]).dt.strftime("%H:%M:%S")

        t1, t2 = st.tabs(["CPU & Memory Utilization", "Network Latency & Packet Loss"])
        with t1:
            c1, c2 = st.columns(2)
            with c1:
                fig_cpu = create_time_series_chart(
                    df_hist, "time", "cpu_utilization", "CPU Utilization Trend", "%",
                    warning_thresh=70.0, critical_thresh=85.0, line_color="#38bdf8"
                )
                st.plotly_chart(fig_cpu, use_container_width=True)
            with c2:
                fig_mem = create_time_series_chart(
                    df_hist, "time", "memory_utilization", "Memory Utilization Trend", "%",
                    warning_thresh=75.0, critical_thresh=90.0, line_color="#a855f7"
                )
                st.plotly_chart(fig_mem, use_container_width=True)
        with t2:
            c3, c4 = st.columns(2)
            with c3:
                fig_lat = create_time_series_chart(
                    df_hist, "time", "network_latency", "Network Latency Trend", "ms",
                    warning_thresh=100.0, critical_thresh=200.0, line_color="#f59e0b"
                )
                st.plotly_chart(fig_lat, use_container_width=True)
            with c4:
                fig_loss = create_time_series_chart(
                    df_hist, "time", "packet_loss", "Packet Loss Trend", "%",
                    warning_thresh=1.0, critical_thresh=5.0, line_color="#ef4444"
                )
                st.plotly_chart(fig_loss, use_container_width=True)
    else:
        st.info("Awaiting telemetry history from simulator... Ensure simulation monitoring is running.")

with col_donut:
    sev_dist = analytics.get("severity_distribution", {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0})
    fig_donut = create_donut_chart(sev_dist, "Active Incident Severity")
    st.plotly_chart(fig_donut, use_container_width=True)

# 3. Bottom Row: Recent Incidents Feed & Device Status Quick Matrix
col_inc, col_dev = st.columns([3, 2])

with col_inc:
    st.subheader("🚨 Recent Incident Feed")
    if incidents:
        for inc in incidents[:5]:
            sev_badge = get_severity_badge(inc.get("severity", "LOW"))
            stat_badge = get_status_badge(inc.get("status", "NEW"))
            conf = f"{inc.get('confidence_score', 0)*100:.0f}%"
            st.markdown(
                f"""
                <div style="background-color:#111827; border:1px solid #1f2937; border-left:4px solid {'#ef4444' if inc.get('severity')=='CRITICAL' else '#f97316'}; border-radius:6px; padding:12px 16px; margin-bottom:8px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:600; font-size:0.95rem; color:#f8fafc;">{inc.get('incident_title')}</span>
                        <div>{sev_badge} {stat_badge}</div>
                    </div>
                    <div style="font-size:0.8rem; color:#94a3b8; margin-top:4px;">
                        Device: <b style="color:#e2e8f0;">{inc.get('affected_device')}</b> | Category: <b style="color:#38bdf8;">{inc.get('incident_category')}</b> | ML Confidence: <b style="color:#e2e8f0;">{conf}</b>
                    </div>
                    <div style="font-size:0.8rem; color:#64748b; margin-top:4px;">
                        {inc.get('root_cause_hypothesis', '')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.success("✅ No active incidents detected. All nodes operating normally.")

with col_dev:
    st.subheader("🖥️ Device Health Status")
    if devices:
        for dev in devices[:6]:
            h_stat = dev.get("health_status", "HEALTHY")
            color = "#10b981" if h_stat == "HEALTHY" else ("#ef4444" if h_stat == "CRITICAL" else "#f97316")
            cpu_val = dev.get("latest_cpu", 0.0)
            lat_val = dev.get("latest_latency", 0.0)
            st.markdown(
                f"""
                <div style="display:flex; justify-content:space-between; align-items:center; background:#111827; border:1px solid #1f2937; border-radius:6px; padding:8px 12px; margin-bottom:6px;">
                    <div>
                        <div style="font-weight:600; font-size:0.85rem; color:#f8fafc;">{dev.get('hostname')}</div>
                        <div style="font-size:0.75rem; color:#64748b;">{dev.get('device_type').upper()} • {dev.get('location')}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:0.75rem; color:#94a3b8;">CPU: <b style="color:#e2e8f0;">{cpu_val}%</b> | Lat: <b style="color:#e2e8f0;">{lat_val}ms</b></div>
                        <span style="font-size:0.7rem; font-weight:700; color:{color};">{h_stat}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("Loading device fleet...")

if auto_refresh:
    time.sleep(5)
    st.rerun()
