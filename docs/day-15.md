# Day 15 — Airflow Docker Setup + pytest in CI/CD
Date: 23-03-2026 | Branch: day-15

## Objective
Run Airflow locally via Docker and add pytest to GitHub Actions pipeline.

## What Was Done
- Added pytest step to GitHub Actions pipeline.yml
- Downloaded official Airflow 2.8.0 Docker image
- Created airflow/dags/, airflow/logs/, airflow/plugins/ directories
- Copied DAGs to airflow/dags/ for Airflow to pick up
- Started Airflow standalone container at localhost:8080
- Verified all 3 DAGs loaded with correct schedules and tags

## Files Modified
| File | Purpose |
|---|---|
| `.github/workflows/pipeline.yml` | Added pytest step |
| `orchestration/dags/daily_ingest.py` | Airflow DAG — ingestion |
| `orchestration/dags/dbt_transform.py` | Airflow DAG — dbt |
| `orchestration/dags/retrain_model.py` | Airflow DAG — retraining |
| `airflow-docker-compose.yaml` | Official Airflow docker-compose |

## Results
- ✅ All 3 DAGs visible in Airflow UI at localhost:8080
- ✅ Correct schedules and tags confirmed
- ✅ pytest added to GitHub Actions pipeline

## Pending
- None