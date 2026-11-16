"""
Pydantic schemas for request/response validation in NOC system.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# -------------------------------------------------------------------
# Device Schemas
# -------------------------------------------------------------------
class DeviceBase(BaseModel):
    id: str
    hostname: str
    device_type: str
    ip_address: str
    status: str
    location: str
    health_status: str

class DeviceCreate(DeviceBase):
    pass

class DeviceResponse(DeviceBase):
    model_config = ConfigDict(from_attributes=True)

    last_heartbeat: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class DeviceMetricSummary(DeviceResponse):
    latest_cpu: Optional[float] = None
    latest_memory: Optional[float] = None
    latest_disk: Optional[float] = None
    latest_latency: Optional[float] = None
    latest_packet_loss: Optional[float] = None


# -------------------------------------------------------------------
# Metric Schemas
# -------------------------------------------------------------------
class MetricBase(BaseModel):
    device_id: str
    cpu_utilization: float = 0.0
    memory_utilization: float = 0.0
    disk_utilization: float = 0.0
    server_uptime: float = 0.0
    process_count: int = 0
    response_time: float = 0.0
    server_availability: float = 1.0
    network_latency: float = 0.0
    packet_loss: float = 0.0
    bandwidth_utilization: float = 0.0
    network_throughput: float = 0.0
    connection_status: int = 1
    dns_response_status: int = 1
    network_availability: float = 1.0

class MetricCreate(MetricBase):
    timestamp: Optional[datetime] = None

class MetricResponse(MetricBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    timestamp: datetime

class CurrentMetricsSummary(BaseModel):
    timestamp: datetime
    total_devices: int
    online_devices: int
    avg_cpu: float
    avg_memory: float
    avg_latency: float
    avg_packet_loss: float
    active_critical_alerts: int


# -------------------------------------------------------------------
# Alert Schemas
# -------------------------------------------------------------------
class AlertBase(BaseModel):
    device_id: str
    device_hostname: str
    metric_name: str
    observed_value: float
    expected_threshold: float
    alert_description: str
    initial_severity: str

class AlertResponse(AlertBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    timestamp: datetime
    status: str
    incident_id: Optional[str] = None
    resolved_at: Optional[datetime] = None

class AlertAcknowledge(BaseModel):
    pass

class AlertResolve(BaseModel):
    notes: Optional[str] = None


# -------------------------------------------------------------------
# Incident Schemas
# -------------------------------------------------------------------
class RecommendationAction(BaseModel):
    action: str
    reason: str
    priority: str  # HIGH, MEDIUM, LOW
    expected_outcome: str
    manual_verification_required: bool = True

class IncidentBase(BaseModel):
    incident_title: str
    incident_description: str
    device_id: str
    affected_device: str
    incident_category: str
    severity: str

class IncidentCreate(IncidentBase):
    confidence_score: float = 0.0
    anomaly_score: float = 0.0
    cluster_id: int = -1
    root_cause_hypothesis: Optional[str] = None
    recommendations: Optional[str] = None

class IncidentHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    incident_id: str
    timestamp: datetime
    old_status: str
    new_status: str
    notes: Optional[str] = None
    updated_by: str

class IncidentResponse(IncidentBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    confidence_score: float
    anomaly_score: float
    cluster_id: int
    first_detected_at: datetime
    last_updated_at: datetime
    status: str
    root_cause_hypothesis: Optional[str] = None
    recommendations: Optional[str] = None
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    parsed_recommendations: Optional[List[RecommendationAction]] = None
    history: Optional[List[IncidentHistoryResponse]] = None

class IncidentStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None
    updated_by: Optional[str] = "NOC_ENGINEER"

class IncidentResolveRequest(BaseModel):
    resolution_notes: str
    updated_by: Optional[str] = "NOC_ENGINEER"


# -------------------------------------------------------------------
# ML Schemas
# -------------------------------------------------------------------
class MLPredictionResponse(BaseModel):
    timestamp: datetime
    device_id: str
    predicted_category: str
    confidence_score: float
    anomaly_score: float
    is_anomaly: bool
    cluster_id: int
    cluster_interpretation: str
    recommended_severity: str

class ModelPerformanceResponse(BaseModel):
    model_name: str
    trained_at: datetime
    metrics: Dict[str, Any]


# -------------------------------------------------------------------
# Analytics Schemas
# -------------------------------------------------------------------
class AnalyticsSummaryResponse(BaseModel):
    total_incidents: int
    active_incidents: int
    resolved_incidents: int
    mtta_minutes: float
    mttr_minutes: float
    resolution_rate: float
    severity_distribution: Dict[str, int]
    category_distribution: Dict[str, int]
    top_problematic_devices: List[Dict[str, Any]]

class IncidentTrendItem(BaseModel):
    date: str
    count: int
    critical_count: int


# -------------------------------------------------------------------
# Simulation Schemas
# -------------------------------------------------------------------
class SimulationStatusResponse(BaseModel):
    is_running: bool
    mode: str
    interval_seconds: int
    total_devices: int
    active_incidents: int
    last_tick: Optional[datetime] = None

class SimulationModeRequest(BaseModel):
    mode: str  # Normal, Warning, Critical, Random

class TriggerIncidentRequest(BaseModel):
    incident_type: str  # "Server Overload", "Network Failure", "High Latency", "Packet Loss", "DNS Failure", "Disk Capacity Issue", "Memory Exhaustion"
    device_id: Optional[str] = None
