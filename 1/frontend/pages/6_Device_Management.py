"""
Page 6: Infrastructure Inventory & Device Topology Management.
"""
import streamlit as st
import pandas as pd

from frontend.components.styling import apply_noc_theme, render_kpi_card, get_status_badge
from frontend.components.tables import format_device_table_data
from frontend.components.simulation_controls import render_simulation_controls
from frontend.api_client import fetch_devices, fetch_device, fetch_device_metrics

apply_noc_theme()
render_simulation_controls()

st.markdown("## 🖥️ Infrastructure Device Management")
st.markdown('<div style="color:#94a3b8; font-size:0.9rem; margin-top:-10px;">Network Topology Inventory, Node Provisioning & Live Hardware Status</div>', unsafe_allow_html=True)

# 1. Fetch Fleet
devices = fetch_devices()
if not devices:
    st.warning("No devices found in infrastructure database.")
    st.stop()

# 2. Filtering
f_col1, f_col2, f_col3 = st.columns(3)
with f_col1:
    type_options = ["All"] + sorted(list(set(d.get("device_type", "").upper() for d in devices)))
    selected_type = st.selectbox("Filter Device Type", type_options, key="dev_type_filter")
with f_col2:
    status_options = ["All"] + sorted(list(set(d.get("status", "") for d in devices)))
    selected_status = st.selectbox("Filter Operating Status", status_options, key="dev_status_filter")
with f_col3:
    loc_options = ["All"] + sorted(list(set(d.get("location", "") for d in devices)))
    selected_loc = st.selectbox("Filter Datacenter Location", loc_options, key="dev_loc_filter")

filtered_devs = devices
if selected_type != "All":
    filtered_devs = [d for d in filtered_devs if d.get("device_type", "").upper() == selected_type]
if selected_status != "All":
    filtered_devs = [d for d in filtered_devs if d.get("status") == selected_status]
if selected_loc != "All":
    filtered_devs = [d for d in filtered_devs if d.get("location") == selected_loc]

# Inventory Table
df_devs = format_device_table_data(filtered_devs)
st.dataframe(df_devs, use_container_width=True, hide_index=True)

st.markdown("---")

# 3. Individual Node Drill-down
st.subheader("🔍 Node Diagnostic Inspector")
device_choices = [f"{d['id']} — {d['hostname']}" for d in filtered_devs]
if device_choices:
    sel_choice = st.selectbox("Select Node for Deep Inspection", device_choices, key="dev_inspect_select")
    target_id = sel_choice.split(" ")[0]
    dev_info = fetch_device(target_id)

    if dev_info:
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.markdown(f"**Device ID:** `{dev_info.get('id')}`")
            st.markdown(f"**Hostname:** `{dev_info.get('hostname')}`")
        with d2:
            st.markdown(f"**Role/Type:** `{dev_info.get('device_type').upper()}`")
            st.markdown(f"**IP Address:** `{dev_info.get('ip_address')}`")
        with d3:
            st.markdown(f"**Datacenter:** `{dev_info.get('location')}`")
            st.markdown(f"**Operating Status:** {get_status_badge(dev_info.get('status', 'ONLINE'))}", unsafe_allow_html=True)
        with d4:
            hb = dev_info.get("last_heartbeat", "")[:19].replace("T", " ")
            st.markdown(f"**Last Heartbeat:** `{hb} UTC`")
            st.markdown(f"**Health Assessment:** `{dev_info.get('health_status')}`")

        st.markdown("##### Recent Metric Snapshot")
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.metric("CPU Load", f"{dev_info.get('latest_cpu', 0):.1f}%")
        with s2:
            st.metric("Memory Usage", f"{dev_info.get('latest_memory', 0):.1f}%")
        with s3:
            st.metric("Disk Storage", f"{dev_info.get('latest_disk', 0):.1f}%")
        with s4:
            st.metric("Roundtrip Latency", f"{dev_info.get('latest_latency', 0):.1f} ms")
