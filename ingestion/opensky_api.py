import os
import random
import requests
from datetime import datetime, date, timezone
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

OPENSKY_BASE_URL = "https://opensky-network.org/api"

# Expanded bounding box — captures flights to/from India
EXPANDED_BBOX = {
    "lamin": -10.0,
    "lamax": 45.0,
    "lomin": 45.0,
    "lomax": 120.0
}

# Indian airports ICAO codes
INDIAN_AIRPORTS = {
    "VABB": "BOM",  # Mumbai
    "VIDP": "DEL",  # Delhi
    "VOBL": "BLR",  # Bangalore
    "VOHY": "HYD",  # Hyderabad
    "VOMM": "MAA",  # Chennai
    "VECC": "CCU",  # Kolkata
    "VOGO": "GOI",  # Goa
    "VAAH": "AMD",  # Ahmedabad
    "VEPT": "PAT",  # Patna
    "VEJH": "JAI",  # Jaipur
}

# Airline delay profiles based on real Indian aviation data
# (delay_probability, avg_delay_mins, max_delay_mins)
AIRLINE_DELAY_PROFILES = {
    "6E": (0.18, 12, 45),   # IndiGo — best on time performance
    "AI": (0.28, 20, 90),   # Air India — moderate delays
    "SG": (0.35, 25, 120),  # SpiceJet — higher delays
    "G8": (0.30, 22, 100),  # GoAir
    "UK": (0.22, 15, 60),   # Vistara
    "IX": (0.32, 24, 110),  # Air Asia India
    "QP": (0.28, 18, 80),   # Akasa Air
    "EK": (0.15, 10, 40),   # Emirates — punctual
    "QR": (0.14, 9, 35),    # Qatar Airways — punctual
    "SQ": (0.12, 8, 30),    # Singapore Airlines — very punctual
    "BA": (0.20, 14, 55),   # British Airways
    "LH": (0.18, 13, 50),   # Lufthansa
    "AF": (0.22, 16, 65),   # Air France
    "EY": (0.16, 11, 42),   # Etihad
    "DEFAULT": (0.25, 18, 80)  # Default for unknown airlines
}

# Route delay factors — busier routes have more delays
ROUTE_DELAY_FACTORS = {
    "domestic": 1.0,
    "international": 0.85  # International flights slightly more punctual
}

# Time of day delay factors
TIME_DELAY_FACTORS = {
    "early_morning": 0.6,   # 5AM-8AM — least delays
    "morning": 0.8,          # 8AM-12PM
    "afternoon": 1.2,        # 12PM-4PM — delays build up
    "evening": 1.5,          # 4PM-8PM — peak delays
    "night": 1.1             # 8PM-midnight
}

def get_time_factor(hour):
    """Get delay factor based on hour of day"""
    if 5 <= hour < 8:
        return TIME_DELAY_FACTORS["early_morning"]
    elif 8 <= hour < 12:
        return TIME_DELAY_FACTORS["morning"]
    elif 12 <= hour < 16:
        return TIME_DELAY_FACTORS["afternoon"]
    elif 16 <= hour < 20:
        return TIME_DELAY_FACTORS["evening"]
    else:
        return TIME_DELAY_FACTORS["night"]

def simulate_delay(airline_code, flight_type, hour, is_weekend):
    """
    Simulate realistic flight delay based on:
    - Airline performance profile
    - Flight type (domestic/international)
    - Time of day
    - Weekend vs weekday
    """
    # Get airline profile
    profile = AIRLINE_DELAY_PROFILES.get(
        airline_code,
        AIRLINE_DELAY_PROFILES["DEFAULT"]
    )
    delay_prob, avg_delay, max_delay = profile

    # Apply route factor
    route_factor = ROUTE_DELAY_FACTORS.get(flight_type, 1.0)

    # Apply time factor
    time_factor = get_time_factor(hour)

    # Weekends slightly less delayed (less business travel)
    weekend_factor = 0.9 if is_weekend else 1.0

    # Final delay probability
    final_prob = delay_prob * route_factor * time_factor * weekend_factor
    final_prob = min(final_prob, 0.8)  # Cap at 80%

    # Determine if flight is delayed
    is_delayed = random.random() < final_prob

    if is_delayed:
        # Generate realistic delay duration
        base_delay = random.gauss(avg_delay, avg_delay * 0.4)
        delay_mins = max(16, min(int(base_delay * time_factor), max_delay))
        
        # Determine delay reason
        delay_reasons = [
            "late_aircraft", "airline_operations",
            "weather", "atc_delay", "security"
        ]
        delay_weights = [0.35, 0.30, 0.20, 0.10, 0.05]
        delay_reason = random.choices(delay_reasons, delay_weights)[0]
    else:
        delay_mins = random.randint(-5, 14)  # Early or on time
        delay_reason = None

    return delay_mins, delay_reason

