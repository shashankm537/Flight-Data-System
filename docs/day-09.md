# Day 9 — Switch to OpenSky API + Fix ML Pipeline
Date: 21-03-2026 | Branch: day-9

## Objective
Replace AviationStack (100 calls/month limit) with OpenSky (unlimited free).

## What Was Done
- Complete rewrite of ingestion using OpenSky bounding box
- Built realistic delay simulation engine with airline profiles
- Added unique constraint to prevent duplicate flights
- Fixed class imbalance with scale_pos_weight + threshold=0.3
- Updated FastAPI and ML training for new data structure

## Files Created/Modified
| File | Purpose |
|---|---|
| `ingestion/opensky_api.py` | OpenSky ingestion + delay simulation |
| `ml/train.py` | Updated for class imbalance |
| `api/main.py` | Updated encode_input() |

## Errors Fixed
| Error | Fix |
|---|---|
| AviationStack /flights/arrival requires paid auth | Switched to OpenSky /states/all |
| 260 duplicate flights | Added unique constraint + ON CONFLICT DO NOTHING |
| Target distribution all zeros | Added realistic delay simulation |
| Class imbalance F1=0 | Added scale_pos_weight + threshold=0.3 |

## Results
- ✅ 609 live flights loaded
- ✅ 72 delayed (11.8%)
- ✅ Model saved as {model, threshold, feature_cols}

## Pending
- None