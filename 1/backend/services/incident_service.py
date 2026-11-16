"""
Incident lifecycle management, correlation, root-cause hypothesis generation, and deduplication.
"""
from datetime import datetime, timezone
import json
import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.models import Incident, IncidentHistory, Device, Alert
from backend.services.recommendation_service import generate_recommendations_json
from backend.utils.logger import logger

VALID_STATUSES = ["NEW", "ACKNOWLEDGED", "INVESTIGATING", "RESOLVED", "CLOSED"]

class IncidentService:
    def __init__(self):
        pass

    def synthesize_root_cause(
        self,
        category: str,
        device_id: str,
        metrics: Dict[str, Any],
        correlated_devices: List[str] = None
    ) -> str:
        """
        Synthesizes a realistic root-cause hypothesis based on telemetry signatures and blast radius.
        """
        if correlated_devices and len(correlated_devices) > 1:
            return (
                f"Correlated Multi-Device Degradation: {len(correlated_devices)} devices "
                f"({', '.join(correlated_devices[:3])}) exhibiting concurrent latency/loss. "
                f"Indicates upstream network backbone or spine switch failure in datacenter."
            )

        if category == "Server Overload":
            return (
                f"High computational demand: Process count ({metrics.get('process_count', 0)}) "
                f"and CPU ({metrics.get('cpu_utilization', 0)}%) indicate thread runaway or CPU saturation."
            )
        elif category == "Memory Exhaustion":
            return (
                f"Memory leak / unbounded buffer allocation: RAM usage at {metrics.get('memory_utilization', 0)}%, "
                f"threatening kernel OOM Killer termination."
            )
        elif category == "Disk Capacity Issue":
            return (
                f"Filesystem block saturation: Storage at {metrics.get('disk_utilization', 0)}% "
                f"likely driven by unrotated application logs or temporary files."
            )
        elif category == "Network Failure":
            return (
                f"Interface blackout / link loss: Availability dropped to 0%, "
                f"indicating broken transceiver or routing table link failure."
            )
        elif category == "High Latency":
            return (
                f"Network path congestion / bufferbloat: Latency spiked to {metrics.get('network_latency', 0)}ms "
                f"with bandwidth at {metrics.get('bandwidth_utilization', 0)}%."
            )
        elif category == "Packet Loss":
            return (
                f"Transmission degradation: {metrics.get('packet_loss', 0)}% packet loss detected, "
                f"suggesting CRC framing errors or interface queue drops."
            )
        elif category == "DNS Failure":
            return (
                f"Recursive resolver unreachable / timeout: DNS response failed (status 0), "
                f"preventing hostname resolution."
            )
        return "Anomalous telemetry deviation from baseline profile."

    def process_telemetry_incident(
        self,
        db: Session,
        device_id: str,
        hostname: str,
        metrics: Dict[str, Any],
        ml_prediction: Dict[str, Any],
        active_alerts: List[Alert]
    ) -> Optional[Incident]:
        """
        Evaluates whether an active incident should be opened, updated, or correlated.
        Prevents duplicate active incidents for the same device and recurring condition.
        """
        category = ml_prediction["predicted_incident_type"]
        severity = ml_prediction["recommended_severity"]
        is_anomaly = ml_prediction["is_anomaly"]

        # Only trigger an incident if it's an abnormal category, or high severity, or high anomaly
        if category == "Normal" and severity == "LOW" and not is_anomaly:
            return None

        now = datetime.now(timezone.utc)

        # 1. Deduplication: Check if there's an existing open incident for this device and category
        existing_incident = db.query(Incident).filter(
            Incident.device_id == device_id,
            Incident.incident_category == category,
            Incident.status.in_(["NEW", "ACKNOWLEDGED", "INVESTIGATING"])
        ).first()

        if existing_incident:
            # Update existing incident telemetry rather than duplicating
            existing_incident.last_updated_at = now
            existing_incident.confidence_score = ml_prediction["classification_confidence"]
            existing_incident.anomaly_score = ml_prediction["anomaly_score"]
            # Escalate severity if incoming severity is higher
            severity_order = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
            if severity_order.get(severity, 1) > severity_order.get(existing_incident.severity, 1):
                existing_incident.severity = severity
            db.commit()
            return existing_incident

        # 2. Multi-device correlation check: Check if other devices have same category recently
        correlated = db.query(Incident).filter(
            Incident.incident_category == category,
            Incident.status.in_(["NEW", "ACKNOWLEDGED", "INVESTIGATING"]),
            Incident.device_id != device_id
        ).all()
        correlated_device_ids = [inc.device_id for inc in correlated]
        if correlated_device_ids:
            correlated_device_ids.append(device_id)

        # 3. Create New Incident
        inc_id = f"INC-{now.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        title = f"{severity} - {category} on {hostname}"
        description = (
            f"Detected {category} condition on {hostname} ({device_id}). "
            f"ML confidence: {ml_prediction['classification_confidence']*100:.1f}%. "
            f"Anomaly score: {ml_prediction['anomaly_score']:.2f}. "
            f"Observed metrics: CPU {metrics.get('cpu_utilization', 0)}%, "
            f"Mem {metrics.get('memory_utilization', 0)}%, Latency {metrics.get('network_latency', 0)}ms."
        )

        root_cause = self.synthesize_root_cause(
            category=category,
            device_id=device_id,
            metrics=metrics,
            correlated_devices=correlated_device_ids
        )

        recs_json = generate_recommendations_json(category, metrics)

        new_incident = Incident(
            id=inc_id,
            incident_title=title,
            incident_description=description,
            device_id=device_id,
            affected_device=hostname,
            incident_category=category,
            severity=severity,
            confidence_score=ml_prediction["classification_confidence"],
            anomaly_score=ml_prediction["anomaly_score"],
            cluster_id=ml_prediction["cluster_id"],
            first_detected_at=now,
            last_updated_at=now,
            status="NEW",
            root_cause_hypothesis=root_cause,
            recommendations=recs_json
        )
        db.add(new_incident)

        # Initial history record
        history = IncidentHistory(
            incident_id=inc_id,
            timestamp=now,
            old_status="NONE",
            new_status="NEW",
            notes="Incident automatically opened by NOC Intelligence Engine.",
            updated_by="SYSTEM"
        )
        db.add(history)

        # Link active alerts to this incident
        for alt in active_alerts:
            if alt.device_id == device_id and not alt.incident_id:
                alt.incident_id = inc_id

        # Update device health status
        device = db.query(Device).filter(Device.id == device_id).first()
        if device:
            if severity == "CRITICAL":
                device.health_status = "CRITICAL"
                if category == "Network Failure" or metrics.get("server_availability", 1.0) == 0:
                    device.status = "OFFLINE"
            elif severity == "HIGH":
                device.health_status = "WARNING"
                device.status = "DEGRADED"

        db.commit()
        logger.info("Created Incident %s [%s] on %s", inc_id, severity, hostname)
        return new_incident

    def update_status(
        self,
        db: Session,
        incident_id: str,
        new_status: str,
        notes: Optional[str] = None,
        updated_by: str = "NOC_ENGINEER"
    ) -> Optional[Incident]:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident or new_status not in VALID_STATUSES:
            return None

        old_status = incident.status
        if old_status == new_status:
            return incident

        now = datetime.now(timezone.utc)
        incident.status = new_status
        incident.last_updated_at = now

        if new_status in ["RESOLVED", "CLOSED"]:
            incident.resolved_at = now
            if notes and not incident.resolution_notes:
                incident.resolution_notes = notes

            # Also resolve linked alerts
            alerts = db.query(Alert).filter(Alert.incident_id == incident_id).all()
            for alt in alerts:
                alt.status = "RESOLVED"
                alt.resolved_at = now

            # Restore device health
            device = db.query(Device).filter(Device.id == incident.device_id).first()
            if device:
                # Check if device has any other active incidents
                other_incidents = db.query(Incident).filter(
                    Incident.device_id == device.id,
                    Incident.id != incident_id,
                    Incident.status.in_(["NEW", "ACKNOWLEDGED", "INVESTIGATING"])
                ).first()
                if not other_incidents:
                    device.health_status = "HEALTHY"
                    device.status = "ONLINE"

        history = IncidentHistory(
            incident_id=incident_id,
            timestamp=now,
            old_status=old_status,
            new_status=new_status,
            notes=notes or f"Status transitioned from {old_status} to {new_status}",
            updated_by=updated_by
        )
        db.add(history)
        db.commit()
        db.refresh(incident)
        return incident

    def resolve_incident(
        self,
        db: Session,
        incident_id: str,
        resolution_notes: str,
        updated_by: str = "NOC_ENGINEER"
    ) -> Optional[Incident]:
        incident = self.update_status(
            db, incident_id, "RESOLVED", notes=resolution_notes, updated_by=updated_by
        )
        if incident:
            incident.resolution_notes = resolution_notes
            db.commit()
            db.refresh(incident)
        return incident

incident_service = IncidentService()
