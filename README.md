# ✈️ Flight Delay Intelligence Platform

> An end-to-end data platform that ingests live flight data, transforms it with dbt, trains an ML model to predict delays, and serves insights through a live dashboard — fully automated with zero manual intervention.

[![Python](https://img.shields.io/badge/Python-3.12.3-blue?logo=python)](https://python.org)
[![dbt](https://img.shields.io/badge/dbt-1.7.4-orange?logo=dbt)](https://getdbt.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.2-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31.1-red?logo=streamlit)](https://streamlit.io)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0.3-blue)](https://xgboost.readthedocs.io)
[![MLflow](https://img.shields.io/badge/MLflow-2.16.0-purple?logo=mlflow)](https://mlflow.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue?logo=postgresql)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)](https://docker.com)

## 🔴 Live Demo

| Service | URL |
|---|---|
| 📊 **Streamlit Dashboard** | [flight-data-system.streamlit.app](https://flight-data-system.streamlit.app) |
| ⚡ **FastAPI REST API** | [flight-data-system-q1an.onrender.com](https://flight-data-system-q1an.onrender.com) |
| 📖 **API Docs (Swagger)** | [flight-data-system-q1an.onrender.com/docs](https://flight-data-system-q1an.onrender.com/docs) |
| 📈 **Metabase — Flight Data Analytics** | [Public Dashboard 1](https://metabase-production-04c3.up.railway.app/public/dashboard/8b35977b-89c0-4b1d-a935-5a951d6bf9b1) |
| 🕐 **Metabase — Time of Day Analysis** | [Public Dashboard 2](https://metabase-production-04c3.up.railway.app/public/dashboard/130fe479-777e-444b-bb98-4fa2b688d6db) |
| 🗺️ **Metabase — Route Performance** | [Public Dashboard 3](https://metabase-production-04c3.up.railway.app/public/dashboard/3d3d6e9d-ae87-470c-bedf-cf12cb9e070a) |

---

## 🏗️ Architecture
```
OpenSky Network API
        │
        ▼
┌─────────────────┐
│   Ingestion     │  opensky_api.py — fetches live flights over India
│   (Python)      │  delay simulation, unique constraint, 60-day rolling window
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Neon PostgreSQL│  3 schemas: raw → warehouse → ml
│  (raw.flights)  │  Singapore region, free 3GB tier
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  dbt Transform  │  3 layers: staging → warehouse → mart
│  (flight_       │  27 data quality tests, fact table enrichment
│   transform)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Feature Engineer │  24 features — airline/airport/route encodings,
│ + XGBoost ML    │  time-of-day, delay profiles, class imbalance handling
└────────┬────────┘
         │
         ├──────────────────────┐
         ▼                      ▼
┌─────────────────┐    ┌─────────────────┐
│    FastAPI      │    │    Streamlit    │
│  /predict       │    │   Dashboard     │
│  /stats         │    │   5 pages       │
│  /flights       │    │   Plotly charts │
│  /airlines      │    └─────────────────┘
│  /routes        │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ GitHub Actions  │  Runs full pipeline 2x daily
│ CI/CD           │  6AM IST + 6PM IST automatically
└─────────────────┘
```

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.12.3 |
| **Database** | Neon.tech PostgreSQL 17 (Singapore) |
| **Ingestion** | OpenSky Network API (free, unlimited) |
| **Transformation** | dbt-postgres 1.7.4 |
| **ML Model** | XGBoost 2.0.3 + scikit-learn 1.4.0 |
| **Experiment Tracking** | MLflow 2.16.0 |
| **API** | FastAPI 0.109.2 + uvicorn 0.27.1 |
| **Dashboard** | Streamlit 1.31.1 + Plotly 5.19.0 |
| **BI Tool** | Metabase (Railway.io) |
| **Containerization** | Docker + Docker Compose |
| **CI/CD** | GitHub Actions |
| **API Deployment** | Render.com |
| **Dashboard Deployment** | Streamlit Community Cloud |

---

## 🗂️ Project Structure
```
Flight-Data-System/
├── .github/workflows/
│   └── pipeline.yml          # GitHub Actions — runs 2x daily
├── ingestion/
│   ├── opensky_api.py        # Live flight ingestion + delay simulation
│   ├── db_connection.py      # SQLAlchemy + Neon connection
│   └── schema.sql            # DDL for all tables
├── transform/
│   ├── feature_engineering.py
│   └── dbt_project/          # flight_transform — staging/warehouse/mart
├── ml/
│   ├── train.py              # XGBoost + MLflow training
│   └── models/
│       └── flight_delay_model.pkl
├── api/
│   ├── main.py               # FastAPI 7 endpoints
│   └── Dockerfile
├── dashboard/
│   ├── streamlit_app/
│   │   └── app.py            # 5-page Streamlit dashboard
│   └── Dockerfile
├── orchestration/
│   └── dags/                 # Airflow DAGs
├── tests/                    # pytest tests — 43 passing
├── docker-compose.yml
└── requirements.txt
```

---

## 🚀 Key Features

- **Live data ingestion** — OpenSky Network API, bounding box covers India + Middle East + SE Asia
- **Realistic delay simulation** — airline profiles (IndiGo 18%, SpiceJet 35%), time-of-day factors, weekend factor
- **Rolling 60-day window** — auto-deletes old data, keeps storage lean forever
- **dbt transformations** — 3-layer architecture with 27 passing data quality tests
- **XGBoost delay predictor** — handles class imbalance with scale_pos_weight + threshold=0.3
- **FastAPI REST API** — 7 endpoints including /flights, /airlines, /routes
- **Streamlit dashboard** — 5 pages: Overview, Airline Analysis, Route Analysis, Trends & Insights, Delay Predictor
- **Metabase BI dashboards** — 3 public dashboards, 12 charts total, no login required
- **Fully automated** — GitHub Actions pipeline runs twice daily

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Root — API info |
| GET | `/health` | Health check + model status |
| POST | `/predict` | Predict flight delay probability |
| GET | `/stats` | Live flight statistics from warehouse |
| GET | `/flights` | Recent flights with optional filters |
| GET | `/airlines` | Airline performance summary |
| GET | `/routes` | Most delayed routes |

---

## 📊 Metabase Public Dashboards

| Dashboard | Charts | Public Link |
|---|---|---|
| **Flight Data Analytics** | 4 charts — airline counts, delay rates, domestic vs international | [View Dashboard](https://metabase-production-04c3.up.railway.app/public/dashboard/8b35977b-89c0-4b1d-a935-5a951d6bf9b1) |
| **Time of Day Analysis** | 4 charts — time of day and day of week patterns | [View Dashboard](https://metabase-production-04c3.up.railway.app/public/dashboard/130fe479-777e-444b-bb98-4fa2b688d6db) |
| **Route Performance** | 4 charts — route analysis, origin/destination airports | [View Dashboard](https://metabase-production-04c3.up.railway.app/public/dashboard/3d3d6e9d-ae87-470c-bedf-cf12cb9e070a) |

---

## ⚙️ Local Setup

### Prerequisites
- Python 3.12.3
- Docker Desktop
- Neon.tech account (free)

### 1. Clone the repo
```bash
git clone https://github.com/shashankm537/Flight-Data-System.git
cd Flight-Data-System
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
Create a `.env` file in the root:
```
DATABASE_URL=your_neon_database_url
RETENTION_DAYS=60
ENVIRONMENT=development
```

### 5. Create database tables
```bash
python ingestion/create_tables.py
```

### 6. Run ingestion
```bash
python ingestion/opensky_api.py
```

### 7. Run dbt transformations
```bash
cd transform/flight_transform
dbt run
dbt test
```

### 8. Train model
```bash
python ml/train.py
```

### 9. Start services
```bash
# Option A — Docker Compose (includes Metabase at localhost:3000)
docker-compose up

# Option B — locally
uvicorn api.main:app --host 0.0.0.0 --port 8000
streamlit run dashboard/streamlit_app/app.py
```

---

## 🤖 ML Model Details

| Parameter | Value |
|---|---|
| Algorithm | XGBoost Classifier |
| Imbalance handling | scale_pos_weight (~7.4) |
| Prediction threshold | 0.3 (optimized for recall) |
| Features | 24 engineered features |
| Tracking | MLflow experiment logging |
| Retraining | Automatic — 2x daily via GitHub Actions |

---

## 🔄 Automated Pipeline

GitHub Actions workflow runs automatically:
- **6:00 AM IST** (00:30 UTC)
- **6:00 PM IST** (12:30 UTC)

Pipeline steps: `Ingest` → `dbt run + test` → `Feature Engineering` → `Retrain Model` → `Upload Artifact`

---

## 👤 Built By

**Shashank M S**
Data Engineer @ Accenture | CS Graduate — BMSCE

[![GitHub](https://img.shields.io/badge/GitHub-shashankm537-black?logo=github)](https://github.com/shashankm537)

---

## 📄 License

MIT License