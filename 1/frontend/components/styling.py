"""
Enterprise NOC CSS styling and visual theming.
"""
import streamlit as st

def apply_noc_theme():
    st.markdown(
        """
        <style>
        /* Base page background and font */
        .stApp {
            background-color: #0b0f19;
            color: #e2e8f0;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #0f172a !important;
            border-right: 1px solid #1e293b !important;
        }

        /* Header styling */
        header[data-testid="stHeader"] {
            background-color: #0b0f19 !important;
        }

        /* Card panels */
        .noc-card {
            background-color: #111827;
            border: 1px solid #1f2937;
            border-radius: 8px;
            padding: 18px 22px;
            margin-bottom: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
        }

        .noc-card-header {
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #94a3b8;
            font-weight: 600;
            margin-bottom: 6px;
        }

        .noc-card-value {
            font-size: 2rem;
            font-weight: 700;
            color: #f8fafc;
            line-height: 1.2;
        }

        .noc-card-sub {
            font-size: 0.8rem;
            color: #64748b;
            margin-top: 4px;
        }

        /* Status Badges */
        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.025em;
        }

        .badge-critical {
            background-color: rgba(239, 68, 68, 0.2);
            color: #ef4444;
            border: 1px solid #ef4444;
        }

        .badge-high {
            background-color: rgba(249, 115, 22, 0.2);
            color: #f97316;
            border: 1px solid #f97316;
        }

        .badge-medium {
            background-color: rgba(245, 158, 11, 0.2);
            color: #f59e0b;
            border: 1px solid #f59e0b;
        }

        .badge-low {
            background-color: rgba(59, 130, 246, 0.2);
            color: #3b82f6;
            border: 1px solid #3b82f6;
        }

        .badge-healthy, .badge-normal {
            background-color: rgba(16, 185, 129, 0.2);
            color: #10b981;
            border: 1px solid #10b981;
        }

        .badge-investigating {
            background-color: rgba(168, 85, 247, 0.2);
            color: #a855f7;
            border: 1px solid #a855f7;
        }

        .badge-resolved {
            background-color: rgba(100, 116, 139, 0.2);
            color: #94a3b8;
            border: 1px solid #475569;
        }

        /* Pulsing indicator */
        .pulse-dot {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background-color: #10b981;
            box-shadow: 0 0 8px #10b981;
            margin-right: 6px;
        }
        .pulse-dot-red {
            background-color: #ef4444;
            box-shadow: 0 0 8px #ef4444;
        }
        .pulse-dot-orange {
            background-color: #f97316;
            box-shadow: 0 0 8px #f97316;
        }

        /* Streamlit widget tweaks */
        div[data-testid="stMetricValue"] {
            color: #f8fafc !important;
            font-size: 1.8rem !important;
            font-weight: 700 !important;
        }
        div[data-testid="stMetricDelta"] {
            font-size: 0.85rem !important;
        }
        div[data-testid="metric-container"] {
            background-color: #111827 !important;
            border: 1px solid #1f2937 !important;
            border-radius: 8px !important;
            padding: 12px 16px !important;
        }

        /* Table styling */
        div[data-testid="stDataFrame"] {
            border: 1px solid #1f2937;
            border-radius: 8px;
            overflow: hidden;
        }

        /* Buttons */
        .stButton button {
            background-color: #1f2937;
            color: #f8fafc;
            border: 1px solid #374151;
            border-radius: 6px;
            font-weight: 500;
            transition: all 0.15s ease-in-out;
        }
        .stButton button:hover {
            background-color: #374151;
            border-color: #4b5563;
            color: #ffffff;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #0f172a;
            border-radius: 8px;
            padding: 4px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 6px;
            padding: 8px 16px;
            color: #94a3b8;
        }
        .stTabs [aria-selected="true"] {
            background-color: #1e293b !important;
            color: #38bdf8 !important;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_kpi_card(title: str, value: str, subtext: str = "", border_color: str = "#1f2937"):
    return f"""
    <div class="noc-card" style="border-left: 4px solid {border_color};">
        <div class="noc-card-header">{title}</div>
        <div class="noc-card-value">{value}</div>
        <div class="noc-card-sub">{subtext}</div>
    </div>
    """

def get_severity_badge(severity: str) -> str:
    s = severity.upper()
    if s == "CRITICAL":
        return '<span class="badge badge-critical">CRITICAL</span>'
    elif s == "HIGH":
        return '<span class="badge badge-high">HIGH</span>'
    elif s == "MEDIUM":
        return '<span class="badge badge-medium">MEDIUM</span>'
    elif s == "LOW":
        return '<span class="badge badge-low">LOW</span>'
    return f'<span class="badge badge-low">{s}</span>'

def get_status_badge(status: str) -> str:
    s = status.upper()
    if s == "NEW":
        return '<span class="badge badge-critical">NEW</span>'
    elif s == "ACKNOWLEDGED":
        return '<span class="badge badge-medium">ACKNOWLEDGED</span>'
    elif s == "INVESTIGATING":
        return '<span class="badge badge-investigating">INVESTIGATING</span>'
    elif s in ["RESOLVED", "CLOSED"]:
        return '<span class="badge badge-resolved">RESOLVED</span>'
    elif s in ["ONLINE", "HEALTHY"]:
        return '<span class="badge badge-healthy">ONLINE</span>'
    elif s == "DEGRADED":
        return '<span class="badge badge-high">DEGRADED</span>'
    elif s == "OFFLINE":
        return '<span class="badge badge-critical">OFFLINE</span>'
    return f'<span class="badge">{s}</span>'
