"""
Operational analytics API endpoints: MTTA, MTTR, distribution and trends.
"""
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from backend.database import get_db
from backend.models import Incident, IncidentHistory, Device
from backend.schemas import AnalyticsSummaryResponse, IncidentTrendItem

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_summary(db: Session = Depends(get_db)):
    """Compute end-to-end incident operational statistics."""
    incidents = db.query(Incident).all()
    total_incidents = len(incidents)
    active_incidents = sum(1 for i in incidents if i.status in ["NEW", "ACKNOWLEDGED", "INVESTIGATING"])
    resolved_incidents = sum(1 for i in incidents if i.status in ["RESOLVED", "CLOSED"])

    # Resolution rate
    resolution_rate = round((resolved_incidents / total_incidents * 100), 1) if total_incidents > 0 else 100.0

    # Severity distribution
    severity_dist: Dict[str, int] = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    # Category distribution
    category_dist: Dict[str, int] = {}

    for inc in incidents:
        severity_dist[inc.severity] = severity_dist.get(inc.severity, 0) + 1
        category_dist[inc.incident_category] = category_dist.get(inc.incident_category, 0) + 1

    # MTTA & MTTR calculations
    ack_durations_minutes = []
    resolve_durations_minutes = []

    for inc in incidents:
        # MTTR: from first_detected_at to resolved_at
        if inc.resolved_at and inc.first_detected_at:
            delta = (inc.resolved_at - inc.first_detected_at).total_seconds() / 60.0
            if delta >= 0:
                resolve_durations_minutes.append(delta)

        # MTTA: from first_detected_at to first ACKNOWLEDGED history entry
        first_ack = (
            db.query(IncidentHistory)
            .filter(IncidentHistory.incident_id == inc.id, IncidentHistory.new_status == "ACKNOWLEDGED")
            .order_by(IncidentHistory.timestamp.asc())
            .first()
        )
        if first_ack and inc.first_detected_at:
            delta = (first_ack.timestamp - inc.first_detected_at).total_seconds() / 60.0
            if delta >= 0:
                ack_durations_minutes.append(delta)

    mtta = round(sum(ack_durations_minutes) / len(ack_durations_minutes), 1) if ack_durations_minutes else 0.0
    mttr = round(sum(resolve_durations_minutes) / len(resolve_durations_minutes), 1) if resolve_durations_minutes else 0.0

    # Top problematic devices
    device_counts = (
        db.query(Incident.device_id, Incident.affected_device, func.count(Incident.id).label("inc_count"))
        .group_by(Incident.device_id, Incident.affected_device)
        .order_by(desc("inc_count"))
        .limit(5)
        .all()
    )
    top_devices = [
        {"device_id": d[0], "hostname": d[1], "incident_count": d[2]}
        for d in device_counts
    ]

    return AnalyticsSummaryResponse(
        total_incidents=total_incidents,
        active_incidents=active_incidents,
        resolved_incidents=resolved_incidents,
        mtta_minutes=mtta,
        mttr_minutes=mttr,
        resolution_rate=resolution_rate,
        severity_distribution=severity_dist,
        category_distribution=category_dist,
        top_problematic_devices=top_devices
    )

@router.get("/severity-distribution")
def get_severity_distribution(db: Session = Depends(get_db)):
    """Counts of incidents grouped by severity level."""
    rows = (
        db.query(Incident.severity, func.count(Incident.id))
        .group_by(Incident.severity)
        .all()
    )
    result = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for sev, count in rows:
        result[sev] = count
    return result

@router.get("/incident-trends")
def get_incident_trends(days: int = 7, db: Session = Depends(get_db)):
    """Chronological volume of incidents."""
    incidents = db.query(Incident).order_by(Incident.first_detected_at.asc()).all()
    trends: Dict[str, Dict[str, int]] = {}

    for inc in incidents:
        day_str = inc.first_detected_at.strftime("%Y-%m-%d") if inc.first_detected_at else "Unknown"
        if day_str not in trends:
            trends[day_str] = {"count": 0, "critical_count": 0}
        trends[day_str]["count"] += 1
        if inc.severity == "CRITICAL":
            trends[day_str]["critical_count"] += 1

    return [
        {"date": date_k, "count": vals["count"], "critical_count": vals["critical_count"]}
        for date_k, vals in trends.items()
    ]

@router.get("/resolution-statistics")
def get_resolution_statistics(db: Session = Depends(get_db)):
    """Key incident response speed metrics."""
    summary = get_analytics_summary(db)
    return {
        "mtta_minutes": summary.mtta_minutes,
        "mttr_minutes": summary.mttr_minutes,
        "resolution_rate": summary.resolution_rate,
        "total_incidents": summary.total_incidents,
        "resolved_incidents": summary.resolved_incidents
    }
