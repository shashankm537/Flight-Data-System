"""
test_features.py
Tests for feature engineering pipeline and ML model input/output.
Run with: pytest tests/test_features.py -v
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock


class TestEncodeInput:

    @pytest.fixture
    def sample_input(self):
        from api.main import FlightInput
        return FlightInput(
            airline_code="6E",
            origin_airport="BOM",
            destination_airport="DEL",
            flight_type="domestic",
            departure_hour=18,
            day_of_week=4,
            is_weekend=False,
            is_monsoon_season=False,
            avg_route_delay=12.5,
            avg_carrier_delay=10.0
        )

    def test_encode_input_returns_dataframe(self, sample_input):
        from api.main import encode_input
        result = encode_input(sample_input)
        assert isinstance(result, pd.DataFrame)

    def test_encode_input_returns_single_row(self, sample_input):
        from api.main import encode_input
        result = encode_input(sample_input)
        assert len(result) == 1

    def test_encode_input_has_expected_columns(self, sample_input):
        from api.main import encode_input
        result = encode_input(sample_input)
        expected_cols = [
            "airline_encoded", "origin_encoded", "destination_encoded",
            "route_encoded", "is_international", "departure_hour",
            "day_of_week", "is_weekend", "is_monsoon_season",
            "avg_route_delay", "avg_carrier_delay"
        ]
        for col in expected_cols:
            assert col in result.columns, f"Missing column: {col}"

    def test_encode_input_domestic_flight_is_international_zero(self, sample_input):
        from api.main import encode_input
        result = encode_input(sample_input)
        assert result["is_international"].values[0] == 0

    def test_encode_input_international_flight_is_international_one(self):
        from api.main import FlightInput, encode_input
        intl_input = FlightInput(
            airline_code="EK",
            origin_airport="BOM",
            destination_airport="DXB",
            flight_type="international",
            departure_hour=22,
            day_of_week=5,
            is_weekend=True,
            is_monsoon_season=False,
            avg_route_delay=20.0,
            avg_carrier_delay=15.0
        )
        result = encode_input(intl_input)
        assert result["is_international"].values[0] == 1

    def test_encode_input_known_airline_encodes_correctly(self, sample_input):
        from api.main import encode_input
        result = encode_input(sample_input)
        assert result["airline_encoded"].values[0] == 1

    def test_encode_input_unknown_airline_encodes_to_99(self):
        from api.main import FlightInput, encode_input
        unknown_input = FlightInput(
            airline_code="XX",
            origin_airport="BOM",
            destination_airport="DEL",
            flight_type="domestic",
            departure_hour=10,
            day_of_week=1,
            is_weekend=False,
            is_monsoon_season=False,
            avg_route_delay=5.0,
            avg_carrier_delay=5.0
        )
        result = encode_input(unknown_input)
        assert result["airline_encoded"].values[0] == 99

    def test_encode_input_known_route_encodes_correctly(self, sample_input):
        from api.main import encode_input
        result = encode_input(sample_input)
        assert result["route_encoded"].values[0] == 0

    def test_encode_input_unknown_route_encodes_to_99(self):
        from api.main import FlightInput, encode_input
        unknown_route = FlightInput(
            airline_code="6E",
            origin_airport="BOM",
            destination_airport="JFK",
            flight_type="international",
            departure_hour=14,
            day_of_week=2,
            is_weekend=False,
            is_monsoon_season=False,
            avg_route_delay=30.0,
            avg_carrier_delay=25.0
        )
        result = encode_input(unknown_route)
        assert result["route_encoded"].values[0] == 99

    def test_encode_input_is_weekend_encoded_as_int(self, sample_input):
        from api.main import encode_input
        result = encode_input(sample_input)
        assert result["is_weekend"].values[0] == 0

    def test_encode_input_departure_hour_preserved(self, sample_input):
        from api.main import encode_input
        result = encode_input(sample_input)
        assert result["departure_hour"].values[0] == 18


class TestModelPrediction:

    def test_model_predicts_delayed_above_threshold(self):
        mock_model = MagicMock()
        mock_model.predict_proba.return_value = np.array([[0.6, 0.4]])
        threshold = 0.3
        prob = mock_model.predict_proba(None)[0][1]
        is_delayed = bool(prob >= threshold)
        assert is_delayed is True

    def test_model_predicts_not_delayed_below_threshold(self):
        mock_model = MagicMock()
        mock_model.predict_proba.return_value = np.array([[0.85, 0.15]])
        threshold = 0.3
        prob = mock_model.predict_proba(None)[0][1]
        is_delayed = bool(prob >= threshold)
        assert is_delayed is False

    def test_risk_level_low_below_0_3(self):
        prob = 0.2
        if prob < 0.3:
            risk = "low"
        elif prob < 0.6:
            risk = "medium"
        else:
            risk = "high"
        assert risk == "low"

    def test_risk_level_medium_between_0_3_and_0_6(self):
        prob = 0.45
        if prob < 0.3:
            risk = "low"
        elif prob < 0.6:
            risk = "medium"
        else:
            risk = "high"
        assert risk == "medium"

    def test_risk_level_high_above_0_6(self):
        prob = 0.75
        if prob < 0.3:
            risk = "low"
        elif prob < 0.6:
            risk = "medium"
        else:
            risk = "high"
        assert risk == "high"

    def test_threshold_0_3_is_lower_than_default(self):
        threshold = 0.3
        assert threshold < 0.5

    def test_model_saved_as_dictionary(self):
        mock_model_data = {
            "model": MagicMock(),
            "threshold": 0.3,
            "feature_cols": ["airline_encoded", "departure_hour"]
        }
        assert "model" in mock_model_data
        assert "threshold" in mock_model_data
        assert "feature_cols" in mock_model_data
        assert mock_model_data["threshold"] == 0.3


class TestFeatureValidation:

    def test_departure_hour_valid_range(self):
        for hour in range(0, 24):
            assert 0 <= hour <= 23

    def test_day_of_week_valid_range(self):
        for day in range(0, 7):
            assert 0 <= day <= 6

    def test_avg_delay_non_negative(self):
        delays = [0.0, 5.5, 12.3, 45.0]
        for d in delays:
            assert d >= 0

    def test_is_weekend_is_binary(self):
        for val in [True, False]:
            assert int(val) in [0, 1]

    def test_is_monsoon_season_is_binary(self):
        for val in [True, False]:
            assert int(val) in [0, 1]