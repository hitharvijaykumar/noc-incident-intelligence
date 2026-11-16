"""
SQLAlchemy ORM models for NOC Incident Intelligence System.
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Index
)
from sqlalchemy.orm import relationship
from backend.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Device(Base):
    __tablename__ = "devices"

    id = Column(String(50), primary_key=True, index=True)
    hostname = Column(String(100), nullable=False, unique=True, index=True)
    device_type = Column(String(50), nullable=False)  # server, router, switch, firewall
    ip_address = Column(String(45), nullable=False)
    status = Column(String(20), default="ONLINE", nullable=False)  # ONLINE, DEGRADED, OFFLINE
    location = Column(String(100), nullable=False)
    last_heartbeat = Column(DateTime, default=utc_now)
    health_status = Column(String(20), default="HEALTHY", nullable=False)  # HEALTHY, WARNING, CRITICAL
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    metrics = relationship("MetricHistory", back_populates="device", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="device", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="device", cascade="all, delete-orphan")
    predictions = relationship("MLPrediction", back_populates="device", cascade="all, delete-orphan")


class MetricHistory(Base):
    __tablename__ = "metric_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(50), ForeignKey("devices.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=utc_now, index=True)

    # Server metrics
    cpu_utilization = Column(Float, default=0.0)
    memory_utilization = Column(Float, default=0.0)
    disk_utilization = Column(Float, default=0.0)
    server_uptime = Column(Float, default=0.0)  # hours
    process_count = Column(Integer, default=0)
    response_time = Column(Float, default=0.0)  # ms
    server_availability = Column(Float, default=1.0)  # 0.0 - 1.0

    # Network metrics
    network_latency = Column(Float, default=0.0)  # ms
    packet_loss = Column(Float, default=0.0)  # %
    bandwidth_utilization = Column(Float, default=0.0)  # %
    network_throughput = Column(Float, default=0.0)  # Mbps
    connection_status = Column(Integer, default=1)  # 1=connected, 0=disconnected
    dns_response_status = Column(Integer, default=1)  # 1=success, 0=failure
    network_availability = Column(Float, default=1.0)  # 0.0 - 1.0

    device = relationship("Device", back_populates="metrics")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(50), primary_key=True, index=True)
    timestamp = Column(DateTime, default=utc_now, index=True)
    device_id = Column(String(50), ForeignKey("devices.id"), nullable=False, index=True)
    device_hostname = Column(String(100), nullable=False)
    metric_name = Column(String(50), nullable=False)
    observed_value = Column(Float, nullable=False)
    expected_threshold = Column(Float, nullable=False)
    alert_description = Column(String(255), nullable=False)
    initial_severity = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(20), default="ACTIVE", nullable=False)  # ACTIVE, ACKNOWLEDGED, RESOLVED, SUPPRESSED
    incident_id = Column(String(50), ForeignKey("incidents.id"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    device = relationship("Device", back_populates="alerts")
    incident = relationship("Incident", back_populates="alerts")


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(50), primary_key=True, index=True)
    incident_title = Column(String(200), nullable=False)
    incident_description = Column(Text, nullable=False)
    device_id = Column(String(50), ForeignKey("devices.id"), nullable=False, index=True)
    affected_device = Column(String(100), nullable=False)
    incident_category = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    confidence_score = Column(Float, default=0.0)
    anomaly_score = Column(Float, default=0.0)
    cluster_id = Column(Integer, default=-1)
    first_detected_at = Column(DateTime, default=utc_now, index=True)
    last_updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    status = Column(String(20), default="NEW", nullable=False, index=True)  # NEW, ACKNOWLEDGED, INVESTIGATING, RESOLVED, CLOSED
    root_cause_hypothesis = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)  # JSON-encoded string
    resolution_notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    device = relationship("Device", back_populates="incidents")
    alerts = relationship("Alert", back_populates="incident")
    history = relationship("IncidentHistory", back_populates="incident", cascade="all, delete-orphan")


class IncidentHistory(Base):
    __tablename__ = "incident_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    incident_id = Column(String(50), ForeignKey("incidents.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=utc_now)
    old_status = Column(String(20), nullable=False)
    new_status = Column(String(20), nullable=False)
    notes = Column(Text, nullable=True)
    updated_by = Column(String(50), default="SYSTEM")

    incident = relationship("Incident", back_populates="history")


class MLPrediction(Base):
    __tablename__ = "ml_predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=utc_now, index=True)
    device_id = Column(String(50), ForeignKey("devices.id"), nullable=False, index=True)
    predicted_category = Column(String(100), nullable=False)
    confidence_score = Column(Float, default=0.0)
    anomaly_score = Column(Float, default=0.0)
    is_anomaly = Column(Boolean, default=False)
    cluster_id = Column(Integer, default=-1)
    cluster_interpretation = Column(String(255), nullable=True)
    recommended_severity = Column(String(20), nullable=False)

    device = relationship("Device", back_populates="predictions")


class SimulationEvent(Base):
    __tablename__ = "simulation_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=utc_now, index=True)
    mode = Column(String(50), nullable=False)
    event_type = Column(String(100), nullable=False)
    target_device_id = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)


class ModelPerformance(Base):
    __tablename__ = "model_performance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(50), nullable=False, index=True)
    trained_at = Column(DateTime, default=utc_now)
    metrics_json = Column(Text, nullable=False)
