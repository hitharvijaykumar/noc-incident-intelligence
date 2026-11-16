"""
Top-level NOC KPI cards and metric summaries.
"""
import streamlit as st
from frontend.components.styling import render_kpi_card

def render_top_kpis(summary_data: dict, incident_summary: dict):
    total_dev = summary_data.get("total_devices", 0)
    online_dev = summary_data.get("online_devices", 0)
    avail_pct = round((online_dev / total_dev * 100), 1) if total_dev > 0 else 100.0

    active_inc = incident_summary.get("active_incidents", 0)
    crit_inc = incident_summary.get("severity_distribution", {}).get("CRITICAL", 0)
    active_alt = summary_data.get("active_critical_alerts", 0)

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.markdown(render_kpi_card("Total Devices", f"{total_dev}", "Simulated nodes", "#38bdf8"), unsafe_allow_html=True)
    with col2:
        st.markdown(render_kpi_card("Healthy Nodes", f"{online_dev}/{total_dev}", f"{avail_pct}% reachable", "#10b981"), unsafe_allow_html=True)
    with col3:
        st.markdown(render_kpi_card("Active Incidents", f"{active_inc}", "Awaiting resolution", "#ef4444" if active_inc > 0 else "#10b981"), unsafe_allow_html=True)
    with col4:
        st.markdown(render_kpi_card("Critical Incidents", f"{crit_inc}", "High severity priority", "#ef4444" if crit_inc > 0 else "#64748b"), unsafe_allow_html=True)
    with col5:
        st.markdown(render_kpi_card("Active Alerts", f"{active_alt}", "Rule engine triggers", "#f59e0b" if active_alt > 0 else "#64748b"), unsafe_allow_html=True)
    with col6:
        st.markdown(render_kpi_card("Availability", f"{avail_pct}%", "Target SLA: 99.9%", "#10b981" if avail_pct >= 99.0 else "#f97316"), unsafe_allow_html=True)
