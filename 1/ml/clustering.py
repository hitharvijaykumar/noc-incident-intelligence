"""
Unsupervised Incident Clustering using K-Means with Silhouette Evaluation.
Derives human-readable cluster profiles from mathematical centroids.
"""
import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

from backend.config import settings
from backend.utils.logger import logger
from backend.database import SessionLocal
from backend.models import ModelPerformance
from ml.preprocessing import FEATURE_COLUMNS, TARGET_COLUMN

def train_kmeans_clustering(dataset_path: Path = None, n_clusters: int = None) -> dict:
    if dataset_path is None:
        dataset_path = settings.DATA_DIR / "training_data.csv"
    if n_clusters is None:
        n_clusters = settings.N_CLUSTERS

    if not dataset_path.exists():
        from ml.generate_dataset import generate_synthetic_dataset
        generate_synthetic_dataset(12000, dataset_path)

    df = pd.read_csv(dataset_path)
    # Cluster on incidents (or full dataset)
    incident_df = df[df[TARGET_COLUMN] != "Normal"]
    if len(incident_df) < 500:
        incident_df = df

    X = incident_df[FEATURE_COLUMNS]

    logger.info("Scaling features and training KMeans with k=%d on %d samples...", n_clusters, len(X))
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(
        n_clusters=n_clusters,
        random_state=settings.RANDOM_SEED,
        n_init=10
    )
    cluster_labels = kmeans.fit_predict(X_scaled)

    # Compute silhouette score on a sample for speed and robustness
    sample_size = min(3000, len(X_scaled))
    sil_score = float(silhouette_score(X_scaled[:sample_size], cluster_labels[:sample_size]))

    # Analyze centroids in original feature scale
    centroids_original = scaler.inverse_transform(kmeans.cluster_centers_)

    cluster_profiles = {}
    for cid in range(n_clusters):
        center = centroids_original[cid]
        c_dict = dict(zip(FEATURE_COLUMNS, [round(float(v), 2) for v in center]))

        # Synthesize interpretation from centroid values
        highlights = []
        if c_dict["cpu_utilization"] >= 80.0:
            highlights.append(f"High CPU ({c_dict['cpu_utilization']}%)")
        if c_dict["memory_utilization"] >= 85.0:
            highlights.append(f"High Memory ({c_dict['memory_utilization']}%)")
        if c_dict["disk_utilization"] >= 85.0:
            highlights.append(f"High Disk ({c_dict['disk_utilization']}%)")
        if c_dict["network_latency"] >= 180.0:
            highlights.append(f"High Latency ({c_dict['network_latency']}ms)")
        if c_dict["packet_loss"] >= 5.0:
            highlights.append(f"High Packet Loss ({c_dict['packet_loss']}%)")
        if c_dict["connection_status"] < 0.5 or c_dict["server_availability"] < 0.5:
            highlights.append("Node Outage / Disconnected")
        if c_dict["dns_response_status"] < 0.5:
            highlights.append("DNS Resolution Failure")

        summary = ", ".join(highlights) if highlights else "Standard Moderate Variance"

        cluster_profiles[str(cid)] = {
            "cluster_id": cid,
            "interpretation": summary,
            "centroid": c_dict,
            "sample_count": int(np.sum(cluster_labels == cid))
        }

    metrics_result = {
        "model_name": "KMeans",
        "n_clusters": n_clusters,
        "silhouette_score": round(sil_score, 4),
        "cluster_profiles": cluster_profiles,
        "n_samples": len(X)
    }

    # Save models
    kmeans_path = settings.MODELS_DIR / "kmeans_model.joblib"
    scaler_path = settings.MODELS_DIR / "kmeans_scaler.joblib"
    joblib.dump(kmeans, kmeans_path)
    joblib.dump(scaler, scaler_path)
    logger.info("KMeans model & scaler saved to: %s", settings.MODELS_DIR)

    # Save profiles JSON
    profiles_path = settings.MODELS_DIR / "kmeans_profiles.json"
    with open(profiles_path, "w", encoding="utf-8") as f:
        json.dump(metrics_result, f, indent=2)

    # Persist in DB
    try:
        db = SessionLocal()
        perf = ModelPerformance(
            model_name="KMeans",
            metrics_json=json.dumps(metrics_result)
        )
        db.add(perf)
        db.commit()
        db.close()
    except Exception as e:
        logger.warning("Could not persist KMeans metrics to DB: %s", e)

    logger.info("KMeans Training Complete. Silhouette score: %.4f", sil_score)
    return metrics_result

if __name__ == "__main__":
    train_kmeans_clustering()
