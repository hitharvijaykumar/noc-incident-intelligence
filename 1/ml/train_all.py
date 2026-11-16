"""
Orchestrator script to generate dataset and train all 3 ML models in sequence.
"""
from pathlib import Path
from backend.config import settings
from backend.utils.logger import logger
from ml.generate_dataset import generate_synthetic_dataset
from ml.train_classifier import train_random_forest
from ml.anomaly_detection import train_isolation_forest
from ml.clustering import train_kmeans_clustering

def train_all_models():
    dataset_path = settings.DATA_DIR / "training_data.csv"
    logger.info("=== STEP 1: Generating Synthetic Dataset (12,000 samples) ===")
    generate_synthetic_dataset(12000, dataset_path)

    logger.info("=== STEP 2: Training Random Forest Classifier ===")
    rf_metrics = train_random_forest(dataset_path)

    logger.info("=== STEP 3: Training Isolation Forest Anomaly Detector ===")
    if_metrics = train_isolation_forest(dataset_path)

    logger.info("=== STEP 4: Training K-Means Clusterer ===")
    km_metrics = train_kmeans_clustering(dataset_path)

    logger.info("=== ALL ML MODELS TRAINED & PERSISTED SUCCESSFULLY ===")
    return {
        "random_forest": rf_metrics,
        "isolation_forest": if_metrics,
        "kmeans": km_metrics
    }

if __name__ == "__main__":
    train_all_models()
