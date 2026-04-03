# Day 2 — Database Connection & Schema
Date: 15-03-2026 | Branch: day-2

## Objective
Connect Python to Neon PostgreSQL and create all database tables.

## What Was Done
- Created database connection script using SQLAlchemy
- Created SQL schema with 3 schemas: raw, warehouse, ml
- Created all tables: raw.flights, warehouse tables, ml.features
- Created auto-delete function for rolling 60-day window
- Verified connection to Neon PostgreSQL 17 Singapore

## Files Created
| File | Purpose |
|---|---|
| `ingestion/db_connection.py` | SQLAlchemy engine + connection test |
| `ingestion/schema.sql` | DDL for all schemas and tables |
| `ingestion/create_tables.py` | Executes schema.sql against Neon |

## Results
- ✅ All tables created in Neon
- ✅ Connection verified — PostgreSQL 17.8 Singapore

## Pending
- None