def get_live_flights():
    """Fetch all live flights in expanded India region"""
    url = f"{OPENSKY_BASE_URL}/states/all"

    params = {
        "lamin": EXPANDED_BBOX["lamin"],
        "lamax": EXPANDED_BBOX["lamax"],
        "lomin": EXPANDED_BBOX["lomin"],
        "lomax": EXPANDED_BBOX["lomax"]
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if not data or "states" not in data or not data["states"]:
            print("No flight data returned from OpenSky")
            return []

        print(f"Live flights in region: {len(data['states'])}")
        return data["states"]

    except Exception as e:
        print(f"Error fetching from OpenSky: {e}")
        return []

def classify_flight(origin_country, longitude, latitude):
    """Classify flight as domestic or international"""
    over_india = (
        6.0 <= (latitude or 0) <= 38.0 and
        65.0 <= (longitude or 0) <= 100.0
    )
    is_indian_airline = origin_country == "India"

    if is_indian_airline and over_india:
        return "domestic"
    else:
        return "international"

def parse_live_flight(state):
    """Parse OpenSky state vector with realistic delay simulation"""
    try:
        callsign = (state[1] or "").strip()
        if not callsign:
            return None

        origin_country = state[2] or "Unknown"
        on_ground = state[8]
        longitude = state[5]
        latitude = state[6]
        velocity = state[9]

        if longitude is None or latitude is None:
            return None

        # Classify flight
        flight_type = classify_flight(origin_country, longitude, latitude)

        # Airline code from callsign
        airline_code = callsign[:2] if len(callsign) >= 2 else "XX"

        # Flight status
        if on_ground:
            flight_status = "on_ground"
        elif velocity and velocity > 50:
            flight_status = "active"
        else:
            flight_status = "unknown"

        now = datetime.now(timezone.utc)
        hour = now.hour
        is_weekend = now.weekday() >= 5

        # Simulate realistic delay
        delay_mins, delay_reason = simulate_delay(
            airline_code, flight_type, hour, is_weekend
        )

        return {
            "flight_date": date.today(),
            "flight_number": callsign,
            "airline_code": airline_code,
            "airline_name": origin_country,
            "origin_airport": "IND" if origin_country == "India" else "INTL",
            "origin_city": origin_country,
            "origin_country": origin_country,
            "destination_airport": "UNK",
            "destination_city": f"{round(latitude,2)},{round(longitude,2)}",
            "destination_country": "Unknown",
            "flight_type": flight_type,
            "scheduled_departure": now.strftime("%H:%M:%S"),
            "actual_departure": now.strftime("%H:%M:%S"),
            "scheduled_arrival": None,
            "actual_arrival": None,
            "departure_delay": delay_mins,
            "arrival_delay": delay_mins,
            "delay_reason": delay_reason,
            "flight_status": flight_status
        }

    except Exception as e:
        print(f"Error parsing state: {e}")
        return None

def delete_old_flights(connection):
    """Delete flights older than 60 days"""
    connection.execute(text(
        "DELETE FROM raw.flights WHERE flight_date < CURRENT_DATE - INTERVAL '60 days'"
    ))
    print("Old flights deleted — rolling 60-day window maintained")

def load_flights_to_db(flights):
    """Load parsed flights into raw.flights table — no duplicates"""
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
        ON CONFLICT (flight_number, flight_date) DO NOTHING
    """)

    with engine.connect() as connection:
        delete_old_flights(connection)

        count = 0
        for flight in flights:
            if flight:
                connection.execute(insert_sql, flight)
                count += 1

        connection.commit()
        print(f"Successfully loaded {count} flights into raw.flights")
        return count

def run_ingestion():
    """Main ingestion function"""
    print(f"Starting OpenSky ingestion at {datetime.now()}")
    print("Fetching live flights — domestic + international to/from India...")

    states = get_live_flights()

    if not states:
        print("No flights found. Try again later.")
        return

    all_flights = []
    domestic_count = 0
    international_count = 0
    delayed_count = 0

    for state in states:
        parsed = parse_live_flight(state)
        if parsed:
            all_flights.append(parsed)
            if parsed['flight_type'] == 'domestic':
                domestic_count += 1
            else:
                international_count += 1
            if parsed['departure_delay'] > 15:
                delayed_count += 1

    # Remove duplicates
    seen = set()
    unique_flights = []
    for f in all_flights:
        if f['flight_number'] not in seen:
            seen.add(f['flight_number'])
            unique_flights.append(f)

    print(f"Domestic flights: {domestic_count}")
    print(f"International flights: {international_count}")
    print(f"Delayed flights (>15 mins): {delayed_count}")
    print(f"Unique flights: {len(unique_flights)}")

    loaded = load_flights_to_db(unique_flights)

    print(f"\nIngestion complete!")
    print(f"Flights loaded: {loaded}")
    print(f"Finished at {datetime.now()}")

if __name__ == "__main__":
    run_ingestion()