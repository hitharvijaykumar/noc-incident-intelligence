"""
Real-time monitoring telemetry API endpoints.
"""
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from backend.database import get_db
from backend.models import MetricHistory, Device, Alert
from backend.schemas import MetricResponse, CurrentMetricsSummary

router = APIRouter(prefix="/api/monitoring", tags=["Monitoring"])

@router.get("/current", response_model=List[MetricResponse])
def get_current_metrics(db: Session = Depends(get_db)):
    """Retrieve the latest telemetry reading for each monitored device."""
    devices = db.query(Device).all()
    results = []
    for dev in devices:
        latest = (
            db.query(MetricHistory)
            .filter(MetricHistory.device_id == dev.id)
            .order_by(desc(MetricHistory.timestamp))
            .first()
        )
        if latest:
            results.append(latest)
    return results

@router.get("/history", response_model=List[MetricResponse])
def get_monitoring_history(
    device_id: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Retrieve historical telemetry entries."""
    query = db.query(MetricHistory)
    if device_id:
        query = query.filter(MetricHistory.device_id == device_id)
    records = query.order_by(desc(MetricHistory.timestamp)).limit(limit).all()
    return list(reversed(records))

@router.get("/summary", response_model=CurrentMetricsSummary)
def get_monitoring_summary(db: Session = Depends(get_db)):
    """Retrieve top-level cluster telemetry KPIs."""
    now = datetime.now(timezone.utc)
    devices = db.query(Device).all()
    total_devices = len(devices)
    online_devices = sum(1 for d in devices if d.status == "ONLINE")

    latest_metrics = []
    for dev in devices:
        latest = (
            db.query(MetricHistory)
            .filter(MetricHistory.device_id == dev.id)
            .order_by(desc(MetricHistory.timestamp))
            .first()
        )
        if latest:
            latest_metrics.append(latest)

    if latest_metrics:
        avg_cpu = round(sum(m.cpu_utilization for m in latest_metrics) / len(latest_metrics), 1)
        avg_mem = round(sum(m.memory_utilization for m in latest_metrics) / len(latest_metrics), 1)
        avg_lat = round(sum(m.network_latency for m in latest_metrics) / len(latest_metrics), 1)
        avg_loss = round(sum(m.packet_loss for m in latest_metrics) / len(latest_metrics), 2)
    else:
        avg_cpu = 0.0
        avg_mem = 0.0
        avg_lat = 0.0
        avg_loss = 0.0

    critical_alerts = (
        db.query(Alert)
        .filter(Alert.status == "ACTIVE", Alert.initial_severity == "CRITICAL")
        .count()
    )

    return CurrentMetricsSummary(
        timestamp=now,
        total_devices=total_devices,
        online_devices=online_devices,
        avg_cpu=avg_cpu,
        avg_memory=avg_mem,
        avg_latency=avg_lat,
        avg_packet_loss=avg_loss,
        active_critical_alerts=critical_alerts
    )
