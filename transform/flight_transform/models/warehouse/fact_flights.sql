-- warehouse/fact_flights.sql
-- Final fact table with enriched delay information

WITH stg AS (
    SELECT * FROM {{ ref('stg_flights') }}
),

enriched AS (
    SELECT
        flight_date,
        flight_number,
        airline_code,
        airline_name,
        origin_airport,
        origin_country,
        destination_airport,
        destination_country,
        flight_type,
        route,
        departure_delay,
        arrival_delay,
        delay_reason,
        flight_status,

        -- Is flight delayed (more than 15 mins)
        CASE 
            WHEN arrival_delay > 15 THEN TRUE 
            ELSE FALSE 
        END AS is_delayed,

        -- Delay category
        CASE
            WHEN arrival_delay <= 0  THEN 'no delay'
            WHEN arrival_delay <= 15 THEN 'minor'
            WHEN arrival_delay <= 60 THEN 'moderate'
            ELSE 'severe'
        END AS delay_category,

        -- Time of day
        CASE
            WHEN EXTRACT(HOUR FROM scheduled_departure) BETWEEN 5 AND 11  THEN 'morning'
            WHEN EXTRACT(HOUR FROM scheduled_departure) BETWEEN 12 AND 16 THEN 'afternoon'
            WHEN EXTRACT(HOUR FROM scheduled_departure) BETWEEN 17 AND 20 THEN 'evening'
            ELSE 'night'
        END AS time_of_day,

        -- Day of week
        EXTRACT(DOW FROM flight_date) AS day_of_week,

        -- Is weekend
        CASE 
            WHEN EXTRACT(DOW FROM flight_date) IN (0, 6) THEN TRUE 
            ELSE FALSE 
        END AS is_weekend,

        -- Is monsoon season (June to September)
        CASE 
            WHEN EXTRACT(MONTH FROM flight_date) BETWEEN 6 AND 9 THEN TRUE 
            ELSE FALSE 
        END AS is_monsoon_season,

        created_at

    FROM stg
)

SELECT * FROM enriched