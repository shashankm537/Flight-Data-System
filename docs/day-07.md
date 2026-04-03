# Day 7 — Streamlit Dashboard
Date: 16-03-2026 | Branch: day-7

## Objective
Build user-facing dashboard showing flight delay insights.

## What Was Done
- Built 4-page Streamlit dashboard
- Overview page with KPI cards and charts
- Airline Analysis with delay rates
- Route Analysis with scatter plots
- Delay Predictor calling FastAPI

## Files Created
| File | Purpose |
|---|---|
| `dashboard/streamlit_app/app.py` | 4-page Streamlit dashboard |

## Errors Fixed
| Error | Fix |
|---|---|
| SQLAlchemy engine cannot be pickled by Streamlit cache | Removed @st.cache_data from get_engine() |

## Results
- ✅ Dashboard live at localhost:8501
- ✅ 96 flights, 17 delayed, 11.86 mins avg delay, 17.71% delay rate

## Pending
- None