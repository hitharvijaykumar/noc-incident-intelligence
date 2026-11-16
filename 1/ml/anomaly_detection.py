"""
Unsupervised Anomaly Detection using Isolation Forest.
Trained on baseline normal operations to detect novel out-of-distribution patterns.
"""
import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import IsolationForest

from backend.config import settings
from backend.utils.logger import logger
from backend.database import SessionLocal
from backend.models import ModelPerformance
from ml.preprocessing import FEATURE_COLUMNS, TARGET_COLUMN

def train_isolation_forest(dataset_path: Path = None, contamination: float = None) -> dict:
    if dataset_path is None:
        dataset_path = settings.DATA_DIR / "training_data.csv"
    if contamination is None:
        contamination = settings.ANOMALY_CONTAMINATION

    if not dataset_path.exists():
        from ml.generate_dataset import generate_synthetic_dataset
        generate_synthetic_dataset(12000, dataset_path)

    df = pd.read_csv(dataset_path)
    # Train primarily on Normal baseline data with small contamination
    normal_df = df[df[TARGET_COLUMN] == "Normal"]
    if len(normal_df) < 500:
        normal_df = df  # fallback

    X = normal_df[FEATURE_COLUMNS]

    logger.info("Training IsolationForest on %d normal baseline records with contamination=%.2f...", len(X), contamination)

    iso_forest = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=settings.RANDOM_SEED,
        n_jobs=-1
    )
    iso_forest.fit(X)

    # Score sample evaluation
    scores = iso_forest.decision_function(X)
    preds = iso_forest.predict(X)
    anomalies_detected = int((preds == -1).sum())

    metrics_result = {
        "model_name": "IsolationForest",
        "contamination": contamination,
        "n_samples": len(X),
        "anomalies_in_training_sample": anomalies_detected,
        "anomaly_percentage": round((anomalies_detected / len(X)) * 100, 2),
        "mean_score": round(float(np.mean(scores)), 4),
        "min_score": round(float(np.min(scores)), 4),
        "max_score": round(float(np.max(scores)), 4),
    }

    # Save model
    model_save_path = settings.MODELS_DIR / "isolation_forest_model.joblib"
    joblib.dump(iso_forest, model_save_path)
    logger.info("IsolationForest model saved to: %s", model_save_path)

    # Save metrics JSON
    metrics_path = settings.MODELS_DIR / "if_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_result, f, indent=2)

    # Persist in DB
    try:
        db = SessionLocal()
        perf = ModelPerformance(
            model_name="IsolationForest",
            metrics_json=json.dumps(metrics_result)
        )
        db.add(perf)
        db.commit()
        db.close()
    except Exception as e:
        logger.warning("Could not persist IF metrics to DB: %s", e)

    logger.info("Isolation Forest Training Complete.")
    return metrics_result

if __name__ == "__main__":
    train_isolation_forest()
