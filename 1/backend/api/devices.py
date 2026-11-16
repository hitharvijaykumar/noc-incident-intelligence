"""
Device management API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.database import get_db
from backend.models import Device, MetricHistory
from backend.schemas import DeviceResponse, DeviceMetricSummary, MetricResponse

router = APIRouter(prefix="/api/devices", tags=["Devices"])

@router.get("", response_model=List[DeviceMetricSummary])
def get_devices(
    device_type: Optional[str] = None,
    status: Optional[str] = None,
    health_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all registered network and server devices with their latest metric snapshot."""
    query = db.query(Device)
    if device_type:
        query = query.filter(Device.device_type == device_type)
    if status:
        query = query.filter(Device.status == status)
    if health_status:
        query = query.filter(Device.health_status == health_status)

    devices = query.all()
    results = []

    for dev in devices:
        latest = (
            db.query(MetricHistory)
            .filter(MetricHistory.device_id == dev.id)
            .order_by(desc(MetricHistory.timestamp))
            .first()
        )
        summary = DeviceMetricSummary.model_validate(dev)
        if latest:
            summary.latest_cpu = latest.cpu_utilization
            summary.latest_memory = latest.memory_utilization
            summary.latest_disk = latest.disk_utilization
            summary.latest_latency = latest.network_latency
            summary.latest_packet_loss = latest.packet_loss
        results.append(summary)

    return results

@router.get("/{device_id}", response_model=DeviceMetricSummary)
def get_device(device_id: str, db: Session = Depends(get_db)):
    """Retrieve details for a single device."""
    dev = db.query(Device).filter(Device.id == device_id).first()
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")

    latest = (
        db.query(MetricHistory)
        .filter(MetricHistory.device_id == dev.id)
        .order_by(desc(MetricHistory.timestamp))
        .first()
    )
    summary = DeviceMetricSummary.model_validate(dev)
    if latest:
        summary.latest_cpu = latest.cpu_utilization
        summary.latest_memory = latest.memory_utilization
        summary.latest_disk = latest.disk_utilization
        summary.latest_latency = latest.network_latency
        summary.latest_packet_loss = latest.packet_loss
    return summary

@router.get("/{device_id}/metrics", response_model=List[MetricResponse])
def get_device_metrics(
    device_id: str,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Retrieve time-series metric history for a specific device."""
    dev = db.query(Device).filter(Device.id == device_id).first()
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")

    metrics = (
        db.query(MetricHistory)
        .filter(MetricHistory.device_id == device_id)
        .order_by(desc(MetricHistory.timestamp))
        .limit(limit)
        .all()
    )
    return list(reversed(metrics))
