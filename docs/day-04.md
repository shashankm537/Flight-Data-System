# Day 4 — dbt Transformations & Data Quality Tests
Date: 16-03-2026 | Branch: day-4

## Objective
Set up dbt and build transformation models with data quality tests.

## What Was Done
- Initialized dbt project: flight_transform
- Built 3 model layers: staging → warehouse → mart
- Written 14 data quality tests
- Configured dbt profiles.yml for Neon connection
- Fixed Python 3.12 distutils compatibility issue

## Files Created
| File | Purpose |
|---|---|
| `transform/flight_transform/models/staging/stg_flights.sql` | Staging view |
| `transform/flight_transform/models/warehouse/fact_flights.sql` | Fact table |
| `transform/flight_transform/models/mart/flight_insights.sql` | Aggregated mart |
| `transform/flight_transform/models/staging/schema.yml` | 14 data quality tests |
| `transform/flight_transform/dbt_project.yml` | dbt configuration |

## Errors Fixed
| Error | Fix |
|---|---|
| distutils missing Python 3.12 | pip install setuptools |
| dbt profiles.yml path issue on Windows | Created at C:\Users\My PC\.dbt\profiles.yml |

## Results
- ✅ PASS=3 dbt run
- ✅ PASS=14 dbt test

## Pending
- None