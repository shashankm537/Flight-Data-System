-- staging/stg_flights.sql
-- Clean and standardize raw flight data

WITH source AS (
    SELECT * FROM raw.flights
),

cleaned AS (
    SELECT
        id,
        flight_date,
        
        -- Clean flight details
        UPPER(TRIM(flight_number))      AS flight_number,
        UPPER(TRIM(airline_code))       AS airline_code,
        INITCAP(TRIM(airline_name))     AS airline_name,
        
        -- Clean airport details
        UPPER(TRIM(origin_airport))     AS origin_airport,
        TRIM(origin_city)               AS origin_city,
        TRIM(origin_country)            AS origin_country,
        UPPER(TRIM(destination_airport)) AS destination_airport,
        TRIM(destination_city)          AS destination_city,
        TRIM(destination_country)       AS destination_country,
        
        -- Flight type
        LOWER(TRIM(flight_type))        AS flight_type,
        
        -- Times
        scheduled_departure,
        actual_departure,
        scheduled_arrival,
        actual_arrival,
        
        -- Delays — treat NULL as 0
        COALESCE(departure_delay, 0)    AS departure_delay,
        COALESCE(arrival_delay, 0)      AS arrival_delay,
        
        -- Delay reason
        COALESCE(delay_reason, 'unknown') AS delay_reason,
        
        -- Flight status
        LOWER(TRIM(flight_status))      AS flight_status,

        -- Departure hour
        EXTRACT(HOUR FROM scheduled_departure)::INT AS departure_hour,
        
        -- Route
        UPPER(TRIM(origin_airport)) || '-' || 
        UPPER(TRIM(destination_airport)) AS route,
        
        created_at

    FROM source
    WHERE flight_number IS NOT NULL
      AND flight_date IS NOT NULL
      AND origin_airport IS NOT NULL
      AND destination_airport IS NOT NULL
)

SELECT * FROM cleaned