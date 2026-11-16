"""
Supervised Random Forest Classifier for NOC Incident Classification.
Trains, evaluates, and persists the model.
"""
import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)

from backend.config import settings
from backend.utils.logger import logger
from backend.database import SessionLocal
from backend.models import ModelPerformance
from ml.preprocessing import FEATURE_COLUMNS, TARGET_COLUMN

def train_random_forest(dataset_path: Path = None) -> dict:
    if dataset_path is None:
        dataset_path = settings.DATA_DIR / "training_data.csv"

    if not dataset_path.exists():
        from ml.generate_dataset import generate_synthetic_dataset
        logger.info("Training dataset not found. Generating synthetic dataset...")
        generate_synthetic_dataset(12000, dataset_path)

    df = pd.read_csv(dataset_path)
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    # Stratified Train-Test Split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=settings.RANDOM_SEED, stratify=y
    )

    logger.info("Training RandomForestClassifier on %d samples (test=%d)...", len(X_train), len(X_test))

    rf = RandomForestClassifier(
        n_estimators=120,
        max_depth=16,
        random_state=settings.RANDOM_SEED,
        n_jobs=-1
    )
    rf.fit(X_train, y_train)

    # Predictions
    y_pred = rf.predict(X_test)

    # Metrics
    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, average="weighted", zero_division=0))
    rec = float(recall_score(y_test, y_pred, average="weighted", zero_division=0))
    f1 = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))

    labels = sorted(list(y.unique()))
    cm = confusion_matrix(y_test, y_pred, labels=labels).tolist()
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

    # Feature Importance
    feature_importance = dict(zip(FEATURE_COLUMNS, [float(v) for v in rf.feature_importances_]))
    sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)

    metrics_result = {
        "model_name": "RandomForestClassifier",
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "classes": labels,
        "confusion_matrix": cm,
        "classification_report": report,
        "feature_importances": dict(sorted_features),
        "train_samples": len(X_train),
        "test_samples": len(X_test)
    }

    # Save Model
    model_save_path = settings.MODELS_DIR / "random_forest_model.joblib"
    joblib.dump(rf, model_save_path)
    logger.info("RandomForestClassifier model saved to: %s", model_save_path)

    # Save Metrics JSON
    metrics_path = settings.MODELS_DIR / "rf_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_result, f, indent=2)

    # Persist in DB
    try:
        db = SessionLocal()
        perf = ModelPerformance(
            model_name="RandomForest",
            metrics_json=json.dumps(metrics_result)
        )
        db.add(perf)
        db.commit()
        db.close()
    except Exception as e:
        logger.warning("Could not persist performance metrics to DB: %s", e)

    logger.info("RF Model Training Complete. Accuracy: %.2f%%, F1: %.2f%%", acc * 100, f1 * 100)
    return metrics_result

if __name__ == "__main__":
    train_random_forest()
