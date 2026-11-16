"""
Unit and integration tests for ML Intelligence Engine.
"""
import pytest
from pathlib import Path
import pandas as pd
import numpy as np

from backend.config import settings
from ml.generate_dataset import generate_synthetic_dataset
from ml.train_classifier import train_random_forest
from ml.anomaly_detection import train_isolation_forest
from ml.clustering import train_kmeans_clustering
from ml.prediction import prediction_service
from ml.preprocessing import extract_feature_vector, FEATURE_COLUMNS

def test_dataset_generation(tmp_path):
    test_csv = tmp_path / "test_data.csv"
    df = generate_synthetic_dataset(n_samples=1000, output_path=test_csv)

    assert len(df) == 1000
    assert set(FEATURE_COLUMNS).issubset(df.columns)
    assert "incident_type" in df.columns
    assert len(df["incident_type"].unique()) == 8

def test_feature_extraction():
    sample_dict = {
        "cpu_utilization": 88.5,
        "memory_utilization": 60.0,
        "disk_utilization": 50.0,
        "network_latency": 25.0,
        "packet_loss": 0.1,
        "bandwidth_utilization": 45.0,
        "server_availability": 1.0,
        "dns_response_status": 1,
        "response_time": 45.0,
        "connection_status": 1,
        "process_count": 350
    }
    vec = extract_feature_vector(sample_dict)
    assert vec.shape == (1, 11)
    assert vec["cpu_utilization"].iloc[0] == 88.5

def test_full_ml_training_and_unified_prediction(tmp_path):
    test_csv = tmp_path / "ml_test_dataset.csv"
    generate_synthetic_dataset(n_samples=2000, output_path=test_csv)

    # Train all 3 models
    rf_metrics = train_random_forest(dataset_path=test_csv)
    assert rf_metrics["accuracy"] >= 0.90
    assert rf_metrics["f1_score"] >= 0.90

    if_metrics = train_isolation_forest(dataset_path=test_csv, contamination=0.05)
    assert if_metrics["anomalies_in_training_sample"] > 0

    km_metrics = train_kmeans_clustering(dataset_path=test_csv, n_clusters=4)
    assert km_metrics["n_clusters"] == 4
    assert km_metrics["silhouette_score"] > 0.1

    # Reload prediction service
    loaded = prediction_service.load_models()
    assert loaded is True

    # Test Server Overload prediction
    overload_sample = {
        "cpu_utilization": 96.0,
        "memory_utilization": 65.0,
        "disk_utilization": 50.0,
        "network_latency": 40.0,
        "packet_loss": 0.1,
        "bandwidth_utilization": 70.0,
        "server_availability": 1.0,
        "dns_response_status": 1,
        "response_time": 300.0,
        "connection_status": 1,
        "process_count": 520
    }
    pred = prediction_service.predict(overload_sample)
    assert pred["predicted_incident_type"] == "Server Overload"
    assert pred["classification_confidence"] > 0.6
    assert pred["recommended_severity"] in ["CRITICAL", "HIGH"]
    assert pred["cluster_id"] in [0, 1, 2, 3]

    # Test Network Failure prediction
    net_fail_sample = {
        "cpu_utilization": 0.0,
        "memory_utilization": 10.0,
        "disk_utilization": 40.0,
        "network_latency": 0.0,
        "packet_loss": 100.0,
        "bandwidth_utilization": 0.0,
        "server_availability": 0.0,
        "dns_response_status": 0,
        "response_time": 0.0,
        "connection_status": 0,
        "process_count": 50
    }
    pred_fail = prediction_service.predict(net_fail_sample)
    assert pred_fail["predicted_incident_type"] == "Network Failure"
    assert pred_fail["recommended_severity"] == "CRITICAL"
