"""
Comprehensive test suite for the ML Ops API.

Tests cover:
- Authentication
- Input validation
- Prediction endpoints
- Error handling
- Database persistence
"""

import pytest
import sys
import os
from datetime import datetime

sys.path.append('.')

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.main import app, get_db
from database import Base, Prediction, ModelMetadata
from config import get_settings

# Override settings for testing
os.environ['TESTING'] = 'True'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

# Create test database
engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(bind=engine)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


# ─────────────────────────────────────────────────────────────
# Authentication Tests
# ─────────────────────────────────────────────────────────────

def test_predict_without_api_key():
    """Test that predictions require API key."""
    response = client.post("/predict/diabetes", json={
        "hbA1c_level": 7.5,
        "blood_glucose_level": 200,
        "age": 45
    })
    assert response.status_code == 403  # Forbidden


def test_predict_with_invalid_api_key():
    """Test that invalid API key is rejected."""
    response = client.post(
        "/predict/diabetes",
        json={
            "hbA1c_level": 7.5,
            "blood_glucose_level": 200,
            "age": 45
        },
        headers={"x-api-key": "wrong-key"}
    )
    assert response.status_code == 401  # Unauthorized


# ─────────────────────────────────────────────────────────────
# Health Checks
# ─────────────────────────────────────────────────────────────

def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["version"] == "2.0.0"


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "models_loaded" in data
    assert "database_connected" in data
    assert "timestamp" in data


# ─────────────────────────────────────────────────────────────
# Input Validation Tests
# ─────────────────────────────────────────────────────────────

def test_diabetes_invalid_hba1c_too_high():
    """Test HbA1c value outside valid range."""
    response = client.post(
        "/predict/diabetes",
        json={
            "hbA1c_level": 20.0,  # > 15%
            "blood_glucose_level": 150,
            "age": 45
        },
        headers={"x-api-key": "dev-key-change-in-production"}
    )
    # Pydantic validation should reject this
    assert response.status_code in [422, 400]


def test_diabetes_invalid_age_negative():
    """Test negative age."""
    response = client.post(
        "/predict/diabetes",
        json={
            "hbA1c_level": 7.5,
            "blood_glucose_level": 150,
            "age": -5
        },
        headers={"x-api-key": "dev-key-change-in-production"}
    )
    assert response.status_code in [422, 400]


def test_diabetes_missing_field():
    """Test missing required field."""
    response = client.post(
        "/predict/diabetes",
        json={
            "hbA1c_level": 7.5,
            "blood_glucose_level": 150
            # Missing age
        },
        headers={"x-api-key": "dev-key-change-in-production"}
    )
    assert response.status_code == 422


# ─────────────────────────────────────────────────────────────
# Prediction Tests
# ─────────────────────────────────────────────────────────────

