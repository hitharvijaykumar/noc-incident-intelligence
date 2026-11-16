"""
End-to-End incident lifecycle and simulation integration tests.
"""
import pytest
from backend.database import SessionLocal, init_db
from backend.models import Incident, Alert, Device, MetricHistory
from backend.services.monitoring_service import monitoring_service
from backend.services.incident_service import incident_service
from backend.services.alert_service import alert_service
from simulator.infrastructure_simulator import simulator_instance
from ml.prediction import prediction_service

@pytest.fixture(scope="session", autouse=True)
def setup_integration():
    init_db()
    simulator_instance.seed_devices_in_db()
    # Ensure models are loaded or trained
    if not prediction_service.is_loaded:
        from ml.train_all import train_all_models
        train_all_models()
        prediction_service.load_models()

def test_e2e_server_overload_incident_flow():
    db = SessionLocal()
    target_dev = "srv-app-01"

    # 1. Trigger simulated Server Overload
    simulator_instance.trigger_incident("Server Overload", target_dev)

    # 2. Step monitoring engine to process telemetry, rules, ML and incident creation
    processed_count = monitoring_service.step_once()
    assert processed_count >= 15

    # 3. Confirm CPU increased above threshold
    latest_metric = (
        db.query(MetricHistory)
        .filter(MetricHistory.device_id == target_dev)
        .order_by(MetricHistory.timestamp.desc())
        .first()
    )
    assert latest_metric is not None
    assert latest_metric.cpu_utilization >= 85.0

    # 4. Confirm alert generation
    alert = (
        db.query(Alert)
        .filter(Alert.device_id == target_dev, Alert.metric_name == "cpu_utilization")
        .order_by(Alert.timestamp.desc())
        .first()
    )
    assert alert is not None
    assert alert.status in ["ACTIVE", "ACKNOWLEDGED"]
    assert alert.initial_severity in ["WARNING", "CRITICAL"]

    # 5. Confirm Incident opened with ML classification
    incident = (
        db.query(Incident)
        .filter(Incident.device_id == target_dev, Incident.incident_category == "Server Overload")
        .order_by(Incident.first_detected_at.desc())
        .first()
    )
    assert incident is not None
    assert incident.status in ["NEW", "ACKNOWLEDGED", "INVESTIGATING"]
    assert incident.confidence_score > 0.5
    assert incident.severity in ["HIGH", "CRITICAL"]
    assert "CPU" in incident.root_cause_hypothesis or "demand" in incident.root_cause_hypothesis

    # 6. Confirm recommendations generated
    assert incident.recommendations is not None
    assert "CPU-intensive processes" in incident.recommendations

    # 7. Resolve the incident
    resolved_inc = incident_service.resolve_incident(
        db=db,
        incident_id=incident.id,
        resolution_notes="Scaled cluster replica and terminated high-load thread.",
        updated_by="NOC_QA_TESTER"
    )
    assert resolved_inc.status == "RESOLVED"
    assert resolved_inc.resolved_at is not None

    # Clear simulator fault
    simulator_instance.clear_incident(target_dev)
    db.close()

def test_duplicate_alert_and_incident_suppression():
    db = SessionLocal()
    target_dev = "srv-web-01"

    # Trigger Disk Capacity fault
    simulator_instance.trigger_incident("Disk Capacity Issue", target_dev)

    # Step twice
    monitoring_service.step_once()
    monitoring_service.step_once()

    # Verify only ONE active incident exists for this device & category
    active_incidents = (
        db.query(Incident)
        .filter(
            Incident.device_id == target_dev,
            Incident.incident_category == "Disk Capacity Issue",
            Incident.status.in_([ "NEW", "ACKNOWLEDGED", "INVESTIGATING" ])
        )
        .all()
    )
    assert len(active_incidents) == 1

    # Cleanup
    simulator_instance.clear_incident(target_dev)
    db.close()
