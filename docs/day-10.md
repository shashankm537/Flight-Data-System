# Day 10 — GitHub Actions CI/CD Pipeline
Date: 22-03-2026 | Branch: day-10

## Objective
Automate full pipeline to run twice daily without manual intervention.

## What Was Done
- Created GitHub Actions workflow file
- Pipeline runs ingestion → dbt → feature engineering → retrain → upload model
- Added 4 repository secrets: DATABASE_URL, DBT_HOST, DBT_USER, DBT_PASSWORD
- Fixed all deprecated Actions versions

## Files Created
| File | Purpose |
|---|---|
| `.github/workflows/pipeline.yml` | CI/CD workflow |

## Errors Fixed
| Error | Fix |
|---|---|
| upload-artifact@v3 deprecated | Updated to v4 |
| checkout@v3 deprecated | Updated to v4 |
| setup-python@v4 deprecated | Updated to v5 |
| distutils error in dbt on Ubuntu | Added pip install setuptools |
| pkg_resources error in mlflow | Upgraded to mlflow==2.16.0 |
| MLflow PermissionError /C: on Linux | Changed tracking URI to tempfile |

## Results
- ✅ Pipeline registered on GitHub Actions
- ✅ Runs at 6AM + 6PM IST daily
- ✅ Morning run successful

## Pending
- Evening run not verified same day