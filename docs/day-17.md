# Day 17 — Streamlit Trends & Insights Page
Date: 31-03-2026 | Branch: day-17

## Objective
Add a Trends & Insights page to Streamlit dashboard.

## What Was Done
- Added Trends & Insights as 5th page in Streamlit
- Added is_monsoon_season to load_flight_data() SQL query
- Built 5 new charts: delay rate over time, time of day, day of week, monsoon analysis

## Files Modified
| File | Purpose |
|---|---|
| `dashboard/streamlit_app/app.py` | Added Trends & Insights page |

## Errors Fixed
| Error | Fix |
|---|---|
| KeyError: is_monsoon_season | Added is_monsoon_season to SELECT query |

## Results
- ✅ 5 pages in Streamlit dashboard
- ✅ All charts rendering correctly

## Pending
- None