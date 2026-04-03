# Day 5 — Feature Engineering & ML Model
Date: 16-03-2026 | Branch: day-5

## Objective
Engineer features and train XGBoost delay prediction model.

## What Was Done
- Built feature engineering script querying fact_flights
- Engineered 24 features including airline/airport/route encodings
- Trained XGBoost classifier with MLflow experiment tracking
- Saved model as dictionary with threshold and feature columns
- Handled class imbalance with scale_pos_weight

## Files Created
| File | Purpose |
|---|---|
| `transform/feature_engineering.py` | Feature engineering pipeline |
| `ml/train.py` | XGBoost training with MLflow |
| `ml/models/flight_delay_model.pkl` | Saved model dict |

## Errors Fixed
| Error | Fix |
|---|---|
| mlflow pkg_resources error | Upgraded mlflow to 2.16.0 |
| is_weekend boolean vs integer | Changed .astype(int) |

## Results
- ✅ Model trained — Accuracy 94.74%, AUC 97.92% (on AviationStack data)
- ✅ Model saved as {model, threshold, feature_cols}

## Pending
- None