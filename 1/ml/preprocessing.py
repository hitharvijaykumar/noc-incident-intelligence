"""
Feature preprocessing definitions and transformations for NOC ML models.
"""
from typing import Dict, Any, List, Union
import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "cpu_utilization",
    "memory_utilization",
    "disk_utilization",
    "network_latency",
    "packet_loss",
    "bandwidth_utilization",
    "server_availability",
    "dns_response_status",
    "response_time",
    "connection_status",
    "process_count",
]

TARGET_COLUMN = "incident_type"

def extract_feature_vector(metric_data: Union[Dict[str, Any], Any]) -> pd.DataFrame:
    """
    Extracts a pandas DataFrame with canonical feature names in exact order from a dict or ORM object.
    Fills missing values with sensible defaults.
    """
    row = {}
    for col in FEATURE_COLUMNS:
        if isinstance(metric_data, dict):
            val = metric_data.get(col)
        else:
            val = getattr(metric_data, col, None)

        if val is None or (isinstance(val, (float, int)) and np.isnan(val)):
            if col in ["server_availability", "dns_response_status", "connection_status"]:
                val = 1.0
            else:
                val = 0.0
        row[col] = float(val)

    return pd.DataFrame([row], columns=FEATURE_COLUMNS)

def prepare_dataframe_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensures input DataFrame has all required columns and fills any missing values.
    """
    clean_df = df.copy()
    for col in FEATURE_COLUMNS:
        if col not in clean_df.columns:
            if col in ["server_availability", "dns_response_status", "connection_status"]:
                clean_df[col] = 1.0
            else:
                clean_df[col] = 0.0
        clean_df[col] = pd.to_numeric(clean_df[col], errors="coerce").fillna(0.0)

    return clean_df[FEATURE_COLUMNS]
