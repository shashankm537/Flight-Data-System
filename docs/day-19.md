# Day 19 — Model Retraining + MLflow Fix
Date: 01-04-2026 | Branch: day-19

## Objective
Retrain XGBoost model with accumulated data and fix MLflow URI issue.

## What Was Done
- Fixed MLflow tracking URI — changed to "mlruns" relative path
- Retrained model with 18,778 rows (16 days of data)
- Tested threshold 0.4 — minimal improvement, reverted to 0.3
- Documented model performance limitations

## Files Modified
| File | Purpose |
|---|---|
| `ml/train.py` | Fixed MLflow tracking URI |

## Model Performance
| Metric | Value |
|---|---|
| Accuracy | 26.68% |
| F1 Score | 39.10% |
| Recall | 97.79% |
| AUC | 0.5634 |
| Training rows | 18,778 |

## Pending
- None