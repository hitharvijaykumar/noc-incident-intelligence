"""
Streamlit main entrypoint for AI-Powered NOC Incident Intelligence System.
"""
import streamlit as st
import time

st.set_page_config(
    page_title="NOC Incident Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

from frontend.components.styling import apply_noc_theme
from frontend.components.simulation_controls import render_simulation_controls
from frontend.api_client import check_backend_health

apply_noc_theme()

# Sidebar Header & Brand
st.sidebar.markdown(
    """
    <div style="display:flex; align-items:center; gap:10px; padding: 10px 0;">
        <span style="font-size: 2rem;">🛡️</span>
        <div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #f8fafc; line-height: 1.2;">NOC INTELLIGENCE</div>
            <div style="font-size: 0.75rem; color: #38bdf8; font-weight: 500;">AI INFRASTRUCTURE OPS</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Backend Connectivity Check
health = check_backend_health()
if health and health.get("status") == "HEALTHY":
    st.sidebar.markdown(
        '<div style="font-size:0.75rem; color:#10b981; font-weight:600; margin-bottom:12px;">● BACKEND CONNECTED</div>',
        unsafe_allow_html=True
    )
else:
    st.sidebar.markdown(
        '<div style="font-size:0.75rem; color:#ef4444; font-weight:600; margin-bottom:12px;">▲ BACKEND DISCONNECTED (Run run_backend.py)</div>',
        unsafe_allow_html=True
    )

# Render Global Simulation Controls
render_simulation_controls()

# Main landing info if directly viewing app.py
st.title("🛡️ AI-Powered Network Operations Center (NOC)")
st.subheader("Autonomous Incident Intelligence & Anomaly Detection Platform")

st.markdown(
    """
    Welcome to the enterprise **AI-Powered Network Operations Center (NOC)**.
    This platform continuously monitors distributed servers and network topology, leverages machine learning
    to predict incident categories, flags zero-day anomalies via Isolation Forests, groups failure modes with K-Means,
    and provides advisory troubleshooting workflows for site reliability and NOC engineers.

    ### 📍 Navigation Guide
    - **1 Overview**: Real-time cluster health summary, live telemetry trends, active incidents, and high-level KPIs.
    - **2 Live Monitoring**: Granular time-series metric explorer with operational warning and critical thresholds.
    - **3 Incident Management**: Comprehensive incident triage, ML confidence scores, root cause hypotheses, and remediation actions.
    - **4 AI Insights**: Model evaluation metrics, Random Forest confusion matrix, feature importance, and cluster centroids.
    - **5 Analytics**: MTTA, MTTR, resolution rates, failure categorization, and problematic device ranking.
    - **6 Device Management**: Topology inventory across servers, switches, routers, and firewalls.

    ---
    👉 **Select a dashboard page from the sidebar menu to begin.**
    """
)

# Quick Status Preview
st.markdown("### 📡 Current System Status")
col1, col2, col3 = st.columns(3)
with col1:
    st.info("**Backend Gateway:** http://127.0.0.1:8000")
with col2:
    st.info("**API Documentation:** http://127.0.0.1:8000/docs")
with col3:
    st.info(f"**Backend Status:** {'ONLINE' if health else 'OFFLINE'}")
