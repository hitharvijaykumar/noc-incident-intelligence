"""
Incident management API endpoints.
"""
from typing import List, Optional
import json
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.database import get_db
from backend.models import Incident, IncidentHistory
from backend.schemas import (
    IncidentResponse, IncidentCreate, IncidentStatusUpdate,
    IncidentResolveRequest, RecommendationAction
)
from backend.services.incident_service import incident_service
from backend.services.recommendation_service import generate_recommendations

router = APIRouter(prefix="/api/incidents", tags=["Incidents"])

def format_incident_response(inc: Incident) -> IncidentResponse:
    resp = IncidentResponse.model_validate(inc)
    if inc.recommendations:
        try:
            raw_recs = json.loads(inc.recommendations)
            resp.parsed_recommendations = [RecommendationAction(**r) for r in raw_recs]
        except Exception:
            resp.parsed_recommendations = []
    else:
        resp.parsed_recommendations = []
    return resp

@router.get("", response_model=List[IncidentResponse])
def get_incidents(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    category: Optional[str] = None,
    device_id: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Retrieve list of incidents with optional filtering."""
    query = db.query(Incident)
    if status:
        query = query.filter(Incident.status == status)
    if severity:
        query = query.filter(Incident.severity == severity)
    if category:
        query = query.filter(Incident.incident_category == category)
    if device_id:
        query = query.filter(Incident.device_id == device_id)

    incidents = query.order_by(desc(Incident.first_detected_at)).limit(limit).all()
    return [format_incident_response(inc) for inc in incidents]

@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    """Retrieve complete incident details and timeline."""
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return format_incident_response(inc)

@router.post("", response_model=IncidentResponse)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    """Manually register an incident."""
    now = datetime.now(timezone.utc)
    inc_id = f"INC-{now.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    recs_json = payload.recommendations or json.dumps(generate_recommendations(payload.incident_category))

    inc = Incident(
        id=inc_id,
        incident_title=payload.incident_title,
        incident_description=payload.incident_description,
        device_id=payload.device_id,
        affected_device=payload.affected_device,
        incident_category=payload.incident_category,
        severity=payload.severity,
        confidence_score=payload.confidence_score,
        anomaly_score=payload.anomaly_score,
        cluster_id=payload.cluster_id,
        first_detected_at=now,
        last_updated_at=now,
        status="NEW",
        root_cause_hypothesis=payload.root_cause_hypothesis or "Manually reported operational incident.",
        recommendations=recs_json
    )
    db.add(inc)

    history = IncidentHistory(
        incident_id=inc_id,
        timestamp=now,
        old_status="NONE",
        new_status="NEW",
        notes="Incident created via API.",
        updated_by="API_USER"
    )
    db.add(history)
    db.commit()
    db.refresh(inc)
    return format_incident_response(inc)

@router.patch("/{incident_id}/status", response_model=IncidentResponse)
def update_incident_status(incident_id: str, payload: IncidentStatusUpdate, db: Session = Depends(get_db)):
    """Transition an incident lifecycle status (e.g. ACKNOWLEDGED, INVESTIGATING, CLOSED)."""
    inc = incident_service.update_status(
        db=db,
        incident_id=incident_id,
        new_status=payload.status,
        notes=payload.notes,
        updated_by=payload.updated_by or "NOC_ENGINEER"
    )
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found or invalid status transition")
    return format_incident_response(inc)

@router.post("/{incident_id}/resolve", response_model=IncidentResponse)
def resolve_incident(incident_id: str, payload: IncidentResolveRequest, db: Session = Depends(get_db)):
    """Resolve an incident and record root cause resolution notes."""
    inc = incident_service.resolve_incident(
        db=db,
        incident_id=incident_id,
        resolution_notes=payload.resolution_notes,
        updated_by=payload.updated_by or "NOC_ENGINEER"
    )
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return format_incident_response(inc)

@router.get("/{incident_id}/recommendations", response_model=List[RecommendationAction])
def get_incident_recommendations(incident_id: str, db: Session = Depends(get_db)):
    """Retrieve AI troubleshooting actions for this incident."""
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    if inc.recommendations:
        try:
            raw_recs = json.loads(inc.recommendations)
            return [RecommendationAction(**r) for r in raw_recs]
        except Exception:
            pass

    return [RecommendationAction(**r) for r in generate_recommendations(inc.incident_category)]
