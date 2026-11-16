"""
Alert generation and rule engine with duplicate suppression, grouping, and resolution.
"""
from datetime import datetime, timezone
import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.config import settings
from backend.models import Alert, Device
from backend.utils.logger import logger

class AlertService:
    def __init__(self):
        # In-memory tracking of recent alert timestamps to handle fast suppression
        self.last_alert_time: Dict[str, float] = {}  # key = f"{device_id}_{metric_name}"

    def evaluate_metrics(self, db: Session, metric_dict: Dict[str, Any]) -> List[Alert]:
        """
        Evaluates metrics against configured thresholds and produces or updates alerts.
        Suppresses continuous duplicates for active alerts.
        """
        device_id = metric_dict.get("device_id")
        hostname = metric_dict.get("hostname", device_id)
        alerts_generated = []

        rules = [
            ("cpu_utilization", metric_dict.get("cpu_utilization", 0.0),
             settings.CPU_NORMAL_MAX, settings.CPU_WARNING_MAX, "CPU Utilization High", "%"),
            ("memory_utilization", metric_dict.get("memory_utilization", 0.0),
             settings.MEMORY_NORMAL_MAX, settings.MEMORY_WARNING_MAX, "Memory Utilization High", "%"),
            ("disk_utilization", metric_dict.get("disk_utilization", 0.0),
             settings.DISK_NORMAL_MAX, settings.DISK_WARNING_MAX, "Disk Storage High", "%"),
            ("network_latency", metric_dict.get("network_latency", 0.0),
             settings.LATENCY_NORMAL_MAX, settings.LATENCY_WARNING_MAX, "Network Latency Degraded", "ms"),
            ("packet_loss", metric_dict.get("packet_loss", 0.0),
             settings.PACKET_LOSS_NORMAL_MAX, settings.PACKET_LOSS_WARNING_MAX, "Packet Loss Detected", "%"),
        ]

        now = datetime.now(timezone.utc)

        # Check offline / availability
        avail = metric_dict.get("server_availability", 1.0)
        conn = metric_dict.get("connection_status", 1)
        if avail <= 0.0 or conn == 0:
            existing = db.query(Alert).filter(
                Alert.device_id == device_id,
                Alert.metric_name == "availability",
                Alert.status.in_(["ACTIVE", "ACKNOWLEDGED"])
            ).first()
            if not existing:
                alt = Alert(
                    id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
                    timestamp=now,
                    device_id=device_id,
                    device_hostname=hostname,
                    metric_name="availability",
                    observed_value=0.0,
                    expected_threshold=1.0,
                    alert_description="Device node or interface is OFFLINE / Unreachable",
                    initial_severity="CRITICAL",
                    status="ACTIVE"
                )
                db.add(alt)
                alerts_generated.append(alt)

        # Check DNS status
        dns_status = metric_dict.get("dns_response_status", 1)
        if dns_status == 0:
            existing = db.query(Alert).filter(
                Alert.device_id == device_id,
                Alert.metric_name == "dns_response_status",
                Alert.status.in_(["ACTIVE", "ACKNOWLEDGED"])
            ).first()
            if not existing:
                alt = Alert(
                    id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
                    timestamp=now,
                    device_id=device_id,
                    device_hostname=hostname,
                    metric_name="dns_response_status",
                    observed_value=0.0,
                    expected_threshold=1.0,
                    alert_description="DNS resolution failure on query resolver",
                    initial_severity="HIGH",
                    status="ACTIVE"
                )
                db.add(alt)
                alerts_generated.append(alt)

        # Numerical metric thresholds
        for metric_name, val, warn_thresh, crit_thresh, label, unit in rules:
            if val >= crit_thresh:
                severity = "CRITICAL"
            elif val >= warn_thresh:
                severity = "WARNING"
            else:
                # Value is normal. If there was an active alert, auto-resolve it
                existing_active = db.query(Alert).filter(
                    Alert.device_id == device_id,
                    Alert.metric_name == metric_name,
                    Alert.status.in_(["ACTIVE", "ACKNOWLEDGED"])
                ).first()
                if existing_active:
                    existing_active.status = "RESOLVED"
                    existing_active.resolved_at = now
                continue

            # Check for duplicate active alert suppression
            existing = db.query(Alert).filter(
                Alert.device_id == device_id,
                Alert.metric_name == metric_name,
                Alert.status.in_(["ACTIVE", "ACKNOWLEDGED"])
            ).first()

            if existing:
                # Duplicate suppression: update observed value without creating a duplicate record
                existing.observed_value = val
                if severity == "CRITICAL" and existing.initial_severity == "WARNING":
                    existing.initial_severity = "CRITICAL"  # Escalate
                continue

            # Create new alert
            expected = warn_thresh if severity == "WARNING" else crit_thresh
            alt = Alert(
                id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
                timestamp=now,
                device_id=device_id,
                device_hostname=hostname,
                metric_name=metric_name,
                observed_value=val,
                expected_threshold=expected,
                alert_description=f"{label}: {val}{unit} (Threshold: {expected}{unit})",
                initial_severity=severity,
                status="ACTIVE"
            )
            db.add(alt)
            alerts_generated.append(alt)

        if alerts_generated:
            db.commit()

        return alerts_generated

    def acknowledge_alert(self, db: Session, alert_id: str) -> Optional[Alert]:
        alt = db.query(Alert).filter(Alert.id == alert_id).first()
        if alt:
            alt.status = "ACKNOWLEDGED"
            db.commit()
            db.refresh(alt)
        return alt

    def resolve_alert(self, db: Session, alert_id: str) -> Optional[Alert]:
        alt = db.query(Alert).filter(Alert.id == alert_id).first()
        if alt:
            alt.status = "RESOLVED"
            alt.resolved_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(alt)
        return alt

alert_service = AlertService()
