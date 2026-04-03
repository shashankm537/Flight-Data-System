# Day 24 — Fix MLflow, Real Airport Codes, Data Reset
Date: 02-04-2026 | Branch: day-24

## Objective
Fix GitHub Actions MLflow error, implement real airport codes and reset data.

## What Was Done
- Fixed MLflow — removed mlflow.xgboost.log_model() causing /C: permission error
- Added AIRPORT_COORDS dictionary with 28 airports
- Added get_nearest_airport() — maps lat/lon to nearest IATA code
- Replaced IND/INTL and UNK with real airport codes
- Cleared all existing data and re-ingested fresh
- Retrained model with fresh data

## Files Modified
| File | Purpose |
|---|---|
| `ml/train.py` | Fixed MLflow URI, removed log_model |
| `ingestion/opensky_api.py` | Added AIRPORT_COORDS, real route estimation |

## Before vs After
| Metric | Before | After |
|---|---|---|
| Routes | 2 (IND-UNK, INTL-UNK) | 20+ real IATA routes |
| Model AUC | 0.5634 | 0.6502 |

## Pending
- None