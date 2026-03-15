import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def verify_data():
    """Verify data loaded correctly in Neon"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        
        # Total flights
        result = conn.execute(text("SELECT COUNT(*) FROM raw.flights"))
        total = result.fetchone()[0]
        print(f"Total flights in DB: {total}")
        
        # Domestic vs International
        result = conn.execute(text("""
            SELECT flight_type, COUNT(*) as count 
            FROM raw.flights 
            GROUP BY flight_type
        """))
        print("\nFlights by type:")
        for row in result:
            print(f"  {row[0]}: {row[1]}")
        
        # Top airlines
        result = conn.execute(text("""
            SELECT airline_name, COUNT(*) as count 
            FROM raw.flights 
            GROUP BY airline_name 
            ORDER BY count DESC 
            LIMIT 5
        """))
        print("\nTop 5 airlines:")
        for row in result:
            print(f"  {row[0]}: {row[1]}")
        
        # Flight status breakdown
        result = conn.execute(text("""
            SELECT flight_status, COUNT(*) as count 
            FROM raw.flights 
            GROUP BY flight_status 
            ORDER BY count DESC
        """))
        print("\nFlight status breakdown:")
        for row in result:
            print(f"  {row[0]}: {row[1]}")

        # Delayed flights
        result = conn.execute(text("""
            SELECT COUNT(*) FROM raw.flights 
            WHERE departure_delay > 15
        """))
        delayed = result.fetchone()[0]
        print(f"\nFlights delayed more than 15 mins: {delayed}")

        # Sample row
        result = conn.execute(text("""
            SELECT flight_number, airline_name, origin_airport, 
                   destination_airport, flight_type, flight_status
            FROM raw.flights 
            LIMIT 5
        """))
        print("\nSample flights:")
        for row in result:
            print(f"  {row[0]} | {row[1]} | {row[2]} -> {row[3]} | {row[4]} | {row[5]}")

if __name__ == "__main__":
    verify_data()