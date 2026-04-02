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

# Airport coordinates for nearest airport estimation
AIRPORT_COORDS = {
    "BOM": (19.0896, 72.8656),
    "DEL": (28.5562, 77.1000),
    "BLR": (13.1986, 77.7066),
    "HYD": (17.2403, 78.4294),
    "MAA": (12.9941, 80.1709),
    "CCU": (22.6520, 88.4463),
    "GOI": (15.3808, 73.8314),
    "AMD": (23.0772, 72.6347),
    "PAT": (25.5913, 85.0880),
    "JAI": (26.8242, 75.8122),
    "LKO": (26.7606, 80.8893),
    "BBI": (20.2444, 85.8178),
    "PNQ": (18.5822, 73.9197),
    "COK": (10.1520, 76.4019),
    "TRV": (8.4821, 76.9201),
    "IXC": (30.6735, 76.7885),
    "SXR": (33.9871, 74.7742),
    "IXB": (26.6812, 88.3286),
    "GAU": (26.1061, 91.5859),
    "DXB": (25.2532, 55.3657),
    "SIN": (1.3644, 103.9915),
    "BKK": (13.6811, 100.7472),
    "KUL": (2.7456, 101.7099),
    "LHR": (51.4775, -0.4614),
    "CDG": (49.0097, 2.5479),
    "FRA": (50.0379, 8.5622),
    "DOH": (25.2609, 51.6138),
    "AUH": (24.4330, 54.6511),
}

INDIAN_AIRPORT_CODES = [
    "BOM", "DEL", "BLR", "HYD", "MAA", "CCU",
    "GOI", "AMD", "PAT", "JAI", "LKO", "BBI",
    "PNQ", "COK", "TRV", "IXC", "SXR", "IXB", "GAU"
]

INTL_AIRPORT_CODES = [
    "DXB", "SIN", "BKK", "KUL", "LHR", "CDG", "FRA", "DOH", "AUH"
]

# Airline delay profiles
AIRLINE_DELAY_PROFILES = {
    "6E": (0.18, 12, 45),
    "AI": (0.28, 20, 90),
    "SG": (0.35, 25, 120),
    "G8": (0.30, 22, 100),
    "UK": (0.22, 15, 60),
    "IX": (0.32, 24, 110),
    "QP": (0.28, 18, 80),
    "EK": (0.15, 10, 40),
    "QR": (0.14, 9, 35),
    "SQ": (0.12, 8, 30),
    "BA": (0.20, 14, 55),
    "LH": (0.18, 13, 50),
    "AF": (0.22, 16, 65),
    "EY": (0.16, 11, 42),
    "DEFAULT": (0.25, 18, 80)
}

ROUTE_DELAY_FACTORS = {
    "domestic": 1.0,
    "international": 0.85
}

TIME_DELAY_FACTORS = {
    "early_morning": 0.6,
    "morning": 0.8,
    "afternoon": 1.2,
    "evening": 1.5,
    "night": 1.1
}

def get_time_factor(hour):
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
    profile = AIRLINE_DELAY_PROFILES.get(airline_code, AIRLINE_DELAY_PROFILES["DEFAULT"])
    delay_prob, avg_delay, max_delay = profile
    route_factor = ROUTE_DELAY_FACTORS.get(flight_type, 1.0)
    time_factor = get_time_factor(hour)
    weekend_factor = 0.9 if is_weekend else 1.0
    final_prob = min(delay_prob * route_factor * time_factor * weekend_factor, 0.8)
    is_delayed = random.random() < final_prob

    if is_delayed:
        base_delay = random.gauss(avg_delay, avg_delay * 0.4)
        delay_mins = max(16, min(int(base_delay * time_factor), max_delay))
        delay_reasons = ["late_aircraft", "airline_operations", "weather", "atc_delay", "security"]
        delay_weights = [0.35, 0.30, 0.20, 0.10, 0.05]
        delay_reason = random.choices(delay_reasons, delay_weights)[0]
    else:
        delay_mins = random.randint(-5, 14)
        delay_reason = None

    return delay_mins, delay_reason

def get_nearest_airport(latitude, longitude, flight_type):
    """Estimate nearest airport based on lat/lon coordinates"""
    if latitude is None or longitude is None:
        if flight_type == "domestic":
            origin = random.choice(INDIAN_AIRPORT_CODES)
            destination = random.choice([a for a in INDIAN_AIRPORT_CODES if a != origin])
        else:
            origin = random.choice(INDIAN_AIRPORT_CODES)
            destination = random.choice(INTL_AIRPORT_CODES)
        return origin, destination

    if flight_type == "domestic":
        # Find nearest Indian airport as origin
        min_dist = float('inf')
        nearest = "DEL"
        for code in INDIAN_AIRPORT_CODES:
            alat, alon = AIRPORT_COORDS[code]
            dist = ((latitude - alat) ** 2 + (longitude - alon) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                nearest = code
        destination = random.choice([a for a in INDIAN_AIRPORT_CODES if a != nearest])
        return nearest, destination
    else:
        # Find nearest airport overall as origin
        min_dist = float('inf')
        nearest = "DXB"
        for code, (alat, alon) in AIRPORT_COORDS.items():
            dist = ((latitude - alat) ** 2 + (longitude - alon) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                nearest = code
        destination = random.choice(INTL_AIRPORT_CODES)
        return nearest, destination

def get_live_flights():
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

        flight_type = classify_flight(origin_country, longitude, latitude)
        airline_code = callsign[:2] if len(callsign) >= 2 else "XX"

        if on_ground:
            flight_status = "on_ground"
        elif velocity and velocity > 50:
            flight_status = "active"
        else:
            flight_status = "unknown"

        now = datetime.now(timezone.utc)
        hour = now.hour
        is_weekend = now.weekday() >= 5

        delay_mins, delay_reason = simulate_delay(airline_code, flight_type, hour, is_weekend)

        # Get estimated airports based on coordinates
        origin_airport, destination_airport = get_nearest_airport(latitude, longitude, flight_type)

        return {
            "flight_date": date.today(),
            "flight_number": callsign,
            "airline_code": airline_code,
            "airline_name": origin_country,
            "origin_airport": origin_airport,
            "origin_city": origin_country,
            "origin_country": origin_country,
            "destination_airport": destination_airport,
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
    connection.execute(text(
        "DELETE FROM raw.flights WHERE flight_date < CURRENT_DATE - INTERVAL '60 days'"
    ))
    print("Old flights deleted — rolling 60-day window maintained")

def load_flights_to_db(flights):
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