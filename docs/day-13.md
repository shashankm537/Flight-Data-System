# Day 13 — pytest Tests, Airflow DAGs, README
Date: 22-03-2026 | Branch: day-13

## Objective
Write pytest tests, create Airflow DAG files and add professional README.

## What Was Done
- Written 43 pytest tests across 3 test files — all passing
- Created 3 Airflow DAG files in orchestration/dags/
- Added conftest.py and __init__.py for pytest configuration
- Added httpx==0.27.0 to requirements.txt
- Written complete README.md with live URLs and architecture diagram

## Files Created
| File | Purpose |
|---|---|
| `tests/test_loader.py` | 5 tests — DB connection |
| `tests/test_api.py` | 15 tests — FastAPI endpoints |
| `tests/test_features.py` | 23 tests — encode_input, model logic |
| `tests/conftest.py` | pytest path configuration |
| `tests/__init__.py` | pytest package init |
| `orchestration/dags/daily_ingest.py` | Airflow DAG — ingestion |
| `orchestration/dags/dbt_transform.py` | Airflow DAG — dbt |
| `orchestration/dags/retrain_model.py` | Airflow DAG — retraining |
| `README.md` | Complete README with live URLs |

## Errors Fixed
| Error | Fix |
|---|---|
| ModuleNotFoundError: httpx | pip install httpx==0.27.0 |
| TypeError: Client.__init__() unexpected keyword | Downgraded to httpx==0.27.0 |

## Results
- ✅ 43/43 tests passing
- ✅ 3 Airflow DAG files written
- ✅ README live on GitHub

## Pending
- None