"""
Page 4: Machine Learning Intelligence, Model Evaluation & Anomaly Analytics.
"""
import streamlit as st
import pandas as pd
import numpy as np

from frontend.components.styling import apply_noc_theme, render_kpi_card
from frontend.components.charts import (
    create_confusion_matrix_chart, create_feature_importance_chart,
    create_cluster_scatter_chart
)
from frontend.components.simulation_controls import render_simulation_controls
from frontend.api_client import (
    fetch_ml_performance, fetch_ml_predictions, fetch_ml_anomalies,
    fetch_ml_clusters, trigger_ml_train
)

apply_noc_theme()
render_simulation_controls()

st.markdown("## 🧠 Machine Learning Intelligence Engine")
st.markdown('<div style="color:#94a3b8; font-size:0.9rem; margin-top:-10px;">Ensemble Supervised Classification, Unsupervised Anomaly Detection & Incident Clustering</div>', unsafe_allow_html=True)

col_top, col_train = st.columns([4, 1])
with col_top:
    st.markdown(
        """
        The NOC AI subsystem integrates three complementary machine learning architectures:
        1. **Random Forest Classifier**: Supervised multiclass diagnostic engine mapping 11 telemetry features into 8 failure classes.
        2. **Isolation Forest**: Unsupervised isolation trees calculating decision boundaries for novel zero-day infrastructure anomalies.
        3. **K-Means Clustering**: Unsupervised vector quantization grouping recurrent failure topologies based on centroid signatures.
        """
    )
with col_train:
    if st.button("🚀 Retrain All Models", use_container_width=True):
        res = trigger_ml_train()
        if res:
            st.toast("Model retraining pipeline launched in background!", icon="⚙️")
        else:
            st.error("Failed to trigger training.")

# 1. Fetch Performance Metrics
perf = fetch_ml_performance()
rf_perf = perf.get("random_forest", {})
if_perf = perf.get("isolation_forest", {})
km_perf = perf.get("kmeans", {})

st.markdown("---")
st.subheader("1. Supervised Random Forest Classifier Performance")

if "accuracy" in rf_perf:
    acc = rf_perf.get("accuracy", 0.0)
    prec = rf_perf.get("precision", 0.0)
    rec = rf_perf.get("recall", 0.0)
    f1 = rf_perf.get("f1_score", 0.0)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(render_kpi_card("Overall Accuracy", f"{acc*100:.2f}%", f"Test set: {rf_perf.get('test_samples', 0)} samples", "#10b981"), unsafe_allow_html=True)
    with k2:
        st.markdown(render_kpi_card("Weighted Precision", f"{prec*100:.2f}%", "True positive fidelity", "#38bdf8"), unsafe_allow_html=True)
    with k3:
        st.markdown(render_kpi_card("Weighted Recall", f"{rec*100:.2f}%", "Coverage across failure types", "#a855f7"), unsafe_allow_html=True)
    with k4:
        st.markdown(render_kpi_card("Weighted F1-Score", f"{f1*100:.2f}%", "Harmonic mean metric", "#f59e0b"), unsafe_allow_html=True)

    rf_c1, rf_c2 = st.columns([3, 2])
    with rf_c1:
        cm = rf_perf.get("confusion_matrix", [])
        classes = rf_perf.get("classes", [])
        if cm and classes:
            fig_cm = create_confusion_matrix_chart(cm, classes)
            st.plotly_chart(fig_cm, use_container_width=True)
    with rf_c2:
        feat_imp = rf_perf.get("feature_importances", {})
        if feat_imp:
            fig_feat = create_feature_importance_chart(feat_imp, top_n=10)
            st.plotly_chart(fig_feat, use_container_width=True)
else:
    st.warning("Random Forest model metrics not available. Click 'Retrain All Models' above.")

st.markdown("---")

# 2. Isolation Forest & K-Means Row
row2_c1, row2_c2 = st.columns(2)

with row2_c1:
    st.subheader("2. Isolation Forest Anomaly Detection")
    if "contamination" in if_perf:
        st.markdown(
            f"""
            - **Contamination Ratio:** `{if_perf.get('contamination', 0.05)}`
            - **Trained Baseline Samples:** `{if_perf.get('n_samples', 0)}`
            - **Training Anomalies Detected:** `{if_perf.get('anomalies_in_training_sample', 0)} ({if_perf.get('anomaly_percentage', 0)}%)`
            - **Decision Function Score Range:** `[{if_perf.get('min_score', 0):.4f}, {if_perf.get('max_score', 0):.4f}]` (Scores `< 0.0` denote anomaly)
            """
        )

        anomalies = fetch_ml_anomalies(limit=8)
        if anomalies:
            st.markdown("**Recent Anomaly Detections:**")
            df_ano = pd.DataFrame([
                {
                    "Time": a["timestamp"][:19].replace("T", " "),
                    "Device": a["device_id"],
                    "Score": a["anomaly_score"],
                    "Predicted Class": a["predicted_category"],
                    "Severity": a["recommended_severity"]
                }
                for a in anomalies
            ])
            st.dataframe(df_ano, use_container_width=True, hide_index=True)
        else:
            st.info("No anomalies detected in recent telemetry stream.")
    else:
        st.info("Isolation Forest metrics not initialized.")

with row2_c2:
    st.subheader("3. K-Means Incident Clustering")
    if "silhouette_score" in km_perf:
        st.markdown(
            f"""
            - **Configured Clusters (k):** `{km_perf.get('n_clusters', 4)}`
            - **Silhouette Quality Score:** `{km_perf.get('silhouette_score', 0):.4f}`
            """
        )
        profiles = km_perf.get("cluster_profiles", {})
        for cid, pdata in profiles.items():
            st.markdown(
                f"""
                <div style="background:#111827; border:1px solid #1f2937; border-left:3px solid #38bdf8; border-radius:4px; padding:6px 12px; margin-bottom:6px;">
                    <b style="color:#38bdf8;">Cluster {cid}:</b> <span style="color:#e2e8f0; font-size:0.85rem;">{pdata.get('interpretation')}</span>
                    <span style="font-size:0.75rem; color:#64748b; margin-left:8px;">({pdata.get('sample_count', 0)} members)</span>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("K-Means profiles not initialized.")

st.markdown("---")

# 3. Live Unified Prediction Stream
st.subheader("4. Live Unified ML Ingestion Stream")
recent_preds = fetch_ml_predictions(limit=15)
if recent_preds:
    df_preds = pd.DataFrame([
        {
            "Time": p["timestamp"][:19].replace("T", " "),
            "Device ID": p["device_id"],
            "Predicted Category": p["predicted_category"],
            "Confidence": f"{p['confidence_score']*100:.1f}%",
            "Anomaly Score": p["anomaly_score"],
            "Is Anomaly": "⚠️ YES" if p["is_anomaly"] else "NORMAL",
            "Cluster ID": p["cluster_id"],
            "Recommended Severity": p["recommended_severity"]
        }
        for p in recent_preds
    ])
    st.dataframe(df_preds, use_container_width=True, hide_index=True)
else:
    st.info("No recent predictions recorded yet.")
