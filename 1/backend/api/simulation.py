"""
Simulation controls API endpoints.
"""
from fastapi import APIRouter, HTTPException
from backend.schemas import SimulationStatusResponse, SimulationModeRequest, TriggerIncidentRequest
from backend.services.monitoring_service import monitoring_service
from simulator.infrastructure_simulator import simulator_instance

router = APIRouter(prefix="/api/simulation", tags=["Simulation"])

@router.get("/status", response_model=SimulationStatusResponse)
def get_simulation_status():
    """Retrieve the operational status of the infrastructure simulator."""
    return SimulationStatusResponse(
        is_running=monitoring_service.is_running,
        mode=simulator_instance.event_generator.current_mode,
        interval_seconds=monitoring_service.interval_seconds,
        total_devices=len(simulator_instance.device_meta),
        active_incidents=len(simulator_instance.event_generator.active_injections),
        last_tick=monitoring_service.last_tick_time
    )

@router.post("/start")
def start_simulation():
    """Start background continuous metric telemetry polling."""
    monitoring_service.start()
    return {"message": "Simulation monitoring started", "is_running": True}

@router.post("/stop")
def stop_simulation():
    """Stop background continuous metric telemetry polling."""
    monitoring_service.stop()
    return {"message": "Simulation monitoring stopped", "is_running": False}

@router.post("/mode")
def set_simulation_mode(payload: SimulationModeRequest):
    """Set global simulation operational mode: Normal, Warning, Critical, or Random."""
    mode = payload.mode
    if mode not in ["Normal", "Warning", "Critical", "Random"]:
        raise HTTPException(status_code=400, detail="Invalid mode. Must be Normal, Warning, Critical, or Random.")
    simulator_instance.set_mode(mode)
    return {"message": f"Simulation mode set to {mode}", "mode": mode}

@router.post("/trigger-incident")
def trigger_incident(payload: TriggerIncidentRequest):
    """Manually inject a synthetic fault into a device."""
    target_device = simulator_instance.trigger_incident(
        incident_type=payload.incident_type,
        device_id=payload.device_id
    )
    # Immediately step the monitoring engine once to capture and process the fault
    monitoring_service.step_once()

    return {
        "message": f"Triggered '{payload.incident_type}' on device '{target_device}'.",
        "incident_type": payload.incident_type,
        "device_id": target_device
    }
