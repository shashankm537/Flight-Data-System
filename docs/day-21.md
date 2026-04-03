# Day 21 — Performance Optimization
Date: 01-04-2026 | Branch: day-21

## Objective
Add database indexes to speed up queries across all layers.

## What Was Done
- Created ingestion/create_indexes.py
- Created 13 indexes across raw, warehouse_warehouse and ml schemas

## Files Created
| File | Purpose |
|---|---|
| `ingestion/create_indexes.py` | Database index creation script |

## Indexes Created
| Index | Table | Column |
|---|---|---|
| idx_raw_flights_date | raw.flights | flight_date |
| idx_raw_flights_airline | raw.flights | airline_code |
| idx_raw_flights_created_at | raw.flights | created_at |
| idx_fact_flights_date | fact_flights | flight_date |
| idx_fact_flights_airline | fact_flights | airline_code |
| idx_fact_flights_is_delayed | fact_flights | is_delayed |
| idx_fact_flights_flight_type | fact_flights | flight_type |
| idx_fact_flights_origin | fact_flights | origin_airport |
| idx_fact_flights_destination | fact_flights | destination_airport |
| idx_fact_flights_time_of_day | fact_flights | time_of_day |
| idx_fact_flights_day_of_week | fact_flights | day_of_week |
| idx_ml_features_airline | ml.features | airline_code |
| idx_ml_features_is_delayed | ml.features | is_delayed |

## Results
- ✅ 13/13 indexes created successfully

## Pending
- None