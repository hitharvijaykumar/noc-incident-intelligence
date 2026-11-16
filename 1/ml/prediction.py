"""
Unified ML Prediction Service combining Random Forest, Isolation Forest, and K-Means.
Provides resilient inference with clear error handling when models are missing.
"""
import json
import joblib
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np

from backend.config import settings
from backend.utils.logger import logger
from backend.utils.severity import calculate_severity
from ml.preprocessing import extract_feature_vector, FEATURE_COLUMNS

class MLPredictionService:
    def __init__(self):
        self.rf_model = None
        self.iso_forest = None
        self.kmeans_model = None
        self.kmeans_scaler = None
        self.cluster_profiles: Dict[str, Any] = {}
        self.is_loaded = False
        self.load_models()

    def load_models(self) -> bool:
        """
        Attempts to load all 3 trained models and metadata.
        Returns True if all are loaded successfully, False otherwise.
        """
        rf_path = settings.MODELS_DIR / "random_forest_model.joblib"
        if_path = settings.MODELS_DIR / "isolation_forest_model.joblib"
        km_path = settings.MODELS_DIR / "kmeans_model.joblib"
        sc_path = settings.MODELS_DIR / "kmeans_scaler.joblib"
        prof_path = settings.MODELS_DIR / "kmeans_profiles.json"

        missing = []
        if not rf_path.exists(): missing.append("Random Forest")
        if not if_path.exists(): missing.append("Isolation Forest")
        if not km_path.exists(): missing.append("K-Means")
        if not sc_path.exists(): missing.append("K-Means Scaler")

        if missing:
            logger.warning(
                "Missing ML models: %s. Run 'python -m ml.train_all' or invoke training via API.",
                ", ".join(missing)
            )
            self.is_loaded = False
            return False

        try:
            self.rf_model = joblib.load(rf_path)
            self.iso_forest = joblib.load(if_path)
            self.kmeans_model = joblib.load(km_path)
            self.kmeans_scaler = joblib.load(sc_path)

            if prof_path.exists():
                with open(prof_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.cluster_profiles = data.get("cluster_profiles", {})

            self.is_loaded = True
            logger.info("All ML models loaded successfully.")
            return True
        except Exception as e:
            logger.error("Failed to load ML models: %s", e)
            self.is_loaded = False
            return False

    def predict(self, metric_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Computes unified ML predictions for a single metric telemetry dictionary.
        Raises RuntimeError if models have not yet been trained.
        """
        if not self.is_loaded:
            loaded = self.load_models()
            if not loaded:
                raise RuntimeError(
                    "ML models are not trained yet. Run 'python -m ml.train_all' to initialize models."
                )

        # 1. Feature extraction
        X = extract_feature_vector(metric_dict)

        # 2. Random Forest Classification
        rf_pred = self.rf_model.predict(X)[0]
        rf_probas = self.rf_model.predict_proba(X)[0]
        class_idx = list(self.rf_model.classes_).index(rf_pred)
        confidence = float(rf_probas[class_idx])

        # 3. Isolation Forest Anomaly Detection
        anomaly_score = float(self.iso_forest.decision_function(X)[0])
        iso_pred = int(self.iso_forest.predict(X)[0])
        is_anomaly = bool(iso_pred == -1)

        # 4. K-Means Clustering
        X_scaled = self.kmeans_scaler.transform(X)
        cluster_id = int(self.kmeans_model.predict(X_scaled)[0])
        cluster_info = self.cluster_profiles.get(str(cluster_id), {})
        cluster_interpretation = cluster_info.get("interpretation", f"Cluster {cluster_id}")

        # 5. Hybrid Severity Assignment
        severity = calculate_severity(
            category=rf_pred,
            metrics=metric_dict,
            is_anomaly=is_anomaly,
            anomaly_score=anomaly_score
        )

        return {
            "predicted_incident_type": rf_pred,
            "classification_confidence": round(confidence, 4),
            "anomaly_score": round(anomaly_score, 4),
            "anomaly_status": "ANOMALY" if is_anomaly else "NORMAL",
            "is_anomaly": is_anomaly,
            "cluster_id": cluster_id,
            "cluster_interpretation": cluster_interpretation,
            "recommended_severity": severity
        }

# Global singleton instance
prediction_service = MLPredictionService()
