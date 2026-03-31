import pytest
import sys
sys.path.append('.')
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_predict_diabetes_positive():
    response = client.post("/predict/diabetes", json={
        "hbA1c_level": 7.5,
        "blood_glucose_level": 200,
        "age": 45
    })
    assert response.status_code == 200
    assert response.json()["result"] in ["Positive", "Negative"]
    assert 0 <= response.json()["probability"] <= 100

def test_predict_diabetes_negative():
    response = client.post("/predict/diabetes", json={
        "hbA1c_level": 4.5,
        "blood_glucose_level": 90,
        "age": 25
    })
    assert response.status_code == 200
    assert response.json()["result"] == "Negative"

def test_predict_ckd():
    response = client.post("/predict/ckd", json={
        "age": 45,
        "hemo": 13.5,
        "pcv": 44,
        "rbcc": 5.0,
        "sc": 0.9
    })
    assert response.status_code == 200
    assert response.json()["result"] in ["Positive", "Negative"]

def test_predict_cld():
    response = client.post("/predict/cld", json={
        "alkphos": 100,
        "sgot": 25,
        "sgpt": 30,
        "total_bilirubin": 0.8,
        "total_proteins": 7.0,
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