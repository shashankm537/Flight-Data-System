"""
create_indexes.py
Creates database indexes for performance optimization.
Run with: python ingestion/create_indexes.py
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def create_indexes():
    """Create indexes on frequently queried columns"""
    
    indexes = [
        # raw.flights indexes
        {
            "name": "idx_raw_flights_date",
            "sql": "CREATE INDEX IF NOT EXISTS idx_raw_flights_date ON raw.flights(flight_date)",
            "description": "Index on flight_date for date range queries"
        },
        {
            "name": "idx_raw_flights_airline",
            "sql": "CREATE INDEX IF NOT EXISTS idx_raw_flights_airline ON raw.flights(airline_code)",
            "description": "Index on airline_code for airline filtering"
        },
        {
            "name": "idx_raw_flights_created_at",
            "sql": "CREATE INDEX IF NOT EXISTS idx_raw_flights_created_at ON raw.flights(created_at)",
            "description": "Index on created_at for recent data queries"
        },

        # warehouse_warehouse.fact_flights indexes
        {
            "name": "idx_fact_flights_date",
            "sql": "CREATE INDEX IF NOT EXISTS idx_fact_flights_date ON warehouse_warehouse.fact_flights(flight_date)",
            "description": "Index on flight_date for warehouse date queries"
        },
        {
            "name": "idx_fact_flights_airline",
            "sql": "CREATE INDEX IF NOT EXISTS idx_fact_flights_airline ON warehouse_warehouse.fact_flights(airline_code)",
            "description": "Index on airline_code for airline analysis"
        },
        {
            "name": "idx_fact_flights_is_delayed",
            "sql": "CREATE INDEX IF NOT EXISTS idx_fact_flights_is_delayed ON warehouse_warehouse.fact_flights(is_delayed)",
            "description": "Index on is_delayed for delay filtering"
        },
        {
            "name": "idx_fact_flights_flight_type",
            "sql": "CREATE INDEX IF NOT EXISTS idx_fact_flights_flight_type ON warehouse_warehouse.fact_flights(flight_type)",
            "description": "Index on flight_type for domestic/international filtering"
        },
        {
            "name": "idx_fact_flights_origin",
            "sql": "CREATE INDEX IF NOT EXISTS idx_fact_flights_origin ON warehouse_warehouse.fact_flights(origin_airport)",
            "description": "Index on origin_airport for route analysis"
        },
        {
            "name": "idx_fact_flights_destination",
            "sql": "CREATE INDEX IF NOT EXISTS idx_fact_flights_destination ON warehouse_warehouse.fact_flights(destination_airport)",
            "description": "Index on destination_airport for route analysis"
        },
        {
            "name": "idx_fact_flights_time_of_day",
            "sql": "CREATE INDEX IF NOT EXISTS idx_fact_flights_time_of_day ON warehouse_warehouse.fact_flights(time_of_day)",
            "description": "Index on time_of_day for time analysis"
        },
        {
            "name": "idx_fact_flights_day_of_week",
            "sql": "CREATE INDEX IF NOT EXISTS idx_fact_flights_day_of_week ON warehouse_warehouse.fact_flights(day_of_week)",
            "description": "Index on day_of_week for weekly patterns"
        },

        # ml.features indexes
        {
            "name": "idx_ml_features_airline",
            "sql": "CREATE INDEX IF NOT EXISTS idx_ml_features_airline ON ml.features(airline_code)",
            "description": "Index on airline_code in ml.features"
        },
        {
            "name": "idx_ml_features_is_delayed",
            "sql": "CREATE INDEX IF NOT EXISTS idx_ml_features_is_delayed ON ml.features(is_delayed)",
            "description": "Index on is_delayed in ml.features"
        },
    ]

    print("="*60)
    print("CREATING DATABASE INDEXES")
    print("="*60)

    success_count = 0
    fail_count = 0

    with engine.connect() as conn:
        for idx in indexes:
            try:
                conn.execute(text(idx["sql"]))
                conn.commit()
                print(f"✅ Created: {idx['name']} — {idx['description']}")
                success_count += 1
            except Exception as e:
                print(f"❌ Failed: {idx['name']} — {str(e)}")
                fail_count += 1

    print("\n" + "="*60)
    print(f"Done! {success_count} indexes created, {fail_count} failed")
    print("="*60)

if __name__ == "__main__":
    create_indexes()