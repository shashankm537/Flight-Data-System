# Day 16 — More dbt Tests + New API Endpoints
Date: 23-03-2026 | Branch: day-16

## Objective
Expand dbt test coverage and add new API endpoints.

## What Was Done
- Expanded schema.yml from 14 to 27 dbt tests
- Added new columns to tests: airline_code, departure_hour, route, is_weekend, is_monsoon_season
- Added departure_hour column to stg_flights.sql
- Fixed global SQLAlchemy engine in api/main.py
- Added 3 new FastAPI endpoints: /flights, /airlines, /routes

## Files Modified
| File | Purpose |
|---|---|
| `transform/flight_transform/models/staging/schema.yml` | 14 → 27 tests |
| `transform/flight_transform/models/staging/stg_flights.sql` | Added departure_hour |
| `api/main.py` | Global engine + 3 new endpoints |

## Results
- ✅ 27/27 dbt tests passing
- ✅ /flights — recent flights with filters
- ✅ /airlines — 269 airlines with delay rates
- ✅ /routes — most delayed routes

## Pending
- None