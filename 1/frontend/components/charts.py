"""
Plotly charts with dark NOC enterprise styling.
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

NOC_PLOT_LAYOUT = {
    "template": "plotly_dark",
    "paper_bgcolor": "#111827",
    "plot_bgcolor": "#111827",
    "font": {"color": "#94a3b8", "family": "Inter, sans-serif"},
    "margin": {"l": 40, "r": 20, "t": 40, "b": 40},
    "xaxis": {
        "gridcolor": "#1f2937",
        "zerolinecolor": "#1f2937",
        "showline": True,
        "linecolor": "#374151"
    },
    "yaxis": {
        "gridcolor": "#1f2937",
        "zerolinecolor": "#1f2937",
        "showline": True,
        "linecolor": "#374151"
    },
    "legend": {"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1}
}

SEVERITY_COLORS = {
    "CRITICAL": "#ef4444",
    "HIGH": "#f97316",
    "MEDIUM": "#f59e0b",
    "LOW": "#3b82f6",
    "Normal": "#10b981"
}

def create_time_series_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    y_unit: str = "%",
    warning_thresh: Optional[float] = None,
    critical_thresh: Optional[float] = None,
    line_color: str = "#38bdf8"
) -> go.Figure:
    fig = go.Figure()

    if not df.empty and x_col in df.columns and y_col in df.columns:
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode="lines+markers",
            name=y_col,
            line=dict(color=line_color, width=2.5),
            marker=dict(size=4),
            fill="tozeroy",
            fillcolor=f"rgba{tuple(list(int(line_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + [0.08])}"
        ))

    if warning_thresh is not None:
        fig.add_hline(
            y=warning_thresh,
            line_dash="dash",
            line_color="#f59e0b",
            annotation_text=f"Warning ({warning_thresh}{y_unit})",
            annotation_position="bottom right",
            annotation_font_color="#f59e0b"
        )

    if critical_thresh is not None:
        fig.add_hline(
            y=critical_thresh,
            line_dash="dash",
            line_color="#ef4444",
            annotation_text=f"Critical ({critical_thresh}{y_unit})",
            annotation_position="top right",
            annotation_font_color="#ef4444"
        )

    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="#f8fafc")),
        yaxis_title=y_unit,
        height=280,
        **NOC_PLOT_LAYOUT
    )
    return fig

def create_donut_chart(data_dict: Dict[str, int], title: str) -> go.Figure:
    labels = list(data_dict.keys())
    values = list(data_dict.values())

    colors = [SEVERITY_COLORS.get(label, "#64748b") for label in labels]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker=dict(colors=colors, line=dict(color="#111827", width=2)),
        textinfo="label+value",
        insidetextorientation="radial"
    )])

    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="#f8fafc")),
        height=280,
        showlegend=False,
        **NOC_PLOT_LAYOUT
    )
    return fig

def create_bar_chart(categories: List[str], counts: List[int], title: str, color: str = "#6366f1") -> go.Figure:
    fig = go.Figure(data=[go.Bar(
        x=categories,
        y=counts,
        marker=dict(color=color, line=dict(color="#1f2937", width=1))
    )])

    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="#f8fafc")),
        height=280,
        **NOC_PLOT_LAYOUT
    )
    return fig

def create_confusion_matrix_chart(cm_data: List[List[int]], classes: List[str]) -> go.Figure:
    fig = go.Figure(data=go.Heatmap(
        z=cm_data,
        x=classes,
        y=classes,
        colorscale="Blues",
        showscale=True,
        text=cm_data,
        texttemplate="%{text}",
        textfont={"size": 11, "color": "white"}
    ))

    fig.update_layout(
        title=dict(text="Confusion Matrix (Classification Accuracy)", font=dict(size=14, color="#f8fafc")),
        xaxis_title="Predicted Class",
        yaxis_title="True Class",
        height=420,
        **NOC_PLOT_LAYOUT
    )
    return fig

def create_feature_importance_chart(feat_dict: Dict[str, float], top_n: int = 10) -> go.Figure:
    sorted_items = sorted(feat_dict.items(), key=lambda x: x[1], reverse=True)[:top_n]
    features = [x[0] for x in reversed(sorted_items)]
    importances = [x[1] for x in reversed(sorted_items)]

    fig = go.Figure(go.Bar(
        x=importances,
        y=features,
        orientation="h",
        marker=dict(
            color=importances,
            colorscale="Viridis",
            line=dict(color="#1f2937", width=1)
        )
    ))

    fig.update_layout(
        title=dict(text=f"Top {top_n} Feature Importances (Random Forest)", font=dict(size=14, color="#f8fafc")),
        xaxis_title="Importance Score",
        height=380,
        **NOC_PLOT_LAYOUT
    )
    return fig

def create_cluster_scatter_chart(records: List[Dict[str, Any]]) -> go.Figure:
    df = pd.DataFrame(records)
    if df.empty or "cpu_utilization" not in df.columns:
        fig = go.Figure()
    else:
        fig = px.scatter(
            df,
            x="cpu_utilization",
            y="network_latency",
            color="cluster_id",
            hover_data=["device_id", "predicted_category"],
            title="K-Means Cluster Space (CPU % vs Latency ms)",
            color_continuous_scale="Turbo"
        )
    fig.update_layout(
        height=380,
        **NOC_PLOT_LAYOUT
    )
    return fig
