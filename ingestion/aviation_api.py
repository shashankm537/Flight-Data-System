import os
import requests
import pandas as pd
from datetime import datetime, date
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AVIATION_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Top 20 busiest Indian routes - domestic + international
ROUTES = [
    # Domestic
    {"dep": "BOM", "arr": "DEL"},  # Mumbai - Delhi
    {"dep": "DEL", "arr": "BOM"},  # Delhi - Mumbai
    {"dep": "BOM", "arr": "BLR"},  # Mumbai - Bangalore
    {"dep": "DEL", "arr": "BLR"},  # Delhi - Bangalore
    {"dep": "BOM", "arr": "CCU"},  # Mumbai - Kolkata
    {"dep": "DEL", "arr": "MAA"},  # Delhi - Chennai
    {"dep": "BLR", "arr": "HYD"},  # Bangalore - Hyderabad
    {"dep": "DEL", "arr": "CCU"},  # Delhi - Kolkata
    {"dep": "BOM", "arr": "GOI"},  # Mumbai - Goa
    {"dep": "DEL", "arr": "AMD"},  # Delhi - Ahmedabad
    # International
    {"dep": "BOM", "arr": "DXB"},  # Mumbai - Dubai
    {"dep": "DEL", "arr": "DXB"},  # Delhi - Dubai
    {"dep": "BLR", "arr": "SIN"},  # Bangalore - Singapore
    {"dep": "DEL", "arr": "LHR"},  # Delhi - London
    {"dep": "BOM", "arr": "LHR"},  # Mumbai - London
    {"dep": "DEL", "arr": "JFK"},  # Delhi - New York
    {"dep": "BOM", "arr": "SIN"},  # Mumbai - Singapore
    {"dep": "DEL", "arr": "BKK"},  # Delhi - Bangkok
    {"dep": "BOM", "arr": "KUL"},  # Mumbai - Kuala Lumpur
    {"dep": "DEL", "arr": "CDG"},  # Delhi - Paris
]

# Airports outside India for international classification
INTERNATIONAL_AIRPORTS = [
    "DXB", "SIN", "LHR", "JFK", "BKK", "KUL", "CDG"
]

def get_flight_type(origin, destination):
    """Determine if flight is domestic or international"""
    if origin in INTERNATIONAL_AIRPORTS or destination in INTERNATIONAL_AIRPORTS:
        return "international"
    return "domestic"

def parse_time(dt_str):
    """Extract just the time from a datetime string"""
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str).strftime("%H:%M:%S")
    except:
        return None

def fetch_flights_for_route(dep_iata, arr_iata):
    """Fetch flights for a specific route from AviationStack"""
    url = "http://api.aviationstack.com/v1/flights"
    params = {
        "access_key": API_KEY,
        "dep_iata": dep_iata,
        "arr_iata": arr_iata,
        "limit": 5
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "data" not in data:
            print(f"No data for route {dep_iata}-{arr_iata}")
            return []

        return data["data"]

    except Exception as e:
        print(f"Error fetching {dep_iata}-{arr_iata}: {e}")
        return []

def parse_flight(flight, flight_type):
    """Parse raw API response into clean dictionary"""
    try:
        dep = flight.get("departure", {})
        arr = flight.get("arrival", {})
        airline = flight.get("airline", {})
        flt = flight.get("flight", {})

        # Parse departure times
        sched_dep = dep.get("scheduled")
        actual_dep = dep.get("actual")
        sched_arr = arr.get("scheduled")
        actual_arr = arr.get("actual")

        # Calculate delays in minutes
        dep_delay = dep.get("delay") or 0
        arr_delay = arr.get("delay") or 0

        return {
            "flight_date": date.today(),
            "flight_number": flt.get("iata", ""),
            "airline_code": airline.get("iata", ""),
            "airline_name": airline.get("name", ""),
            "origin_airport": dep.get("iata", ""),
            "origin_city": dep.get("airport", ""),
            "origin_country": "India" if dep.get("iata") not in INTERNATIONAL_AIRPORTS else "International",
            "destination_airport": arr.get("iata", ""),
            "destination_city": arr.get("airport", ""),
            "destination_country": "India" if arr.get("iata") not in INTERNATIONAL_AIRPORTS else "International",
            "flight_type": flight_type,
            "scheduled_departure": parse_time(sched_dep),
            "actual_departure": parse_time(actual_dep),
            "scheduled_arrival": parse_time(sched_arr),
            "actual_arrival": parse_time(actual_arr),
            "departure_delay": int(dep_delay),
            "arrival_delay": int(arr_delay),
            "delay_reason": None,
            "flight_status": flight.get("flight_status", "")
        }

    except Exception as e:
        print(f"Error parsing flight: {e}")
        return None

def delete_old_flights(connection):
    """Delete flights older than 60 days"""
    connection.execute(text(
        "DELETE FROM raw.flights WHERE flight_date < CURRENT_DATE - INTERVAL '60 days'"
    ))
    print("Old flights deleted — rolling 60-day window maintained")

def load_flights_to_db(flights):
    """Load parsed flights into raw.flights table"""
    if not flights:
        print("No flights to load")
        return 0

    engine = create_engine(DATABASE_URL)

    insert_sql = text("""
        INSERT INTO raw.flights (
            flight_date, flight_number, airline_code, airline_name,
            origin_airport, origin_city, origin_country,
            destination_airport, destination_city, destination_country,
            flight_type, scheduled_departure, actual_departure,
            scheduled_arrival, actual_arrival,
            departure_delay, arrival_delay, delay_reason, flight_status
        ) VALUES (
            :flight_date, :flight_number, :airline_code, :airline_name,
            :origin_airport, :origin_city, :origin_country,
            :destination_airport, :destination_city, :destination_country,
            :flight_type, :scheduled_departure, :actual_departure,
            :scheduled_arrival, :actual_arrival,
            :departure_delay, :arrival_delay, :delay_reason, :flight_status
        )
    """)

    with engine.connect() as connection:
        # Delete old data first
        delete_old_flights(connection)

        # Insert new flights
        count = 0
        for flight in flights:
            if flight:
                connection.execute(insert_sql, flight)
                count += 1

        connection.commit()
        print(f"Successfully loaded {count} flights into raw.flights")
        return count

def run_ingestion():
    """Main ingestion function — fetch all routes and load to DB"""
    print(f"Starting ingestion at {datetime.now()}")
    print(f"Fetching data for {len(ROUTES)} routes...")

    all_flights = []
    api_calls = 0

    for route in ROUTES:
        dep = route["dep"]
        arr = route["arr"]
        flight_type = get_flight_type(dep, arr)

        print(f"Fetching {dep} -> {arr} ({flight_type})...")
        flights = fetch_flights_for_route(dep, arr)
        api_calls += 1

        for flight in flights:
            parsed = parse_flight(flight, flight_type)
            if parsed:
                all_flights.append(parsed)

    print(f"\nTotal API calls made: {api_calls}")
    print(f"Total flights fetched: {len(all_flights)}")

    # Load to database
    loaded = load_flights_to_db(all_flights)

    print(f"\nIngestion complete!")
    print(f"Flights loaded: {loaded}")
    print(f"Finished at {datetime.now()}")

if __name__ == "__main__":
    run_ingestion()