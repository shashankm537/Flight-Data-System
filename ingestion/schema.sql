-- Create schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS warehouse;
CREATE SCHEMA IF NOT EXISTS ml;

-- Raw flights table (staging)
CREATE TABLE IF NOT EXISTS raw.flights (
    id SERIAL PRIMARY KEY,
    flight_date DATE NOT NULL,
    flight_number VARCHAR(20),
    airline_code VARCHAR(10),
    airline_name VARCHAR(100),
    origin_airport VARCHAR(10),
    origin_city VARCHAR(100),
    origin_country VARCHAR(100),
    destination_airport VARCHAR(10),
    destination_city VARCHAR(100),
    destination_country VARCHAR(100),
    flight_type VARCHAR(20),        -- 'domestic' or 'international'
    scheduled_departure TIME,
    actual_departure TIME,
    scheduled_arrival TIME,
    actual_arrival TIME,
    departure_delay INTEGER,
    arrival_delay INTEGER,
    delay_reason VARCHAR(50),
    flight_status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_flight_date 
    ON raw.flights(flight_date);

CREATE INDEX IF NOT EXISTS idx_airline 
    ON raw.flights(airline_code);

CREATE INDEX IF NOT EXISTS idx_flight_type 
    ON raw.flights(flight_type);

-- Auto delete flights older than 60 days
CREATE OR REPLACE FUNCTION delete_old_flights()
RETURNS void AS $$
BEGIN
    DELETE FROM raw.flights 
    WHERE flight_date < CURRENT_DATE - INTERVAL '60 days';
    RAISE NOTICE 'Old flights deleted successfully';
END;
$$ LANGUAGE plpgsql;

-- Warehouse fact table
CREATE TABLE IF NOT EXISTS warehouse.fact_flights (
    id SERIAL PRIMARY KEY,
    flight_date DATE NOT NULL,
    flight_number VARCHAR(20),
    airline_code VARCHAR(10),
    airline_name VARCHAR(100),
    origin_airport VARCHAR(10),
    origin_country VARCHAR(100),
    destination_airport VARCHAR(10),
    destination_country VARCHAR(100),
    flight_type VARCHAR(20),
    departure_delay INTEGER,
    arrival_delay INTEGER,
    delay_reason VARCHAR(50),
    is_delayed BOOLEAN,
    delay_category VARCHAR(20),     -- 'no delay', 'minor', 'moderate', 'severe'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster dashboard queries
CREATE INDEX IF NOT EXISTS idx_wh_flight_date 
    ON warehouse.fact_flights(flight_date);

CREATE INDEX IF NOT EXISTS idx_wh_flight_type 
    ON warehouse.fact_flights(flight_type);

CREATE INDEX IF NOT EXISTS idx_wh_airline 
    ON warehouse.fact_flights(airline_code);

-- ML features table
CREATE TABLE IF NOT EXISTS ml.features (
    id SERIAL PRIMARY KEY,
    flight_date DATE NOT NULL,
    flight_number VARCHAR(20),
    airline_code VARCHAR(10),
    origin_airport VARCHAR(10),
    destination_airport VARCHAR(10),
    flight_type VARCHAR(20),
    departure_hour INTEGER,
    day_of_week INTEGER,            -- 0=Monday, 6=Sunday
    is_weekend BOOLEAN,
    is_monsoon_season BOOLEAN,      -- June to September
    route VARCHAR(20),              -- e.g. 'BOM-DEL'
    avg_route_delay FLOAT,
    avg_carrier_delay FLOAT,
    avg_carrier_delay_intl FLOAT,   -- international specific
    is_delayed BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);