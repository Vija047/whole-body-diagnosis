from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
import mlflow
import mlflow.sklearn
import warnings
warnings.filterwarnings('ignore')

app = FastAPI(
    title="Whole Body Diagnosis API",
    description="AI-powered disease screening API",
    version="1.0.0"
)

# ── Load models ───────────────────────────────────────────────────
models  = {}
scalers = {}
diseases = ['diabetes', 'ckd', 'cld', 'heart']

for d in diseases:
    models[d]  = joblib.load(f'models/{d}_model.pkl')
    scalers[d] = joblib.load(f'models/{d}_scaler.pkl')

print("All models loaded ✅")

# ── Input schemas ─────────────────────────────────────────────────
class DiabetesInput(BaseModel):
    hbA1c_level: float
    blood_glucose_level: float
    age: float

class CKDInput(BaseModel):
    age: float
    hemo: float
    pcv: float
    rbcc: float
    sc: float

class CLDInput(BaseModel):
    alkphos: float
    sgot: float
    sgpt: float
    total_bilirubin: float
    total_proteins: float
    albumin: float

class HeartInput(BaseModel):
    age: float
    chol: float
    trestbps: float
    cp: float
    thalachh: float

# ── Predict helper ────────────────────────────────────────────────
def predict(disease, features, feature_names):
    arr    = pd.DataFrame([features], columns=feature_names)
    arr_s  = scalers[disease].transform(arr)
    pred   = models[disease].predict(arr_s)[0]
    prob   = models[disease].predict_proba(arr_s)[0][1]
    result = 'Positive' if pred == 1 else 'Negative'
    return {
        "disease": disease,
        "result": result,
        "probability": round(float(prob) * 100, 1),
        "risk_level": "High" if prob > 0.6 else "Medium" if prob > 0.4 else "Low"
    }

# ── Routes ────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "Whole Body Diagnosis API", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy", "models_loaded": list(models.keys())}

@app.post("/predict/diabetes")
def predict_diabetes(data: DiabetesInput):
    features = [data.hbA1c_level, data.blood_glucose_level, data.age]
    names    = ['hbA1c_level', 'blood_glucose_level', 'age']
    return predict('diabetes', features, names)

@app.post("/predict/ckd")
def predict_ckd(data: CKDInput):
    features = [data.age, data.hemo, data.pcv, data.rbcc, data.sc]
    names    = ['age', 'hemo', 'pcv', 'rbcc', 'sc']
    return predict('ckd', features, names)

@app.post("/predict/cld")
def predict_cld(data: CLDInput):
    features = [data.alkphos, data.sgot, data.sgpt,
                data.total_bilirubin, data.total_proteins, data.albumin]
    names    = ['alkphos', 'sgot', 'sgpt',
                'total_bilirubin', 'total_proteins', 'albumin']
    return predict('cld', features, names)

@app.post("/predict/heart")
def predict_heart(data: HeartInput):
    features = [data.age, data.chol, data.trestbps, data.cp, data.thalachh]
    names    = ['age', 'chol', 'trestbps', 'cp', 'thalachh']
    return predict('heart', features, names)

@app.get("/models/info")
def models_info():
    return {
        "diabetes": {"features": 3, "inputs": "hbA1c, glucose, age"},
        "ckd":      {"features": 5, "inputs": "age, hemo, pcv, rbcc, sc"},
        "cld":      {"features": 6, "inputs": "alkphos, sgot, sgpt, bilirubin, proteins, albumin"},
        "heart":    {"features": 5, "inputs": "age, chol, trestbps, cp, thalachh"}
    }