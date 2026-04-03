# Day 3 — Live Flight Ingestion (AviationStack)
Date: 16-03-2026 | Branch: day-3

## Objective
Pull real flight data into the database using AviationStack API.

## What Was Done
- Built AviationStack API ingestion script
- Fetched domestic and international flights over India
- Created data verification script to confirm data loaded
- Parsed and cleaned flight data before inserting

## Files Created
| File | Purpose |
|---|---|
| `ingestion/aviation_api.py` | AviationStack API ingestion script |
| `ingestion/verify_data.py` | Data verification queries |

## Errors Fixed
| Error | Fix |
|---|---|
| InvalidDatetimeFormat — time field | Added parse_time() to extract HH:MM:SS from ISO datetime |

## Results
- ✅ 96 real flights loaded — 50 domestic, 46 international

## Pending
- None