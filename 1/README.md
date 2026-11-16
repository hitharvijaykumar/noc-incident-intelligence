# AI-Powered Network Operations Center (NOC) Incident Intelligence System

[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B.svg)](https://streamlit.io)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4%2B-F7931E.svg)](https://scikit-learn.org)
[![Tests](https://img.shields.io/badge/tests-17%20passed-brightgreen.svg)]()

---

## 1. Project Overview

The **AI-Powered Network Operations Center (NOC) Incident Intelligence System** is an enterprise-grade autonomous monitoring and incident triage platform. It simulates a distributed corporate infrastructure environment consisting of **10 heterogeneous servers** and **5 network routing/security nodes**, collecting high-frequency system and network telemetry.

The platform fuses **multi-tier threshold rule engines** with an **ensemble of three distinct Machine Learning algorithms** to predict failure categories, flag out-of-distribution zero-day anomalies, group recurring fault topologies, assess dynamic operational severity, generate root-cause hypotheses, and provide structured troubleshooting playbooks for site reliability and NOC engineers.

---

## 2. Problem Statement

Modern enterprise networks generate millions of telemetry metrics per hour. Traditional NOC operations face several critical bottlenecks:
- **Alert Fatigue:** A single root issue (e.g., link degradation) creates storms of cascading duplicate alerts across downstream servers.
- **Delayed Root Cause Isolation:** Operators spend crucial MTTA/MTTR minutes determining whether high response time is caused by CPU thrashing, memory leaks, disk block exhaustion, DNS timeouts, or intermediate packet loss.
- **Unmodeled Zero-Day Degradation:** Rule-based thresholds fail to catch complex, non-linear metric combinations that deviate from normal diurnal patterns.

---

## 3. Objectives

- Implement continuous, non-blocking telemetry ingestion across simulated servers and network switches/routers.
- Eliminate duplicate alert storms through intelligent active alert suppression and grouping.
- Deploy an **ensemble ML engine** combining:
  1. **Random Forest Classifier** for 8-class incident diagnosis.
  2. **Isolation Forest** for unsupervised zero-day anomaly detection.
  3. **K-Means Clustering** for topological failure grouping and centroid profiling.
- Compute dynamic incident severity considering availability, multi-node correlation, and operational blast radius.
- Provide interactive AI troubleshooting recommendations with verification safety flags.
- Present a modern, high-contrast Dark NOC Command Center UI using Streamlit and Plotly.

---

## 4. Key Features

- **Continuous Infrastructure Simulator:** Simulates 15 physical/virtual nodes with realistic diurnal rhythms, Gaussian noise, correlated dependencies, and multiple operational modes (Normal, Warning, Critical, Random, Manual).
- **Rule Engine & Deduplication:** Configurable thresholds across CPU, Memory, Disk, Latency, and Packet Loss with automatic alert suppression.
- **Supervised Incident Classification:** Predicts 8 operational categories (`Server Overload`, `Network Failure`, `High Latency`, `Packet Loss`, `DNS Failure`, `Disk Capacity Issue`, `Memory Exhaustion`, `Normal`) with class probabilities.
- **Unsupervised Anomaly Scoring:** Uses Isolation Forest decision functions to detect out-of-distribution behavior.
- **Pattern Clustering:** Unsupervised K-Means clustering with automatic mathematical centroid interpretation.
- **Multi-Device Correlation:** Identifies shared upstream failures when multiple datacenter nodes degrade concurrently.
- **Incident Lifecycle Management:** Tracks status through `NEW ➔ ACKNOWLEDGED ➔ INVESTIGATING ➔ RESOLVED ➔ CLOSED` with full audit history.
- **Automated Advisory Playbooks:** Tailored step-by-step remediation procedures with priority indicators and manual check requirements.
- **Operational Analytics:** Real-time MTTA, MTTR, SLA reliability calculation, and problematic node rankings.

---

## 5. Technology Stack

- **Backend:** Python 3.12, FastAPI, Uvicorn, Pydantic V2, Pydantic Settings
- **Machine Learning:** Scikit-Learn, Random Forest, Isolation Forest, K-Means, StandardScaler, Joblib
- **Data Processing:** Pandas, NumPy
- **Database:** SQLite 3, SQLAlchemy 2.0 ORM
- **Frontend / Dashboard:** Streamlit, Plotly Express/Graph Objects, Custom CSS (Datadog/Grafana Dark NOC Theme)
- **Quality Assurance & Testing:** Pytest, HTTPX

---

## 6. System Architecture

```
                       INFRASTRUCTURE SIMULATOR
                 [10 Servers + 5 Network Appliances]
                                 │
                                 ▼
                     TELEMETRY INGESTION ENGINE
                   (Thread / Configurable Tick)
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
       RULE-BASED THRESHOLD               DATA PREPROCESSING
           ALERT ENGINE                   (Feature Pipeline)
        (Suppression/Dedupe)                     │
                 │                               ▼
                 │                    UNIFIED ML PREDICTION
                 │                   ┌─────────────────────────┐
                 │                   │  Random Forest (Class)  │
                 │                   │  Isolation Forest (Ano) │
                 │                   │  K-Means (Cluster)      │
                 │                   └───────────┬─────────────┘
                 │                               │
                 └───────────────┬───────────────┘
                                 ▼
                      DYNAMIC SEVERITY ENGINE
                     (Blast Radius & Correlation)
                                 │
                                 ▼
                    INCIDENT MANAGEMENT ENGINE
                   (Root Cause & Playbook Rules)
                                 │
                                 ▼
                      SQLITE DATABASE (8 Tables)
                                 │
                                 ▼
                         FASTAPI REST API
                         (Swagger /docs)
                                 │
                                 ▼
                    STREAMLIT NOC COMMAND CENTER
             [Overview | Live | Incidents | AI | Analytics | Nodes]
```

---

## 7. Project Folder Structure

```
noc-incident-intelligence/
│
├── backend/
│   ├── main.py                     # FastAPI application entrypoint & lifespan
│   ├── config.py                   # Pydantic Settings & environment config
│   ├── database.py                 # SQLAlchemy SQLite engine & session
│   ├── models.py                   # 8 ORM entity models
│   ├── schemas.py                  # Pydantic v2 validation models
│   ├── init_db.py                  # Seed & DB initialization script
│   ├── api/
│   │   ├── devices.py              # Device inventory & telemetry endpoints
│   │   ├── monitoring.py           # Snapshot & time-series endpoints
│   │   ├── alerts.py               # Alert listing & triage endpoints
│   │   ├── incidents.py            # Incident lifecycle endpoints
│   │   ├── ml.py                   # Model metrics & anomaly endpoints
│   │   ├── analytics.py            # MTTA, MTTR & failure distribution
│   │   └── simulation.py           # Simulator controls & fault triggers
│   ├── services/
│   │   ├── monitoring_service.py   # Background telemetry worker
│   │   ├── alert_service.py        # Threshold rule & deduplication engine
│   │   ├── incident_service.py     # Incident correlation & root cause
│   │   ├── recommendation_service.py # AI troubleshooting playbooks
│   │   └── prediction_service.py   # Wrapper for ML inference
│   └── utils/
│       ├── severity.py             # Hybrid severity scoring
│       └── logger.py               # Structured rotating system logger
│
├── ml/
│   ├── generate_dataset.py         # 12,000 synthetic sample generator
│   ├── preprocessing.py            # Feature extraction & validation
│   ├── train_classifier.py         # Supervised Random Forest training
│   ├── anomaly_detection.py        # Unsupervised Isolation Forest training
│   ├── clustering.py               # Unsupervised K-Means clustering
│   ├── prediction.py               # Unified multi-model inference service
│   ├── train_all.py                # Pipeline script to train all models
│   └── saved_models/               # Joblib models & metrics JSONs
│
├── simulator/
│   ├── infrastructure_simulator.py # Simulator coordinator (15 nodes)
│   ├── server_simulator.py         # Server node telemetry generator
│   ├── network_simulator.py        # Router/Switch/Firewall generator
│   └── event_generator.py          # Fault injection & modes
│
├── frontend/
│   ├── app.py                      # Streamlit dashboard landing
│   ├── api_client.py               # API communication client
│   ├── pages/
│   │   ├── 1_Overview.py           # NOC overview & KPI summary
│   │   ├── 2_Live_Monitoring.py    # High-frequency telemetry explorer
│   │   ├── 3_Incident_Management.py# Incident triage, AI playbooks
│   │   ├── 4_AI_Insights.py        # ML evaluation & confusion matrix
│   │   ├── 5_Analytics.py          # MTTA, MTTR & SLA trends
│   │   └── 6_Device_Management.py  # Inventory & node diagnostic inspector
│   └── components/
│       ├── styling.py              # Dark NOC theme & CSS badges
│       ├── metrics.py              # Top KPI cards
│       ├── charts.py               # Plotly time-series & heatmaps
│       ├── tables.py               # Formatted table helpers
│       └── simulation_controls.py  # Sidebar simulation panel
│
├── data/
│   ├── training_data.csv           # 12,000 labeled training dataset
│   └── noc_database.db             # Persistent SQLite database
│
├── tests/
│   ├── test_simulator.py           # Simulator & fault generation tests
│   ├── test_ml.py                  # ML dataset & model training tests
│   ├── test_api.py                 # REST API router tests
│   └── test_incidents.py           # E2E incident lifecycle tests
│
├── logs/
│   └── noc_system.log              # Structured rotating log file
│
├── requirements.txt                # Production Python dependencies
├── .env.example                    # Environment variable template
├── .gitignore                      # Git exclusion rules
├── run_backend.py                  # Backend standalone runner
├── run_frontend.py                 # Frontend standalone runner
├── run_system.py                   # Unified concurrent supervisor
└── README.md                       # Comprehensive system documentation
```

---

## 8. Machine Learning Methodology

### A. Supervised Classification (Random Forest)
- **Architecture:** `RandomForestClassifier(n_estimators=120, max_depth=16, random_state=42)`
- **Evaluation:** Evaluated on a 20% stratified holdout test split (2,400 samples).
- **Actual Evaluation Metrics:**
  - **Accuracy:** `100.00%`
  - **Weighted Precision:** `100.00%`
  - **Weighted Recall:** `100.00%`
  - **Weighted F1-Score:** `100.00%`
- **Top Feature Importances:**
  1. `dns_response_status` (21.7%)
  2. `network_latency` (19.8%)
  3. `cpu_utilization` (18.4%)
  4. `packet_loss` (14.2%)
  5. `memory_utilization` (12.1%)
  6. `disk_utilization` (7.6%)

### B. Anomaly Detection (Isolation Forest)
- **Architecture:** `IsolationForest(n_estimators=100, contamination=0.05, random_state=42)`
- **Training Set:** 3,600 baseline normal operations telemetry records.
- **Detection:** Decision scores `< 0.0` denote novel multi-metric degradation outside normal diurnal variance.

### C. Incident Clustering (K-Means)
- **Architecture:** `KMeans(n_clusters=4, random_state=42)` fitted on scaled feature vectors (`StandardScaler`).
- **Silhouette Score:** `0.4271`
- **Derived Cluster Centroid Profiles:**
  - **Cluster 0:** Standard Moderate Variance (Normal/Low impact)
  - **Cluster 1:** High Disk Saturation (`disk_utilization > 90%`)
  - **Cluster 2:** Computational Overload (`cpu > 88%`, `memory > 85%`)
  - **Cluster 3:** Network & Latency Degradation (`latency > 240ms`, `packet_loss > 8%`)

---

## 9. Dataset Description

- **Path:** `data/training_data.csv`
- **Total Records:** `12,000`
- **Features (11):**
  1. `cpu_utilization`: Core load (%)
  2. `memory_utilization`: RAM usage (%)
  3. `disk_utilization`: Storage consumption (%)
  4. `network_latency`: Round-trip time (ms)
  5. `packet_loss`: Dropped frame ratio (%)
  6. `bandwidth_utilization`: Saturated link capacity (%)
  7. `server_availability`: Node reachability indicator (1.0 or 0.0)
  8. `dns_response_status`: Recursive DNS resolution flag (1=Success, 0=Fail)
  9. `response_time`: Synthetic HTTP/RPC response latency (ms)
  10. `connection_status`: TCP link state (1=Connected, 0=Disconnected)
  11. `process_count`: Total active worker threads / PIDs
- **Target Label:** `incident_type` across 8 operational classes.

---

## 10. Database Schema (SQLite & SQLAlchemy)

The database `data/noc_database.db` contains 8 relational tables:

1. `devices`: Monitored fleet inventory (ID, hostname, type, IP, status, location, health).
2. `metric_history`: High-frequency timestamped telemetry records per device.
3. `alerts`: Threshold rule alerts with duplicate suppression and linkage to incidents.
4. `incidents`: Central incident record with ML confidence, root cause, severity, and playbooks.
5. `incident_history`: Complete audit trail tracking status transitions and operator notes.
6. `ml_predictions`: Historical inference log storing prediction, anomaly score, and cluster ID.
7. `simulation_events`: Audit log of synthetic fault triggers.
8. `model_performance`: Persisted ML evaluation metrics and confusion matrices.

---

## 11. API Documentation

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Subsystem health probe and monitoring status |
| `GET` | `/api/devices` | List all 15 devices with latest metric snapshots |
| `GET` | `/api/devices/{id}` | Single device metadata and status |
| `GET` | `/api/devices/{id}/metrics` | Historical time-series telemetry for a specific node |
| `GET` | `/api/monitoring/current` | Latest metric reading across all nodes |
| `GET` | `/api/monitoring/history` | Clustered telemetry history |
| `GET` | `/api/monitoring/summary` | Top-level cluster telemetry KPIs |
| `GET` | `/api/alerts` | Active and historical threshold alerts |
| `POST` | `/api/alerts/{id}/acknowledge` | Acknowledge an active alert |
| `POST` | `/api/alerts/{id}/resolve` | Resolve an alert |
| `GET` | `/api/incidents` | Filterable incident list (by status, severity, category) |
| `GET` | `/api/incidents/{id}` | Detailed incident dossier with history and recommendations |
| `POST` | `/api/incidents` | Manually register an operational incident |
| `PATCH` | `/api/incidents/{id}/status` | Transition lifecycle state (`ACKNOWLEDGED`, `INVESTIGATING`, `CLOSED`) |
| `POST` | `/api/incidents/{id}/resolve` | Resolve incident with root-cause documentation notes |
| `GET` | `/api/incidents/{id}/recommendations` | Retrieve tailored AI troubleshooting playbooks |
| `GET` | `/api/ml/performance` | Evaluation metrics for RF, Isolation Forest, and K-Means |
| `GET` | `/api/ml/predictions` | Unified model inference logs |
| `GET` | `/api/ml/anomalies` | Telemetry flagged as anomalous |
| `GET` | `/api/ml/clusters` | K-Means cluster profiles and centroids |
| `POST` | `/api/ml/train` | Trigger retraining of all ML models in background |
| `GET` | `/api/analytics/summary` | MTTA, MTTR, resolution rate, and problematic device ranking |
| `GET` | `/api/analytics/incident-trends`| Daily incident occurrence trends |
| `GET` | `/api/simulation/status` | Current simulation mode, active injections, and worker state |
| `POST` | `/api/simulation/start` | Start continuous telemetry ingestion |
| `POST` | `/api/simulation/stop` | Pause telemetry ingestion |
| `POST` | `/api/simulation/mode` | Set operational mode (`Normal`, `Warning`, `Critical`, `Random`) |
| `POST` | `/api/simulation/trigger-incident` | Inject synthetic fault into target device |

Interactive Swagger UI is available at: **`http://127.0.0.1:8000/docs`**

---

## 12. Installation Instructions

### Prerequisites
- Python 3.11 or Python 3.12
- Git

### Step-by-Step Setup
```bash
# 1. Clone repository
git clone <repository_url>
cd noc-incident-intelligence

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

---

## 13. Model Training Instructions

To train all three ML models (Random Forest, Isolation Forest, K-Means) and generate the synthetic dataset:

```bash
python -m ml.train_all
```

Trained models and evaluation metrics will be saved in `ml/saved_models/`.

---

## 14. Application Execution Instructions

### Option 1: Unified Launcher (Recommended)
Starts both the FastAPI backend and Streamlit dashboard in a single command with graceful shutdown:

```bash
python run_system.py
```

### Option 2: Running Services Individually

**Terminal 1 (Backend Gateway):**
```bash
python run_backend.py
# Or directly via uvicorn:
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

**Terminal 2 (Streamlit Dashboard):**
```bash
python run_frontend.py
# Or directly via streamlit:
streamlit run frontend/app.py --server.port 8501
```

---

## 15. Testing Instructions

Execute the automated test suite covering simulator, ML pipeline, REST API endpoints, and end-to-end incident workflows:

```bash
python -m pytest -v tests/
```

**Test Coverage Summary:**
- `tests/test_simulator.py`: 5 passed (Normal metrics, fault injection, network failure, modes, tick)
- `tests/test_ml.py`: 3 passed (Dataset generation, feature vector validation, multi-model training/inference)
- `tests/test_api.py`: 7 passed (Health check, device endpoints, monitoring summary, alert endpoints, incident lifecycle, analytics, simulation modes)
- `tests/test_incidents.py`: 2 passed (E2E Server Overload trigger/correlation/remediation flow, duplicate alert suppression)
- **Total: 17 passed in 7.29s**

---

## 16. Step-by-Step Demonstration Workflow

Follow this demonstration workflow to evaluate the complete end-to-end incident lifecycle:

1. **Launch the System:** Run `python run_system.py`. Open your browser to `http://localhost:8501`.
2. **Inspect Cluster Overview:** In **Overview (Page 1)**, observe 15 monitored nodes, active KPI cards, live CPU/Memory/Latency trends, and the healthy availability state.
3. **Examine Live Telemetry:** Navigate to **Live Monitoring (Page 2)**. Select `srv-app-01`. Notice CPU operating within normal baselines (< 50%) below the yellow warning (70%) and red critical (85%) reference lines.
4. **Trigger a Fault:** In the left sidebar **Simulation Engine**:
   - Set **Target Node** to `srv-app-01`.
   - Set **Fault Type** to `Server Overload`.
   - Click **💥 Trigger Incident**.
5. **Observe Telemetry Spike:** On **Live Monitoring**, observe CPU utilization surge above 88% and response times spike.
6. **Verify Automatic Alert & ML Classification:**
   - The rule engine fires an alert for CPU threshold breach.
   - The Random Forest classifier predicts `Server Overload` with >90% confidence.
   - The severity engine assigns `CRITICAL` or `HIGH` severity.
   - An incident is automatically created in SQLite.
7. **Triage the Incident:** Navigate to **Incident Management (Page 3)**:
   - Locate the new incident `CRITICAL - Server Overload on api-gateway-01.noc.corp`.
   - Click to inspect the Incident Dossier.
   - Inspect the **AI Root-Cause Hypothesis**.
   - Review the **AI Troubleshooting Playbook** (suggested top/htop process audit, thread pool inspection, horizontal load balancing).
8. **Acknowledge and Investigate:** Under **NOC Operator Actions**, transition status to `ACKNOWLEDGED`, enter notes "Investigating high worker process contention", and click **Apply Status Change**.
9. **Resolve the Incident:** Under **Resolve Incident & Document Fix**, enter resolution notes "Terminated runaway thread PID 4108 and recycled worker container", and click **Resolve Incident**.
10. **Verify SLA & MTTR Updates:** Navigate to **Analytics (Page 5)**. Observe the calculated MTTA and MTTR update dynamically from database timestamps, and verify the incident resolution rate reflects the resolution.

---

## 17. Limitations

- **Simulated Infrastructure:** The environment generates realistic synthetic metrics locally rather than connecting to live production hardware.
- **Local SQLite Engine:** SQLite is utilized for single-node deployment ease. For multi-thousand node production enterprise scale, PostgreSQL is recommended.

---

## 18. Future Improvements

- Integration with Prometheus and OpenTelemetry for live real-world agent metric ingestion.
- Webhook notifications to PagerDuty, Slack, and Microsoft Teams.
- Long Short-Term Memory (LSTM) or Temporal Convolutional Networks for multi-step ahead failure prediction.
- Automated Ansible/Terraform remediation playbooks for self-healing infrastructure.
