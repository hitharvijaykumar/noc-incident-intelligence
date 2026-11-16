"""
Centralized API Client for Streamlit to communicate with FastAPI backend.
"""
import requests
from typing import Dict, List, Any, Optional

API_BASE_URL = "http://127.0.0.1:8000/api"
TIMEOUT = 4.0

def _get(endpoint: str, params: Optional[dict] = None) -> Any:
    try:
        resp = requests.get(f"{API_BASE_URL}{endpoint}", params=params, timeout=TIMEOUT)
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception:
        return None

def _post(endpoint: str, json_data: Optional[dict] = None) -> Any:
    try:
        resp = requests.post(f"{API_BASE_URL}{endpoint}", json=json_data, timeout=TIMEOUT)
        if resp.status_code in [200, 201]:
            return resp.json()
        return None
    except Exception:
        return None

def _patch(endpoint: str, json_data: Optional[dict] = None) -> Any:
    try:
        resp = requests.patch(f"{API_BASE_URL}{endpoint}", json=json_data, timeout=TIMEOUT)
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception:
        return None

# Health
def check_backend_health() -> Optional[dict]:
    return _get("/health")

# Devices
def fetch_devices(status: Optional[str] = None) -> List[dict]:
    res = _get("/devices", {"status": status} if status else None)
    return res or []

def fetch_device(device_id: str) -> Optional[dict]:
    return _get(f"/devices/{device_id}")

def fetch_device_metrics(device_id: str, limit: int = 50) -> List[dict]:
    res = _get(f"/devices/{device_id}/metrics", {"limit": limit})
    return res or []

# Monitoring
def fetch_monitoring_summary() -> dict:
    return _get("/monitoring/summary") or {}

def fetch_current_metrics() -> List[dict]:
    return _get("/monitoring/current") or []

def fetch_monitoring_history(device_id: Optional[str] = None, limit: int = 100) -> List[dict]:
    params = {"limit": limit}
    if device_id:
        params["device_id"] = device_id
    return _get("/monitoring/history", params) or []

# Alerts
def fetch_alerts(status: Optional[str] = None, limit: int = 100) -> List[dict]:
    params = {"limit": limit}
    if status:
        params["status"] = status
    return _get("/alerts", params) or []

def acknowledge_alert(alert_id: str) -> Optional[dict]:
    return _post(f"/alerts/{alert_id}/acknowledge")

def resolve_alert(alert_id: str) -> Optional[dict]:
    return _post(f"/alerts/{alert_id}/resolve")

# Incidents
def fetch_incidents(status: Optional[str] = None, severity: Optional[str] = None, limit: int = 100) -> List[dict]:
    params = {"limit": limit}
    if status:
        params["status"] = status
    if severity:
        params["severity"] = severity
    return _get("/incidents", params) or []

def fetch_incident(incident_id: str) -> Optional[dict]:
    return _get(f"/incidents/{incident_id}")

def update_incident_status(incident_id: str, new_status: str, notes: Optional[str] = None) -> Optional[dict]:
    return _patch(f"/incidents/{incident_id}/status", {"status": new_status, "notes": notes})

def resolve_incident(incident_id: str, notes: str) -> Optional[dict]:
    return _post(f"/incidents/{incident_id}/resolve", {"resolution_notes": notes})

def fetch_incident_recommendations(incident_id: str) -> List[dict]:
    return _get(f"/incidents/{incident_id}/recommendations") or []

# ML
def fetch_ml_performance() -> dict:
    return _get("/ml/performance") or {}

def fetch_ml_predictions(limit: int = 50) -> List[dict]:
    return _get("/ml/predictions", {"limit": limit}) or []

def fetch_ml_anomalies(limit: int = 50) -> List[dict]:
    return _get("/ml/anomalies", {"limit": limit}) or []

def fetch_ml_clusters() -> dict:
    return _get("/ml/clusters") or {}

def trigger_ml_train() -> Optional[dict]:
    return _post("/ml/train")

# Analytics
def fetch_analytics_summary() -> dict:
    return _get("/analytics/summary") or {}

def fetch_incident_trends() -> List[dict]:
    return _get("/analytics/incident-trends") or []

# Simulation
def fetch_simulation_status() -> dict:
    return _get("/simulation/status") or {}

def start_simulation() -> Optional[dict]:
    return _post("/simulation/start")

def stop_simulation() -> Optional[dict]:
    return _post("/simulation/stop")

def set_simulation_mode(mode: str) -> Optional[dict]:
    return _post("/simulation/mode", {"mode": mode})

def trigger_simulation_incident(incident_type: str, device_id: Optional[str] = None) -> Optional[dict]:
    payload = {"incident_type": incident_type}
    if device_id:
        payload["device_id"] = device_id
    return _post("/simulation/trigger-incident", payload)
