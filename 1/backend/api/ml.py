"""
Machine Learning insights and model metrics API endpoints.
"""
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
from fastapi import APIRouter, Depends, Query, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.config import settings
from backend.database import get_db
from backend.models import MLPrediction, ModelPerformance
from backend.schemas import MLPredictionResponse
from ml.train_all import train_all_models
from ml.prediction import prediction_service

router = APIRouter(prefix="/api/ml", tags=["Machine Learning"])

@router.get("/performance")
def get_model_performance(db: Session = Depends(get_db)):
    """Retrieve evaluation metrics for all 3 trained ML models."""
    rf_file = settings.MODELS_DIR / "rf_metrics.json"
    if_file = settings.MODELS_DIR / "if_metrics.json"
    km_file = settings.MODELS_DIR / "kmeans_profiles.json"

    result = {}
    if rf_file.exists():
        with open(rf_file, "r", encoding="utf-8") as f:
            result["random_forest"] = json.load(f)
    else:
        result["random_forest"] = {"status": "Not trained yet. Trigger /api/ml/train."}

    if if_file.exists():
        with open(if_file, "r", encoding="utf-8") as f:
            result["isolation_forest"] = json.load(f)
    else:
        result["isolation_forest"] = {"status": "Not trained yet."}

    if km_file.exists():
        with open(km_file, "r", encoding="utf-8") as f:
            result["kmeans"] = json.load(f)
    else:
        result["kmeans"] = {"status": "Not trained yet."}

    return result

@router.get("/predictions", response_model=List[MLPredictionResponse])
def get_recent_predictions(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retrieve recent unified model inference logs."""
    preds = db.query(MLPrediction).order_by(desc(MLPrediction.timestamp)).limit(limit).all()
    return preds

@router.get("/anomalies", response_model=List[MLPredictionResponse])
def get_recent_anomalies(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retrieve records flagged as out-of-distribution anomalies by Isolation Forest."""
    anomalies = (
        db.query(MLPrediction)
        .filter(MLPrediction.is_anomaly == True)
        .order_by(desc(MLPrediction.timestamp))
        .limit(limit)
        .all()
    )
    return anomalies

@router.get("/clusters")
def get_clusters_info():
    """Retrieve K-Means cluster profiles and centroids."""
    km_file = settings.MODELS_DIR / "kmeans_profiles.json"
    if not km_file.exists():
        raise HTTPException(status_code=404, detail="K-Means model not trained yet")
    with open(km_file, "r", encoding="utf-8") as f:
        return json.load(f)

@router.post("/train")
def train_models_endpoint(background_tasks: BackgroundTasks):
    """Trigger training for all 3 ML models."""
    def run_training():
        train_all_models()
        prediction_service.load_models()

    background_tasks.add_task(run_training)
    return {"message": "Model training initiated in background. Check /api/ml/performance shortly."}
