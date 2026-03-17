import os
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
MODEL_PATH = "ml/models/flight_delay_model.pkl"

app = FastAPI(
    title="Flight Delay Prediction API",
    description="Predicts flight delays for Indian domestic and international routes",
    version="1.0.0"
)

# Global model variables
model = None
threshold = 0.3

@app.on_event("startup")
async def load_model():
    global model, threshold
    try:
        model_data = joblib.load(MODEL_PATH)
        model = model_data["model"]
        threshold = model_data["threshold"]
        print(f"Model loaded successfully from {MODEL_PATH}")
        print(f"Prediction threshold: {threshold}")
    except Exception as e:
        print(f"Error loading model: {e}")

# Request schema
class FlightInput(BaseModel):
    airline_code: str
    origin_airport: str
    destination_airport: str
    flight_type: str
    departure_hour: int
    day_of_week: int
    is_weekend: bool
    is_monsoon_season: bool
    avg_route_delay: float
    avg_carrier_delay: float

# Response schema
class PredictionResponse(BaseModel):
    flight: str
    delay_probability: float
    is_delayed: bool
    risk_level: str
    message: str

def encode_input(data: FlightInput) -> pd.DataFrame:
    """Encode input data for model prediction"""

    airline_map = {
        'AI': 0, '6E': 1, 'SG': 2, 'G8': 3, 'UK': 4,
        'QR': 5, 'EK': 6, 'SQ': 7, 'BA': 8, 'AF': 9,
        'LH': 10, 'VS': 11, 'QF': 12, 'JL': 13, 'KL': 14
    }

    airport_map = {
        'BOM': 0, 'DEL': 1, 'BLR': 2, 'HYD': 3, 'MAA': 4,
        'CCU': 5, 'GOI': 6, 'AMD': 7, 'DXB': 8, 'SIN': 9,
        'LHR': 10, 'JFK': 11, 'BKK': 12, 'KUL': 13, 'CDG': 14
    }

    route = f"{data.origin_airport}-{data.destination_airport}"
    route_map = {
        'BOM-DEL': 0, 'DEL-BOM': 1, 'BOM-BLR': 2, 'DEL-BLR': 3,
        'BOM-CCU': 4, 'DEL-MAA': 5, 'BLR-HYD': 6, 'DEL-CCU': 7,
        'BOM-GOI': 8, 'DEL-AMD': 9, 'BOM-DXB': 10, 'DEL-DXB': 11,
        'BLR-SIN': 12, 'DEL-LHR': 13, 'BOM-LHR': 14, 'DEL-JFK': 15,
        'BOM-SIN': 16, 'DEL-BKK': 17, 'BOM-KUL': 18, 'DEL-CDG': 19
    }

    features = {
        'airline_encoded': airline_map.get(data.airline_code, 99),
        'origin_encoded': airport_map.get(data.origin_airport, 99),
        'destination_encoded': airport_map.get(data.destination_airport, 99),
        'route_encoded': route_map.get(route, 99),
        'is_international': 1 if data.flight_type == 'international' else 0,
        'departure_hour': data.departure_hour,
        'day_of_week': data.day_of_week,
        'is_weekend': int(data.is_weekend),
        'is_monsoon_season': int(data.is_monsoon_season),
        'avg_route_delay': data.avg_route_delay,
        'avg_carrier_delay': data.avg_carrier_delay
    }

    return pd.DataFrame([features])

@app.get("/")
async def root():
    return {
        "message": "Flight Delay Prediction API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "threshold": threshold
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict(flight: FlightInput):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        X = encode_input(flight)

        # Use trained threshold for prediction
        prob = model.predict_proba(X)[0][1]
        is_delayed = bool(prob >= threshold)

        # Risk level
        if prob < 0.3:
            risk_level = "low"
            message = "Flight is likely to be on time"
        elif prob < 0.6:
            risk_level = "medium"
            message = "Flight has moderate delay risk"
        else:
            risk_level = "high"
            message = "Flight is likely to be delayed"

        route = f"{flight.origin_airport}-{flight.destination_airport}"

        return PredictionResponse(
            flight=f"{flight.airline_code} {route}",
            delay_probability=round(float(prob), 4),
            is_delayed=is_delayed,
            risk_level=risk_level,
            message=message
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get current flight statistics from database"""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_flights,
                    SUM(CASE WHEN is_delayed THEN 1 ELSE 0 END) as delayed_flights,
                    ROUND(AVG(arrival_delay)::numeric, 2) as avg_delay_mins,
                    MIN(flight_date) as data_from,
                    MAX(flight_date) as data_to
                FROM warehouse_warehouse.fact_flights
            """))
            row = result.fetchone()
            return {
                "total_flights": row[0],
                "delayed_flights": row[1],
                "avg_delay_mins": float(row[2]) if row[2] else 0,
                "data_from": str(row[3]),
                "data_to": str(row[4])
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))