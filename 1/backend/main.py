"""
FastAPI application entrypoint for AI-Powered NOC Incident Intelligence System.
"""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import init_db
from backend.utils.logger import logger
from backend.services.monitoring_service import monitoring_service
from simulator.infrastructure_simulator import simulator_instance
from ml.prediction import prediction_service

# Routers
from backend.api.devices import router as devices_router
from backend.api.monitoring import router as monitoring_router
from backend.api.alerts import router as alerts_router
from backend.api.incidents import router as incidents_router
from backend.api.ml import router as ml_router
from backend.api.analytics import router as analytics_router
from backend.api.simulation import router as simulation_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    logger.info("Initializing %s...", settings.APP_NAME)
    init_db()
    simulator_instance.seed_devices_in_db()

    # Verify/Train ML Models
    rf_file = settings.MODELS_DIR / "random_forest_model.joblib"
    if not rf_file.exists():
        logger.info("ML models not found on disk. Initiating automated training sequence...")
        from ml.train_all import train_all_models
        train_all_models()

    prediction_service.load_models()

    # Pre-seed initial telemetry steps if DB is freshly created
    import os
    if os.environ.get("TESTING") != "1":
        logger.info("Seeding initial telemetry baseline...")
        for _ in range(3):
            monitoring_service.step_once()

        # Start continuous background monitoring
        monitoring_service.start()
        logger.info("NOC System is operational and monitoring background active.")

    yield

    # --- Shutdown ---
    if os.environ.get("TESTING") != "1":
        logger.info("Shutting down NOC System...")
        monitoring_service.stop()
        logger.info("NOC System shutdown complete.")

app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise-grade AI/ML Infrastructure Monitoring & Automated Incident Intelligence",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(devices_router)
app.include_router(monitoring_router)
app.include_router(alerts_router)
app.include_router(incidents_router)
app.include_router(ml_router)
app.include_router(analytics_router)
app.include_router(simulation_router)

@app.get("/api/health", tags=["Health"])
def health_check():
    """Health probe verifying API status and backend subsystems."""
    return {
        "status": "HEALTHY",
        "timestamp": datetime.now(timezone.utc),
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "monitoring_active": monitoring_service.is_running,
        "models_loaded": prediction_service.is_loaded
    }

@app.get("/", tags=["Health"])
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs_url": "/docs",
        "health_url": "/api/health"
    }
