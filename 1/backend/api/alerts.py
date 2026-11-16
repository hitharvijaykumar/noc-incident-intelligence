"""
Alerts API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.database import get_db
from backend.models import Alert
from backend.schemas import AlertResponse, AlertResolve
from backend.services.alert_service import alert_service

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

@router.get("", response_model=List[AlertResponse])
def get_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    device_id: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List alerts with optional filtering."""
    query = db.query(Alert)
    if status:
        query = query.filter(Alert.status == status)
    if severity:
        query = query.filter(Alert.initial_severity == severity)
    if device_id:
        query = query.filter(Alert.device_id == device_id)

    return query.order_by(desc(Alert.timestamp)).limit(limit).all()

@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: str, db: Session = Depends(get_db)):
    """Retrieve single alert by ID."""
    alt = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alt:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alt

@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(alert_id: str, db: Session = Depends(get_db)):
    """Mark an active alert as acknowledged."""
    alt = alert_service.acknowledge_alert(db, alert_id)
    if not alt:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alt

@router.post("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(alert_id: str, payload: Optional[AlertResolve] = None, db: Session = Depends(get_db)):
    """Manually resolve an active alert."""
    alt = alert_service.resolve_alert(db, alert_id)
    if not alt:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alt
