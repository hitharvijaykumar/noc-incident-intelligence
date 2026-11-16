"""
API endpoint integration tests directly testing router functions and data validation.
"""
import pytest
from backend.database import SessionLocal, init_db
from simulator.infrastructure_simulator import simulator_instance

# Import endpoint handlers
from backend.main import health_check
from backend.api.devices import get_devices, get_device, get_device_metrics
from backend.api.monitoring import get_monitoring_summary, get_current_metrics, get_monitoring_history
from backend.api.alerts import get_alerts, acknowledge_alert, resolve_alert
from backend.api.incidents import get_incidents, get_incident, create_incident, update_incident_status, resolve_incident
from backend.api.analytics import get_analytics_summary, get_severity_distribution, get_incident_trends
from backend.api.simulation import get_simulation_status, set_simulation_mode, trigger_incident
from backend.schemas import (
    IncidentCreate, IncidentStatusUpdate, IncidentResolveRequest,
    SimulationModeRequest, TriggerIncidentRequest
)

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    init_db()
    simulator_instance.seed_devices_in_db()

@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_health_endpoint():
    res = health_check()
    assert res["status"] == "HEALTHY"
    assert "app_name" in res

def test_devices_endpoints(db):
    devices = get_devices(db=db)
    assert len(devices) >= 15

    dev_id = devices[0].id
    single_dev = get_device(device_id=dev_id, db=db)
    assert single_dev.id == dev_id

    metrics = get_device_metrics(device_id=dev_id, limit=20, db=db)
    assert isinstance(metrics, list)

def test_monitoring_endpoints(db):
    summary = get_monitoring_summary(db=db)
    assert summary.total_devices >= 15
    assert hasattr(summary, "avg_cpu")

    current = get_current_metrics(db=db)
    assert isinstance(current, list)

    history = get_monitoring_history(limit=50, db=db)
    assert isinstance(history, list)

def test_alerts_endpoints(db):
    alerts = get_alerts(limit=50, db=db)
    assert isinstance(alerts, list)

def test_incident_lifecycle(db):
    # Create incident
    payload = IncidentCreate(
        incident_title="Unit Test Elevated CPU",
        incident_description="Synthetic load testing CPU threshold violation",
        device_id="srv-app-01",
        affected_device="api-gateway-01.noc.corp",
        incident_category="Server Overload",
        severity="HIGH",
        confidence_score=0.95,
        anomaly_score=-0.20,
        cluster_id=1
    )
    inc = create_incident(payload=payload, db=db)
    assert inc.id.startswith("INC-")
    assert inc.status == "NEW"

    # Acknowledge incident
    ack_payload = IncidentStatusUpdate(status="ACKNOWLEDGED", notes="Assigned to engineer")
    ack_inc = update_incident_status(incident_id=inc.id, payload=ack_payload, db=db)
    assert ack_inc.status == "ACKNOWLEDGED"

    # Resolve incident
    resolve_payload = IncidentResolveRequest(resolution_notes="Optimized DB query pool and freed CPU.")
    res_inc = resolve_incident(incident_id=inc.id, payload=resolve_payload, db=db)
    assert res_inc.status == "RESOLVED"
    assert res_inc.resolution_notes == "Optimized DB query pool and freed CPU."

def test_analytics_endpoints(db):
    summary = get_analytics_summary(db=db)
    assert summary.total_incidents >= 1
    assert 0.0 <= summary.resolution_rate <= 100.0

    sev_dist = get_severity_distribution(db=db)
    assert isinstance(sev_dist, dict)

    trends = get_incident_trends(db=db)
    assert isinstance(trends, list)

def test_simulation_endpoints():
    status = get_simulation_status()
    assert hasattr(status, "is_running")
    assert status.total_devices >= 15

    mode_res = set_simulation_mode(SimulationModeRequest(mode="Warning"))
    assert mode_res["mode"] == "Warning"

    # Reset mode to Normal
    set_simulation_mode(SimulationModeRequest(mode="Normal"))
