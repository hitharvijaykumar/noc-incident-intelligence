"""
Interactive Simulation Control Panel component for sidebar or modal.
"""
import streamlit as st
from frontend.api_client import (
    fetch_simulation_status, start_simulation, stop_simulation,
    set_simulation_mode, trigger_simulation_incident, fetch_devices
)

def render_simulation_controls():
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎮 Simulation Engine")

    status = fetch_simulation_status()
    is_running = status.get("is_running", False)
    current_mode = status.get("mode", "Normal")
    active_injections = status.get("active_incidents", 0)

    # Active indicator
    if is_running:
        status_html = '<div style="display:flex; align-items:center; margin-bottom:10px;"><span class="pulse-dot"></span><span style="font-size:0.85rem; font-weight:600; color:#10b981;">TELEMETRY ACTIVE</span></div>'
    else:
        status_html = '<div style="display:flex; align-items:center; margin-bottom:10px;"><span class="pulse-dot pulse-dot-red"></span><span style="font-size:0.85rem; font-weight:600; color:#ef4444;">MONITORING PAUSED</span></div>'

    st.sidebar.markdown(status_html, unsafe_allow_html=True)

    # Monitoring Start/Stop
    col_a, col_b = st.sidebar.columns(2)
    with col_a:
        if st.button("▶ Start", key="sim_start_btn", disabled=is_running, use_container_width=True):
            start_simulation()
            st.rerun()
    with col_b:
        if st.button("⏹ Stop", key="sim_stop_btn", disabled=not is_running, use_container_width=True):
            stop_simulation()
            st.rerun()

    # Simulation Mode
    mode_options = ["Normal", "Warning", "Critical", "Random"]
    mode_index = mode_options.index(current_mode) if current_mode in mode_options else 0
    selected_mode = st.sidebar.selectbox(
        "Simulation Mode",
        mode_options,
        index=mode_index,
        key="sim_mode_select"
    )
    if selected_mode != current_mode:
        set_simulation_mode(selected_mode)
        st.toast(f"Simulation mode set to {selected_mode}", icon="⚡")
        st.rerun()

    # Trigger Incident Section
    st.sidebar.markdown("**Inject Synthetic Fault**")

    # Devices for targeting
    devices = fetch_devices()
    device_choices = ["Auto-assign"] + [f"{d['id']} ({d['hostname']})" for d in devices]
    selected_dev = st.sidebar.selectbox("Target Node", device_choices, index=0, key="sim_target_dev")

    target_device_id = None
    if selected_dev != "Auto-assign":
        target_device_id = selected_dev.split(" ")[0]

    faults = [
        "Server Overload",
        "Network Failure",
        "High Latency",
        "Packet Loss",
        "DNS Failure",
        "Disk Capacity Issue",
        "Memory Exhaustion",
    ]

    selected_fault = st.sidebar.selectbox("Fault Type", faults, key="sim_fault_select")

    if st.sidebar.button("💥 Trigger Incident", key="sim_trigger_btn", use_container_width=True):
        res = trigger_simulation_incident(selected_fault, target_device_id)
        if res:
            st.toast(f"Fault '{selected_fault}' injected into {res.get('device_id')}!", icon="🚨")
            st.rerun()
        else:
            st.error("Failed to inject fault via API.")
