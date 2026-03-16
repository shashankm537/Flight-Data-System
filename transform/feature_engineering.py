import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_engine():
    return create_engine(DATABASE_URL)

def fetch_warehouse_data():
    """Fetch cleaned data from warehouse.fact_flights"""
    engine = get_engine()
    
    query = """
        SELECT 
            flight_date,
            flight_number,
            airline_code,
            origin_airport,
            destination_airport,
            flight_type,
            departure_delay,
            arrival_delay,
            delay_category,
            is_delayed,
            time_of_day,
            day_of_week,
            is_weekend,
            is_monsoon_season,
            route,
            flight_status
        FROM warehouse_warehouse.fact_flights
        WHERE flight_status != 'cancelled'
    """
    
    df = pd.read_sql(query, engine)
    print(f"Fetched {len(df)} flights from warehouse")
    return df

def engineer_features(df):
    """Engineer features for ML model"""
    
    # Departure hour from flight_date
    df['departure_hour'] = pd.to_datetime(df['flight_date']).dt.hour
    
    # Encode time of day
    time_map = {'morning': 0, 'afternoon': 1, 'evening': 2, 'night': 3}
    df['time_of_day_encoded'] = df['time_of_day'].map(time_map).fillna(0)
    
    # Encode flight type
    df['is_international'] = (df['flight_type'] == 'international').astype(int)
    
    # Average delay per route
    route_avg = df.groupby('route')['arrival_delay'].mean().reset_index()
    route_avg.columns = ['route', 'avg_route_delay']
    df = df.merge(route_avg, on='route', how='left')
    
    # Average delay per carrier
    carrier_avg = df.groupby('airline_code')['arrival_delay'].mean().reset_index()
    carrier_avg.columns = ['airline_code', 'avg_carrier_delay']
    df = df.merge(carrier_avg, on='airline_code', how='left')
    
    # Encode airline code
    df['airline_encoded'] = df['airline_code'].astype('category').cat.codes
    
    # Encode origin airport
    df['origin_encoded'] = df['origin_airport'].astype('category').cat.codes
    
    # Encode destination airport
    df['destination_encoded'] = df['destination_airport'].astype('category').cat.codes
    
    # Fill nulls
    df['avg_route_delay'] = df['avg_route_delay'].fillna(0)
    df['avg_carrier_delay'] = df['avg_carrier_delay'].fillna(0)
    df['is_weekend'] = df['is_weekend'].astype(bool)
    df['is_monsoon_season'] = df['is_monsoon_season'].astype(bool)
    
    print(f"Features engineered successfully")
    print(f"Total features: {len(df.columns)}")
    
    return df

def save_features_to_db(df):
    """Save engineered features to ml.features table"""
    engine = get_engine()
    
    features_df = df[[
        'flight_date',
        'flight_number',
        'airline_code',
        'origin_airport',
        'destination_airport',
        'flight_type',
        'departure_hour',
        'day_of_week',
        'is_weekend',
        'is_monsoon_season',
        'route',
        'avg_route_delay',
        'avg_carrier_delay',
        'is_delayed'
    ]].copy()
    
    # Clear existing features
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE ml.features"))
        conn.commit()
    
    # Save to database
    features_df.to_sql(
        'features',
        engine,
        schema='ml',
        if_exists='append',
        index=False
    )
    
    print(f"Saved {len(features_df)} feature rows to ml.features")
    return features_df

def run_feature_engineering():
    """Main function"""
    print("Starting feature engineering...")
    
    # Fetch data
    df = fetch_warehouse_data()
    
    if df.empty:
        print("No data found in warehouse. Run ingestion first.")
        return None
    
    # Engineer features
    df = engineer_features(df)
    
    # Save to DB
    features_df = save_features_to_db(df)
    
    print("\nFeature engineering complete!")
    print(f"Features saved: {len(features_df)}")
    
    return df

if __name__ == "__main__":
    run_feature_engineering()