# Flight Delay Intelligence Platform — Project Summary

## Project Overview
An end-to-end data platform that ingests live flight data, transforms it with dbt, trains an ML model to predict delays, and serves insights through multiple live dashboards — fully automated with zero manual intervention.

**Developer:** Shashank M S — Data Engineer @ Accenture | CS Graduate — BMSCE  
**GitHub:** https://github.com/shashankm537/Flight-Data-System  
**Duration:** 30 days (March 2026 — April 2026)

---

## Live URLs
| Service | URL |
|---|---|
| Streamlit Dashboard | https://flight-data-system.streamlit.app |
| FastAPI REST API | https://flight-data-system-q1an.onrender.com |
| API Swagger Docs | https://flight-data-system-q1an.onrender.com/docs |
| Metabase — Flight Data Analytics | https://metabase-production-04c3.up.railway.app/public/dashboard/8b35977b-89c0-4b1d-a935-5a951d6bf9b1 |
| Metabase — Time of Day Analysis | https://metabase-production-04c3.up.railway.app/public/dashboard/130fe479-777e-444b-bb98-4fa2b688d6db |
| Metabase — Route Performance | https://metabase-production-04c3.up.railway.app/public/dashboard/3d3d6e9d-ae87-470c-bedf-cf12cb9e070a |

---

## Architecture
```
OpenSky Network API (free, unlimited)
        │
        ▼
Python Ingestion Script
- Bounding box: India + Middle East + SE Asia
- Realistic delay simulation
- Unique constraint — no duplicates
- Rolling 60-day auto-delete
        │
        ▼
Neon PostgreSQL 17 (Singapore)
- raw.flights — staging table
- warehouse_warehouse.fact_flights — enriched fact table
- ml.features — engineered features
        │
        ▼
dbt Transformations (flight_transform)
- staging → warehouse → mart
- 27 data quality tests
- fact_flights enriched with delay_category, time_of_day, is_monsoon_season
        │
        ▼
Feature Engineering + XGBoost ML
- 24 engineered features
- scale_pos_weight for class imbalance
- threshold=0.3 for better recall
- MLflow experiment tracking
        │
        ├─────────────────────┐─────────────────────┐
        ▼                     ▼                     ▼
FastAPI (Render)      Streamlit (Cloud)      Metabase (Railway)
7 endpoints           5 pages                3 dashboards
/predict              Overview               Flight Data Analytics
/stats                Airline Analysis       Time of Day Analysis
/flights              Route Analysis         Route Performance
/airlines             Trends & Insights
/routes               Delay Predictor
        │
        ▼
GitHub Actions CI/CD
- Runs 2x daily (6AM + 6PM IST)
- Full pipeline: ingest → dbt → features → retrain → health check
- 37+ successful runs, 0 failures
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Language | Python 3.12.3 | Core development |
| Database | Neon PostgreSQL 17 | Cloud database |
| Ingestion | OpenSky Network API | Live flight data |
| Transformation | dbt-postgres 1.7.4 | Data modeling |
| ML | XGBoost 2.0.3 | Delay prediction |
| Experiment Tracking | MLflow 2.16.0 | Model versioning |
| API | FastAPI 0.109.2 | REST endpoints |
| Dashboard | Streamlit 1.31.1 | Data app |
| BI Tool | Metabase | Business intelligence |
| Containerization | Docker + Compose | Local deployment |
| Orchestration | Airflow 2.8.0 | DAG orchestration |
| CI/CD | GitHub Actions | Automation |
| API Hosting | Render.com | FastAPI deployment |
| Dashboard Hosting | Streamlit Cloud | Streamlit deployment |
| BI Hosting | Railway.io | Metabase deployment |
| Testing | pytest (43 tests) | Quality assurance |
| Monitoring | Custom monitor.py | Health checks |
| Indexing | PostgreSQL indexes | Performance |

---

## Key Metrics (as of April 2026)

| Metric | Value |
|---|---|
| Total flights in DB | 20,000+ |
| Days of data | 17+ days |
| Pipeline runs | 40+ (100% success) |
| dbt tests passing | 27/27 |
| pytest tests passing | 43/43 |
| Database indexes | 13 |
| Unique routes | 20+ real IATA routes |
| Delay rate | ~24% |
| Model AUC | 0.65 |
| Model recall | 97.79% |
| API endpoints | 7 |
| Streamlit pages | 5 |
| Metabase dashboards | 3 |
| Metabase charts | 12 |

---

## Day by Day Progress

| Day | Work Done |
|---|---|
| Day 1 | Environment setup, project structure |
| Day 2 | Database connection, schema creation |
| Day 3 | AviationStack API ingestion |
| Day 4 | dbt transformations, 14 tests |
| Day 5 | Feature engineering, XGBoost model |
| Day 6 | FastAPI 4 endpoints |
| Day 7 | Streamlit dashboard 4 pages |
| Day 8 | Docker containerization |
| Day 9 | Switch to OpenSky API, delay simulation |
| Day 10 | GitHub Actions CI/CD |
| Day 11 | Render deployment attempt |
| Day 12 | Fix Render deployment, Streamlit Cloud |
| Day 13 | pytest 43 tests, Airflow DAGs, README |
| Day 14 | Metabase setup, Railway deployment |
| Day 15 | Airflow Docker, pytest in CI/CD |
| Day 16 | 27 dbt tests, 3 new API endpoints |
| Day 17 | Streamlit Trends & Insights page |
| Day 18 | 2 new Metabase dashboards |
| Day 19 | Model retrain with 18,778 rows |
| Day 20 | Data quality monitoring script |
| Day 21 | 13 database indexes |
| Day 22 | Health check in CI/CD pipeline |
| Day 23 | Project summary documentation |

---

## Roles Showcased

| Role | Evidence |
|---|---|
| **Data Engineer** | Ingestion pipeline, dbt, CI/CD, Docker, PostgreSQL, indexing |
| **Data Scientist** | XGBoost, MLflow, feature engineering, class imbalance handling |
| **Data Analyst** | Metabase dashboards, Streamlit charts, delay insights |
| **Backend Engineer** | FastAPI 7 endpoints, Swagger docs, Render deployment |
| **DevOps** | GitHub Actions, Docker Compose, Airflow DAGs, monitoring |

---

## Known Limitations

1. **Simulated delay data** — OpenSky doesn't provide real delays, so model AUC is ~0.56
2. **Render cold starts** — FastAPI on Render free tier spins down after inactivity
3. **Metabase local only** — Dashboard data is live but Metabase itself runs on Railway free tier

---

## Interview Talking Points

**"Tell me about a data project you built"**
- End-to-end platform: ingestion → transformation → ML → API → dashboard
- Fully automated: 37+ pipeline runs with zero failures
- Multi-role: showcases DE, DS, DA, and DevOps skills in one project

**"What challenges did you face?"**
- OpenSky API has no delay data → built realistic delay simulation
- Python 3.14 on Render → pinned pyarrow and set PYTHON_VERSION
- MLflow Windows path issue → changed tracking URI to relative path
- Class imbalance → scale_pos_weight + threshold=0.3

**"How did you handle data quality?"**
- 27 dbt tests on every pipeline run
- 43 pytest tests for API and features
- Custom monitor.py health check after every ingestion
- Unique constraints prevent duplicate data

**"How does the pipeline work?"**
- GitHub Actions triggers at 6AM and 6PM IST
- OpenSky API → raw.flights → dbt → fact_flights → feature engineering → XGBoost → FastAPI → Streamlit
- Fully automated, zero manual intervention