# Day 6 — FastAPI Prediction Endpoint
Date: 17-03-2026 | Branch: day-6

## Objective
Build REST API to serve the trained model predictions.

## What Was Done
- Built FastAPI app with 4 endpoints
- Implemented encode_input() for feature encoding
- Added Pydantic request/response schemas
- Tested all endpoints via Swagger UI

## Files Created
| File | Purpose |
|---|---|
| `api/main.py` | FastAPI app with 4 endpoints |

## API Endpoints
| Method | Endpoint | Description |
|---|---|---|
| GET | / | Root — API info |
| GET | /health | Health check + model status |
| POST | /predict | Predict flight delay |
| GET | /stats | Flight statistics |

## Results
- ✅ API live at localhost:8000
- ✅ Tested via Swagger UI — BOM-DEL delay probability 0.53%

## Pending
- None