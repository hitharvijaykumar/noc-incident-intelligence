"""
Page 3: Incident Management and Intelligent Troubleshooting Workflows.
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Any

from frontend.components.styling import apply_noc_theme, get_severity_badge, get_status_badge, render_kpi_card
from frontend.components.tables import format_incident_table_data
from frontend.components.simulation_controls import render_simulation_controls
from frontend.api_client import (
    fetch_incidents, fetch_incident, update_incident_status,
    resolve_incident, fetch_device_metrics
)

apply_noc_theme()
render_simulation_controls()

st.markdown("## 🚨 Incident Management & Remediation")
st.markdown('<div style="color:#94a3b8; font-size:0.9rem; margin-top:-10px;">Automated Alert Correlation, ML Root Cause Intelligence & Interactive Triage</div>', unsafe_allow_html=True)

# 1. Filters Bar
col_f1, col_f2, col_f3, col_f4 = st.columns([2, 1, 1, 1])

with col_f1:
    search_query = st.text_input("🔍 Search Incidents", placeholder="Search by title, device or category...", key="inc_search")

with col_f2:
    status_filter = st.selectbox("Status", ["All", "NEW", "ACKNOWLEDGED", "INVESTIGATING", "RESOLVED", "CLOSED"], index=0, key="inc_status_filter")

with col_f3:
    severity_filter = st.selectbox("Severity", ["All", "CRITICAL", "HIGH", "MEDIUM", "LOW"], index=0, key="inc_sev_filter")

with col_f4:
    category_filter = st.selectbox("Category", [
        "All", "Server Overload", "Network Failure", "High Latency", "Packet Loss",
        "DNS Failure", "Disk Capacity Issue", "Memory Exhaustion"
    ], index=0, key="inc_cat_filter")

# Fetch Incidents
incidents = fetch_incidents(
    status=None if status_filter == "All" else status_filter,
    severity=None if severity_filter == "All" else severity_filter,
    limit=200
)

# Apply category & search client-side filtering
if category_filter != "All":
    incidents = [i for i in incidents if i.get("incident_category") == category_filter]

if search_query:
    q = search_query.lower()
    incidents = [
        i for i in incidents
        if q in i.get("id", "").lower()
        or q in i.get("incident_title", "").lower()
        or q in i.get("affected_device", "").lower()
        or q in i.get("incident_category", "").lower()
    ]

# Incident Summary Cards
crit_count = sum(1 for i in incidents if i.get("severity") == "CRITICAL")
active_count = sum(1 for i in incidents if i.get("status") in ["NEW", "ACKNOWLEDGED", "INVESTIGATING"])
resolved_count = sum(1 for i in incidents if i.get("status") in ["RESOLVED", "CLOSED"])

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(render_kpi_card("Filtered Incidents", str(len(incidents)), "Matching current criteria", "#38bdf8"), unsafe_allow_html=True)
with c2:
    st.markdown(render_kpi_card("Active Unresolved", str(active_count), "Requires NOC triage", "#ef4444" if active_count > 0 else "#10b981"), unsafe_allow_html=True)
with c3:
    st.markdown(render_kpi_card("Critical Severity", str(crit_count), "Urgent SLA impact", "#ef4444" if crit_count > 0 else "#64748b"), unsafe_allow_html=True)
with c4:
    st.markdown(render_kpi_card("Resolved / Closed", str(resolved_count), "Remediation verified", "#10b981"), unsafe_allow_html=True)

st.markdown("---")

if not incidents:
    st.info("No incidents found matching the specified filters.")
    st.stop()

# 2. Main Incidents Table
df_inc = format_incident_table_data(incidents)
st.dataframe(df_inc, use_container_width=True, hide_index=True)

# 3. Incident Selection for Detailed Inspection
incident_choices = [f"{i['id']} — [{i['severity']}] {i['incident_title']}" for i in incidents]
selected_choice = st.selectbox("👉 Select Incident to Inspect & Triage", incident_choices, key="inc_inspect_select")
selected_id = selected_choice.split(" ")[0]

selected_incident = fetch_incident(selected_id)
if not selected_incident:
    st.error("Failed to load details for selected incident.")
    st.stop()

st.markdown("---")
st.subheader(f"🛠️ Incident Dossier: {selected_incident.get('id')}")

# Incident Metadata Grid
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"**Target Node:** `{selected_incident.get('affected_device')}` (`{selected_incident.get('device_id')}`)")
    st.markdown(f"**Severity:** {get_severity_badge(selected_incident.get('severity', 'LOW'))}", unsafe_allow_html=True)
with m2:
    st.markdown(f"**Category:** `{selected_incident.get('incident_category')}`")
    st.markdown(f"**Status:** {get_status_badge(selected_incident.get('status', 'NEW'))}", unsafe_allow_html=True)
with m3:
    conf = f"{selected_incident.get('confidence_score', 0)*100:.1f}%"
    st.markdown(f"**ML Classifier Confidence:** `{conf}`")
    st.markdown(f"**Anomaly Score:** `{selected_incident.get('anomaly_score', 0):.2f}`")
with m4:
    det_time = selected_incident.get('first_detected_at', '')[:19].replace('T', ' ')
    st.markdown(f"**First Detected:** `{det_time} UTC`")
    res_time = selected_incident.get('resolved_at')
    st.markdown(f"**Resolved At:** `{res_time[:19].replace('T', ' ') if res_time else 'Active'}`")

# Root Cause Analysis Box
st.markdown("#### 🔬 AI Root-Cause Hypothesis")
st.info(f"**Hypothesis:** {selected_incident.get('root_cause_hypothesis', 'Baseline telemetry deviation')}")

# Two Tabs: Troubleshooting Recommendations & Incident Timeline
tab_recs, tab_timeline, tab_actions = st.tabs([
    "💡 AI Troubleshooting Playbook",
    "📜 Incident Timeline & Audit Trail",
    "⚡ NOC Operator Actions"
])

with tab_recs:
    recs = selected_incident.get("parsed_recommendations") or []
    if recs:
        for idx, rec in enumerate(recs, start=1):
            prio = rec.get("priority", "MEDIUM")
            prio_color = "#ef4444" if prio == "HIGH" else ("#f59e0b" if prio == "MEDIUM" else "#3b82f6")
            manual = "⚠️ Manual Verification Required" if rec.get("manual_verification_required", True) else "⚙️ Automated Safe Check"

            st.markdown(
                f"""
                <div style="background-color:#111827; border:1px solid #1f2937; border-left:4px solid {prio_color}; border-radius:6px; padding:12px 16px; margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between;">
                        <span style="font-weight:600; color:#f8fafc;">Step {idx}: {rec.get('action')}</span>
                        <span style="font-size:0.75rem; font-weight:700; color:{prio_color};">PRIORITY: {prio}</span>
                    </div>
                    <div style="font-size:0.85rem; color:#94a3b8; margin-top:6px;">
                        <b>Diagnostic Context:</b> {rec.get('reason')}
                    </div>
                    <div style="font-size:0.85rem; color:#10b981; margin-top:4px;">
                        <b>Expected Outcome:</b> {rec.get('expected_outcome')}
                    </div>
                    <div style="font-size:0.75rem; color:#64748b; margin-top:6px;">
                        {manual}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.markdown("_No specific recommendations recorded for this incident type._")

