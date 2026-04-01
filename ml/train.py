import os
import pandas as pd
import numpy as np
import mlflow
import mlflow.xgboost
import joblib
from datetime import datetime
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score,
    recall_score, confusion_matrix, roc_auc_score
)
from xgboost import XGBClassifier

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# MLflow setup
import tempfile
mlflow.set_tracking_uri("mlruns")
mlflow.set_experiment("flight_delay_prediction")

def fetch_features():
    """Fetch engineered features from ml.features"""
    engine = create_engine(DATABASE_URL)

    query = """
        SELECT 
            airline_code,
            origin_airport,
            destination_airport,
            flight_type,
            departure_hour,
            day_of_week,
            is_weekend,
            is_monsoon_season,
            route,
            avg_route_delay,
            avg_carrier_delay,
            is_delayed
        FROM ml.features
    """

    df = pd.read_sql(query, engine)
    print(f"Fetched {len(df)} rows from ml.features")
    return df

def prepare_data(df):
    """Prepare features and target for training"""

    # Encode categorical columns
    df['airline_encoded'] = df['airline_code'].astype('category').cat.codes
    df['origin_encoded'] = df['origin_airport'].astype('category').cat.codes
    df['destination_encoded'] = df['destination_airport'].astype('category').cat.codes
    df['route_encoded'] = df['route'].astype('category').cat.codes
    df['is_international'] = (df['flight_type'] == 'international').astype(int)
    df['is_weekend'] = df['is_weekend'].astype(int)
    df['is_monsoon_season'] = df['is_monsoon_season'].astype(int)

    # Feature columns
    feature_cols = [
        'airline_encoded',
        'origin_encoded',
        'destination_encoded',
        'route_encoded',
        'is_international',
        'departure_hour',
        'day_of_week',
        'is_weekend',
        'is_monsoon_season',
        'avg_route_delay',
        'avg_carrier_delay'
    ]

    X = df[feature_cols]
    y = df['is_delayed'].astype(int)

    print(f"Features: {feature_cols}")
    print(f"Target distribution: {y.value_counts().to_dict()}")

    return X, y, feature_cols

def train_model(X, y):
    """Train XGBoost model with class imbalance handling"""

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42,
        stratify=y if y.sum() > 1 else None
    )

    print(f"Train size: {len(X_train)} | Test size: {len(X_test)}")

    # Calculate scale_pos_weight to handle class imbalance
    # This tells XGBoost to weight the minority class higher
    neg_count = (y_train == 0).sum()
    pos_count = (y_train == 1).sum()
    scale_pos_weight = neg_count / pos_count if pos_count > 0 else 1
    print(f"scale_pos_weight: {scale_pos_weight:.2f} (handles class imbalance)")

    with mlflow.start_run():
        # Model parameters with class imbalance handling
        params = {
            "n_estimators": 200,
            "max_depth": 5,
            "learning_rate": 0.05,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": 42,
            "eval_metric": "logloss",
            "scale_pos_weight": scale_pos_weight,  # Key fix for imbalance
            "min_child_weight": 3,
            "gamma": 0.1
        }

        # Train model
        model = XGBClassifier(**params)
        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )

        # Use lower threshold for predictions (0.3 instead of 0.5)
        # This makes model more sensitive to delays
        y_prob = model.predict_proba(X_test)[:, 1]
        threshold = 0.3
        y_pred = (y_prob >= threshold).astype(int)

        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)

        try:
            auc = roc_auc_score(y_test, y_prob)
        except:
            auc = 0.0

        # Log to MLflow
        mlflow.log_params(params)
        mlflow.log_param("prediction_threshold", threshold)
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("f1_score", f1)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("auc", auc)
        mlflow.log_metric("train_size", len(X_train))
        mlflow.log_metric("test_size", len(X_test))
        mlflow.log_metric("scale_pos_weight", scale_pos_weight)

        # Log model
        mlflow.xgboost.log_model(model, "model")

        print("\nModel Performance:")
        print(f"  Accuracy:  {accuracy:.4f}")
        print(f"  F1 Score:  {f1:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall:    {recall:.4f}")
        print(f"  AUC:       {auc:.4f}")
        print(f"\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))

        # Save model and threshold locally
        os.makedirs("ml/models", exist_ok=True)
        model_path = "ml/models/flight_delay_model.pkl"
        joblib.dump({
            "model": model,
            "threshold": threshold,
            "feature_cols": list(X.columns)
        }, model_path)
        print(f"\nModel saved to {model_path}")

        return model, accuracy, f1

def run_training():
    """Main training function"""
    print(f"Starting model training at {datetime.now()}")
    print("="*50)

    # Fetch features
    df = fetch_features()

    if df.empty:
        print("No features found. Run feature engineering first.")
        return

    # Prepare data
    X, y, feature_cols = prepare_data(df)

    # Train model
    model, accuracy, f1 = train_model(X, y)

    print("="*50)
    print(f"Training complete at {datetime.now()}")
    print(f"Best accuracy: {accuracy:.4f}")
    print(f"Best F1 score: {f1:.4f}")

if __name__ == "__main__":
    run_training()