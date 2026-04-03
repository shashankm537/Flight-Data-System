"""
test_api.py
Tests for FastAPI endpoints — /, /health, /predict, /stats
Run with: pytest tests/test_api.py -v
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


VALID_FLIGHT_INPUT = {
    "airline_code": "6E",
    "origin_airport": "BOM",
    "destination_airport": "DEL",
    "flight_type": "domestic",
    "departure_hour": 18,
    "day_of_week": 4,
    "is_weekend": False,
    "is_monsoon_season": False,
    "avg_route_delay": 12.5,
    "avg_carrier_delay": 10.0
}


@pytest.fixture
def client():
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = [[0.65, 0.35]]
    with patch("api.main.model", mock_model), \
         patch("api.main.threshold", 0.3):
        from api.main import app
        with TestClient(app) as c:
            yield c


@pytest.fixture
def client_no_model():
    with patch("api.main.model", None), \
         patch("api.main.load_model", return_value=None):
        from api.main import app
        with TestClient(app) as c:
            yield c


def test_root_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_root_returns_correct_fields(client):
    response = client.get("/")
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "status" in data
    assert data["status"] == "running"
    assert data["version"] == "1.0.0"


def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_shows_model_loaded(client):
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["threshold"] == 0.3


def test_health_shows_model_loaded_status_is_bool(client):
    response = client.get("/health")
    data = response.json()
    assert isinstance(data["model_loaded"], bool)


def test_predict_returns_200_with_valid_input(client):
    response = client.post("/predict", json=VALID_FLIGHT_INPUT)
    assert response.status_code == 200


def test_predict_response_has_required_fields(client):
    response = client.post("/predict", json=VALID_FLIGHT_INPUT)
    data = response.json()
    assert "flight" in data
    assert "delay_probability" in data
    assert "is_delayed" in data
    assert "risk_level" in data
    assert "message" in data


def test_predict_delay_probability_is_float_between_0_and_1(client):
    response = client.post("/predict", json=VALID_FLIGHT_INPUT)
    prob = response.json()["delay_probability"]
    assert isinstance(prob, float)
    assert 0.0 <= prob <= 1.0


def test_predict_is_delayed_returns_bool(client):
    response = client.post("/predict", json=VALID_FLIGHT_INPUT)
    data = response.json()
    assert isinstance(data["is_delayed"], bool)


def test_predict_risk_level_is_valid_value(client):
    response = client.post("/predict", json=VALID_FLIGHT_INPUT)
    risk = response.json()["risk_level"]
    assert risk in ["low", "medium", "high"]


def test_predict_returns_200_when_model_is_loaded(client):
    response = client.post("/predict", json=VALID_FLIGHT_INPUT)
    assert response.status_code == 200


def test_predict_returns_422_with_missing_fields(client):
    response = client.post("/predict", json={"airline_code": "6E"})
    assert response.status_code == 422


def test_predict_flight_label_contains_route(client):
    response = client.post("/predict", json=VALID_FLIGHT_INPUT)
    flight_label = response.json()["flight"]
    assert "BOM" in flight_label
    assert "DEL" in flight_label


def test_stats_returns_200(client):
    mock_row = (7882, 1830, 8.49, "2025-01-01", "2025-03-22")
    mock_result = MagicMock()
    mock_result.fetchone.return_value = mock_row
    mock_conn = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.execute.return_value = mock_result
    mock_engine = MagicMock()
    mock_engine.connect.return_value = mock_conn
    with patch("api.main.create_engine", return_value=mock_engine):
        response = client.get("/stats")
    assert response.status_code == 200


def test_stats_returns_correct_fields(client):
    mock_row = (7882, 1830, 8.49, "2025-01-01", "2025-03-22")
    mock_result = MagicMock()
    mock_result.fetchone.return_value = mock_row
    mock_conn = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.execute.return_value = mock_result
    mock_engine = MagicMock()
    mock_engine.connect.return_value = mock_conn
    with patch("api.main.create_engine", return_value=mock_engine):
        response = client.get("/stats")
        data = response.json()
    assert "total_flights" in data
    assert "delayed_flights" in data
    assert "avg_delay_mins" in data
    assert "data_from" in data
    assert "data_to" in data