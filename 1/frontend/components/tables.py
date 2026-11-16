"""
Table formatting helpers for incidents, alerts, and devices.
"""
import pandas as pd
import streamlit as st
from typing import List, Dict, Any
from frontend.components.styling import get_severity_badge, get_status_badge

def format_incident_table_data(incidents: List[Dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for inc in incidents:
        first_det = inc.get("first_detected_at", "")
        if first_det and len(first_det) >= 19:
            first_det = first_det[:19].replace("T", " ")
        rows.append({
            "Incident ID": inc.get("id"),
            "Detected (UTC)": first_det,
            "Device": inc.get("affected_device") or inc.get("device_id"),
            "Category": inc.get("incident_category"),
            "Severity": inc.get("severity"),
            "Confidence": f"{inc.get('confidence_score', 0)*100:.1f}%",
            "Anomaly Score": f"{inc.get('anomaly_score', 0):.2f}",
            "Status": inc.get("status")
        })
    return pd.DataFrame(rows)

def format_device_table_data(devices: List[Dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for dev in devices:
        rows.append({
            "Device ID": dev.get("id"),
            "Hostname": dev.get("hostname"),
            "Type": dev.get("device_type", "").upper(),
            "IP Address": dev.get("ip_address"),
            "Location": dev.get("location"),
            "Status": dev.get("status"),
            "Health": dev.get("health_status"),
            "CPU (%)": dev.get("latest_cpu", 0.0),
            "Memory (%)": dev.get("latest_memory", 0.0),
            "Latency (ms)": dev.get("latest_latency", 0.0),
            "Packet Loss (%)": dev.get("latest_packet_loss", 0.0)
        })
    return pd.DataFrame(rows)
