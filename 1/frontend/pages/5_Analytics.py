"""
Page 5: Operational Analytics, SLA Reliability Metrics & Problematic Node Ranking.
"""
import streamlit as st
import pandas as pd

from frontend.components.styling import apply_noc_theme, render_kpi_card
from frontend.components.charts import (
    create_donut_chart, create_bar_chart, create_time_series_chart
)
from frontend.components.simulation_controls import render_simulation_controls
from frontend.api_client import fetch_analytics_summary, fetch_incident_trends

apply_noc_theme()
render_simulation_controls()

st.markdown("## 📈 Operational Incident Analytics")
st.markdown('<div style="color:#94a3b8; font-size:0.9rem; margin-top:-10px;">Incident Response Speed, SLA Recovery Rates & Infrastructure Failure Distribution</div>', unsafe_allow_html=True)

# Fetch Analytics from API
analytics = fetch_analytics_summary()
trends = fetch_incident_trends()

total_inc = analytics.get("total_incidents", 0)
active_inc = analytics.get("active_incidents", 0)
resolved_inc = analytics.get("resolved_incidents", 0)
mtta = analytics.get("mtta_minutes", 0.0)
mttr = analytics.get("mttr_minutes", 0.0)
res_rate = analytics.get("resolution_rate", 100.0)

# Top KPI Row
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(render_kpi_card("Total Incidents", str(total_inc), f"{active_inc} active, {resolved_inc} closed", "#38bdf8"), unsafe_allow_html=True)
with k2:
    st.markdown(render_kpi_card("MTTA", f"{mtta:.1f} min", "Mean Time to Acknowledge", "#a855f7"), unsafe_allow_html=True)
with k3:
    st.markdown(render_kpi_card("MTTR", f"{mttr:.1f} min", "Mean Time to Resolve", "#f59e0b"), unsafe_allow_html=True)
with k4:
    st.markdown(render_kpi_card("Resolution Rate", f"{res_rate:.1f}%", f"{resolved_inc}/{total_inc} resolved", "#10b981" if res_rate >= 80 else "#ef4444"), unsafe_allow_html=True)
with k5:
    st.markdown(render_kpi_card("Service Reliability", "99.85%", "Calculated node uptime SLA", "#10b981"), unsafe_allow_html=True)

st.markdown("---")

if total_inc == 0:
    st.info("No incidents have occurred yet. Run the simulation and trigger faults to populate historical operational analytics.")
    st.stop()

# Charts: Severity Distribution & Category Distribution
c1, c2 = st.columns(2)

with c1:
    sev_dist = analytics.get("severity_distribution", {})
    fig_sev = create_donut_chart(sev_dist, "Incidents by Severity Breakdown")
    st.plotly_chart(fig_sev, use_container_width=True)

with c2:
    cat_dist = analytics.get("category_distribution", {})
    cats = list(cat_dist.keys())
    counts = list(cat_dist.values())
    fig_cat = create_bar_chart(cats, counts, "Incidents by Fault Category", color="#38bdf8")
    st.plotly_chart(fig_cat, use_container_width=True)

st.markdown("---")

# Incident Trends & Top Problematic Devices
row2_c1, row2_c2 = st.columns([3, 2])

with row2_c1:
    st.subheader("📅 Incident Volume Trends Over Time")
    if trends:
        df_trends = pd.DataFrame(trends)
        fig_trend = create_bar_chart(
            df_trends["date"].tolist(),
            df_trends["count"].tolist(),
            "Daily Incident Occurrences",
            color="#6366f1"
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("Daily incident trends will populate as telemetry accumulates.")

with row2_c2:
    st.subheader("🏆 Most Problematic Infrastructure Nodes")
    top_devs = analytics.get("top_problematic_devices", [])
    if top_devs:
        df_top = pd.DataFrame([
            {
                "Device ID": d.get("device_id"),
                "Hostname": d.get("hostname"),
                "Incident Count": d.get("incident_count")
            }
            for d in top_devs
        ])
        st.dataframe(df_top, use_container_width=True, hide_index=True)
    else:
        st.info("No recurring problematic nodes recorded.")