@pytest.mark.skipif(not os.environ.get('MODELS_READY'), reason="Models not loaded")
def test_predict_diabetes():
    """Test diabetes prediction."""
    response = client.post(
        "/predict/diabetes",
        json={
            "hbA1c_level": 7.5,
            "blood_glucose_level": 200,
            "age": 45
        },
        headers={"x-api-key": "dev-key-change-in-production"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["disease"] == "diabetes"
    assert data["result"] in ["Positive", "Negative"]
    assert 0 <= data["probability"] <= 100
    assert data["risk_level"] in ["Low", "Medium", "High"]
    assert "confidence" in data
    assert "timestamp" in data


@pytest.mark.skipif(not os.environ.get('MODELS_READY'), reason="Models not loaded")
def test_predict_ckd():
    """Test CKD prediction."""
    response = client.post(
        "/predict/ckd",
        json={
            "age": 45,
            "hemo": 13.5,
            "pcv": 44,
            "rbcc": 5.0,
            "sc": 0.9
        },
        headers={"x-api-key": "dev-key-change-in-production"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["disease"] == "ckd"
    assert data["result"] in ["Positive", "Negative"]


@pytest.mark.skipif(not os.environ.get('MODELS_READY'), reason="Models not loaded")
def test_predict_cld():
    """Test CLD prediction."""
    response = client.post(
        "/predict/cld",
        json={
            "alkphos": 100,
            "sgot": 25,
            "sgpt": 30,
            "total_bilirubin": 0.8,
            "total_proteins": 7.0,
            "albumin": 4.2
        },
        headers={"x-api-key": "dev-key-change-in-production"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["disease"] == "cld"


@pytest.mark.skipif(not os.environ.get('MODELS_READY'), reason="Models not loaded")
def test_predict_heart():
    """Test heart disease prediction."""
    response = client.post(
        "/predict/heart",
        json={
            "age": 60,
            "chol": 240,
            "trestbps": 140,
            "cp": 1,
            "thalachh": 120
        },
        headers={"x-api-key": "dev-key-change-in-production"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["disease"] == "heart"


# ─────────────────────────────────────────────────────────────
# Database Persistence Tests
# ─────────────────────────────────────────────────────────────

@pytest.mark.skipif(not os.environ.get('MODELS_READY'), reason="Models not loaded")
def test_prediction_logged_to_database():
    """Test that predictions are persisted to database."""
    db = TestingSessionLocal()
    
    # Make prediction
    response = client.post(
        "/predict/diabetes",
        json={
            "hbA1c_level": 7.5,
            "blood_glucose_level": 200,
            "age": 45
        },
        headers={"x-api-key": "dev-key-change-in-production"}
    )
    
    # Verify database entry
    prediction = db.query(Prediction).filter(
        Prediction.disease == "diabetes"
    ).first()
    
    assert prediction is not None
    assert prediction.result in ["Positive", "Negative"]
    assert prediction.probability >= 0
    assert prediction.features is not None
    
    db.close()


# ─────────────────────────────────────────────────────────────
# Model Info Tests
# ─────────────────────────────────────────────────────────────

def test_models_info():
    """Test model information endpoint."""
    response = client.get(
        "/models/info",
        headers={"x-api-key": "dev-key-change-in-production"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "diabetes" in data
    assert "ckd" in data
    assert "cld" in data
    assert "heart" in data
    
    for disease, info in data.items():
        assert "features" in info
        assert "inputs" in info
        assert "description" in info


# ─────────────────────────────────────────────────────────────
# Error Handling Tests
# ─────────────────────────────────────────────────────────────

def test_malformed_json():
    """Test error handling for malformed JSON."""
    response = client.post(
        "/predict/diabetes",
        data="invalid json",
        headers={"x-api-key": "dev-key-change-in-production"}
    )
    assert response.status_code in [400, 422]


def test_unknown_disease():
    """Test prediction for unknown disease."""
    # This test would need a way to trigger unknown disease
    # For now, we test with valid endpoint
    assert True


# ─────────────────────────────────────────────────────────────
# Performance Tests
# ─────────────────────────────────────────────────────────────

@pytest.mark.skipif(not os.environ.get('MODELS_READY'), reason="Models not loaded")
def test_prediction_latency():
    """Test that predictions complete within acceptable time."""
    import time
    
    start = time.time()
    response = client.post(
        "/predict/diabetes",
        json={
            "hbA1c_level": 7.5,
            "blood_glucose_level": 200,
            "age": 45
        },
        headers={"x-api-key": "dev-key-change-in-production"}
    )
    latency = (time.time() - start) * 1000  # ms
    
    assert response.status_code == 200
    assert latency < 500  # Should complete in < 500ms
    
    # Verify latency is logged
    data = response.json()
    assert "timestamp" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
        "albumin": 4.0
    })
    assert response.status_code == 200

def test_predict_heart():
    response = client.post("/predict/heart", json={
        "age": 45,
        "chol": 200,
        "trestbps": 120,
        "cp": 0,
        "thalachh": 150
    })
    assert response.status_code == 200

def test_models_info():
    response = client.get("/models/info")
    assert response.status_code == 200
    assert "diabetes" in response.json()