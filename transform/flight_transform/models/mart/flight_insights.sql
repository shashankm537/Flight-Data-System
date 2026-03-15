-- mart/flight_insights.sql
-- Aggregated insights for dashboard consumption

WITH fact AS (
    SELECT * FROM {{ ref('fact_flights') }}
),

-- Delay summary by airline
airline_summary AS (
    SELECT
        airline_code,
        airline_name,
        flight_type,
        COUNT(*)                                    AS total_flights,
        SUM(CASE WHEN is_delayed THEN 1 ELSE 0 END) AS delayed_flights,
        ROUND(AVG(arrival_delay)::numeric, 2)       AS avg_delay_mins,
        ROUND(
            100.0 * SUM(CASE WHEN is_delayed THEN 1 ELSE 0 END) / COUNT(*),
            2
        )                                           AS delay_percentage,
        SUM(CASE WHEN flight_status = 'cancelled' 
            THEN 1 ELSE 0 END)                      AS cancelled_flights
    FROM fact
    GROUP BY airline_code, airline_name, flight_type
),

-- Delay summary by route
route_summary AS (
    SELECT
        route,
        origin_airport,
        destination_airport,
        flight_type,
        COUNT(*)                                    AS total_flights,
        SUM(CASE WHEN is_delayed THEN 1 ELSE 0 END) AS delayed_flights,
        ROUND(AVG(arrival_delay)::numeric, 2)       AS avg_delay_mins,
        ROUND(
            100.0 * SUM(CASE WHEN is_delayed THEN 1 ELSE 0 END) / COUNT(*),
            2
        )                                           AS delay_percentage
    FROM fact
    GROUP BY route, origin_airport, destination_airport, flight_type
),

-- Delay by time of day
time_summary AS (
    SELECT
        time_of_day,
        COUNT(*)                                    AS total_flights,
        SUM(CASE WHEN is_delayed THEN 1 ELSE 0 END) AS delayed_flights,
        ROUND(AVG(arrival_delay)::numeric, 2)       AS avg_delay_mins
    FROM fact
    GROUP BY time_of_day
),

-- Overall summary
overall AS (
    SELECT
        COUNT(*)                                    AS total_flights,
        SUM(CASE WHEN is_delayed THEN 1 ELSE 0 END) AS total_delayed,
        SUM(CASE WHEN flight_status = 'cancelled' 
            THEN 1 ELSE 0 END)                      AS total_cancelled,
        ROUND(AVG(arrival_delay)::numeric, 2)       AS avg_delay_mins,
        ROUND(
            100.0 * SUM(CASE WHEN is_delayed THEN 1 ELSE 0 END) / COUNT(*),
            2
        )                                           AS overall_delay_percentage,
        MIN(flight_date)                            AS data_from,
        MAX(flight_date)                            AS data_to
    FROM fact
)

SELECT
    o.total_flights,
    o.total_delayed,
    o.total_cancelled,
    o.avg_delay_mins,
    o.overall_delay_percentage,
    o.data_from,
    o.data_to
FROM overall o