with tab_timeline:
    history = selected_incident.get("history") or []
    if history:
        for h in history:
            h_time = h.get("timestamp", "")[:19].replace("T", " ")
            st.markdown(
                f"""
                <div style="border-left: 2px solid #38bdf8; padding-left: 14px; margin-bottom: 12px;">
                    <div style="font-size: 0.8rem; color: #64748b;">{h_time} UTC — by <b>{h.get('updated_by')}</b></div>
                    <div style="font-size: 0.9rem; color: #f8fafc; font-weight: 500;">
                        Status Transition: <span style="color:#ef4444;">{h.get('old_status')}</span> ➔ <span style="color:#10b981;">{h.get('new_status')}</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 2px;">{h.get('notes', '')}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("No audit entries recorded.")

with tab_actions:
    st.markdown("#### Operational Status Update")
    act_col1, act_col2 = st.columns(2)

    with act_col1:
        st.markdown("**Transition Lifecycle Status**")
        curr_status = selected_incident.get("status", "NEW")
        target_status = st.selectbox("New Lifecycle State", ["ACKNOWLEDGED", "INVESTIGATING", "CLOSED"], key="triage_status_select")
        status_notes = st.text_input("Triage Log / Notes", placeholder="e.g. Assigned to on-call engineer; inspecting logs.", key="triage_notes_input")

        if st.button("Apply Status Change", key="apply_status_btn"):
            res = update_incident_status(selected_id, target_status, status_notes)
            if res:
                st.toast(f"Incident {selected_id} updated to {target_status}!", icon="✅")
                st.rerun()
            else:
                st.error("Failed to update incident status.")

    with act_col2:
        st.markdown("**Resolve Incident & Document Fix**")
        res_notes = st.text_area("Root Cause Resolution Notes", placeholder="e.g. Cleared stuck worker thread / restarted daemon / link recovered.", key="res_notes_input")

        if st.button("Resolve Incident (Close)", key="resolve_inc_btn"):
            if not res_notes.strip():
                st.warning("Please provide resolution notes before resolving the incident.")
            else:
                res = resolve_incident(selected_id, res_notes)
                if res:
                    st.toast(f"Incident {selected_id} successfully marked as RESOLVED!", icon="🎉")
                    st.rerun()
                else:
                    st.error("Failed to resolve incident.")
