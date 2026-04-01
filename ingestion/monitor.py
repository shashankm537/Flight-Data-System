"""
monitor.py
Data Quality Monitoring Script — checks pipeline health and data quality.
Run with: python ingestion/monitor.py
"""

import os
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def check_todays_ingestion():
    """Check if data was ingested today"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) FROM raw.flights
            WHERE flight_date = CURRENT_DATE
        """))
        count = result.scalar()
    status = "✅" if count > 0 else "❌"
    print(f"{status} Today's ingestion: {count} flights loaded for {date.today()}")
    return count > 0

def check_last_24h_ingestion():
    """Check flights loaded in last 24 hours"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) FROM raw.flights
            WHERE created_at >= NOW() - INTERVAL '24 hours'
        """))
        count = result.scalar()
    status = "✅" if count > 100 else "⚠️"
    print(f"{status} Last 24h ingestion: {count} flights (expected > 100)")
    return count > 100

def check_null_values():
    """Check for NULL values in critical columns"""
    critical_columns = [
        'flight_number', 'flight_date', 'airline_code',
        'origin_airport', 'destination_airport', 'flight_type'
    ]
    all_good = True
    with engine.connect() as conn:
        for col in critical_columns:
            result = conn.execute(text(f"""
                SELECT COUNT(*) FROM raw.flights
                WHERE {col} IS NULL
            """))
            null_count = result.scalar()
            status = "✅" if null_count == 0 else "❌"
            if null_count > 0:
                all_good = False
            print(f"{status} NULL check — {col}: {null_count} NULLs")
    return all_good

def check_delay_rate():
    """Check if delay rate is within expected range (10-40%)"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN is_delayed THEN 1 ELSE 0 END) as delayed,
                ROUND(100.0 * SUM(CASE WHEN is_delayed THEN 1 ELSE 0 END) / COUNT(*), 2) as delay_rate
            FROM warehouse_warehouse.fact_flights
        """))
        row = result.fetchone()
        total, delayed, delay_rate = row[0], row[1], float(row[2])
    
    status = "✅" if 10 <= delay_rate <= 40 else "⚠️"
    print(f"{status} Delay rate: {delay_rate}% (expected 10-40%) — {delayed}/{total} flights delayed")
    return 10 <= delay_rate <= 40

def check_data_freshness():
    """Check if warehouse data is up to date"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT MAX(flight_date) FROM warehouse_warehouse.fact_flights
        """))
        max_date = result.scalar()
    
    days_old = (date.today() - max_date).days if max_date else 999
    status = "✅" if days_old <= 1 else "⚠️"
    print(f"{status} Data freshness: latest data is {days_old} day(s) old (max date: {max_date})")
    return days_old <= 1

def check_ml_features():
    """Check if ML features table has data"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) FROM ml.features
        """))
        count = result.scalar()
    status = "✅" if count > 0 else "❌"
    print(f"{status} ML features: {count} rows in ml.features")
    return count > 0

def check_rolling_window():
    """Check if rolling 60-day window is working"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT MIN(flight_date), MAX(flight_date), COUNT(*)
            FROM raw.flights
        """))
        row = result.fetchone()
        min_date, max_date, total = row[0], row[1], row[2]
    
    if min_date and max_date:
        days_span = (max_date - min_date).days
        status = "✅" if days_span <= 61 else "⚠️"
        print(f"{status} Rolling window: {days_span} days of data ({min_date} to {max_date}), {total} total rows")
    else:
        print("❌ Rolling window: No data found")
    return True

def run_monitoring():
    """Run all monitoring checks"""
    print("="*60)
    print(f"FLIGHT DATA SYSTEM — HEALTH CHECK")
    print(f"Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    print("\n📥 INGESTION CHECKS")
    print("-"*40)
    check_todays_ingestion()
    check_last_24h_ingestion()

    print("\n🔍 DATA QUALITY CHECKS")
    print("-"*40)
    check_null_values()

    print("\n📊 WAREHOUSE CHECKS")
    print("-"*40)
    check_delay_rate()
    check_data_freshness()
    check_rolling_window()

    print("\n🤖 ML CHECKS")
    print("-"*40)
    check_ml_features()

    print("\n" + "="*60)
    print("Health check complete!")
    print("="*60)

if __name__ == "__main__":
    run_monitoring()