"""
Production-grade FastAPI for disease prediction.

Features:
- Error handling with proper HTTP status codes
- API key authentication
- Request/response logging
- Prediction persistence
- Input validation with bounds checking
- Model integrity checks
"""

import time
import os
import sys
from datetime import datetime
from functools import lru_cache

from fastapi import FastAPI, HTTPException, Depends, status, Header, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator, ConfigDict
import joblib
import numpy as np
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from config import get_settings
from logger import app_logger, pred_logger
from database import get_db, init_db, Prediction, ModelMetadata

settings = get_settings()

# Initialize database
init_db()

app = FastAPI(
    title="Whole Body Diagnosis API",
    description="Production ML Ops API for multi-disease diagnosis",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

@app.get("/debug/info")
def debug_info():
    import sklearn
    import numpy
    import joblib
    return {
        "numpy_version": numpy.__version__,
        "sklearn_version": sklearn.__version__,
        "joblib_version": joblib.__version__,
        "python_version": os.sys.version
    }


@app.get("/")
def root():
    return {"status": "ok", "message": "Whole Body Diagnosis API is running"}


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),


    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────
# Authentication
# ─────────────────────────────────────────────────────────────────

def verify_api_key(x_api_key: str = Header(...)) -> str:
    """Verify API key from request header."""
    if x_api_key.strip() != settings.API_KEY.strip():
        app_logger.warning(f"Unauthorized API key attempt: {x_api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return x_api_key


# ─────────────────────────────────────────────────────────────────
# Model Management
# ─────────────────────────────────────────────────────────────────

# Global cache for models and scalers
MODEL_CACHE = {}
SCALER_CACHE = {}


def _install_numpy_pickle_compat_aliases() -> None:
    """Install module aliases so NumPy 2.x pickles can load on NumPy 1.x runtimes."""
    if hasattr(np, "core"):
        sys.modules.setdefault("numpy._core", np.core)
        if hasattr(np.core, "multiarray"):
            sys.modules.setdefault("numpy._core.multiarray", np.core.multiarray)
        if hasattr(np.core, "numeric"):
            sys.modules.setdefault("numpy._core.numeric", np.core.numeric)
        if hasattr(np.core, "numerictypes"):
            sys.modules.setdefault("numpy._core.numerictypes", np.core.numerictypes)

def get_model_and_scaler(disease: str):
    """Lazy load and cache a specific model and scaler."""
    if disease in MODEL_CACHE and disease in SCALER_CACHE:
        return MODEL_CACHE[disease], SCALER_CACHE[disease]
    
    # Use absolute path to avoid CWD issues
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(base_dir, settings.MODELS_DIR)
    
    model_path = os.path.join(models_dir, f'{disease}_model.pkl')
    scaler_path = os.path.join(models_dir, f'{disease}_scaler.pkl')
    
    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        app_logger.error(f"❌ Files missing for {disease}: {model_path} or {scaler_path}")
        raise FileNotFoundError(f"Model or scaler not found for {disease}")
    
    try:
        app_logger.info(f"🧠 Loading {disease} model into memory...")
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
    except ModuleNotFoundError as e:
        if "numpy._core" not in str(e):
            app_logger.error(f"❌ Failed to load {disease} model: {str(e)}")
            raise

        app_logger.warning(
            "Detected NumPy pickle compatibility issue (numpy._core). "
            "Applying compatibility aliases and retrying model load."
        )
        _install_numpy_pickle_compat_aliases()
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        
    # Cache them
    MODEL_CACHE[disease] = model
    SCALER_CACHE[disease] = scaler
    app_logger.info(f"✅ {disease} model loaded successfully")
    
    return model, scaler


# No longer load all on startup to save memory on Render Free tier
MODELS_READY = True  # We'll handle individual failures in the routes
STARTUP_ERROR = None


# ─────────────────────────────────────────────────────────────────
# Input Schemas with Validation
# ─────────────────────────────────────────────────────────────────

class DiabetesInput(BaseModel):
    """Diabetes prediction input with validated ranges."""
    hbA1c_level: float = Field(..., ge=4.0, le=15.0, description="HbA1c level (4-15%)")
    blood_glucose_level: float = Field(..., ge=70, le=400, description="Blood glucose (70-400 mg/dL)")
    age: float = Field(..., ge=1, le=120, description="Age (1-120 years)")
    
    @validator('*')
    def check_not_nan(cls, v):
        if v is None or (isinstance(v, float) and np.isnan(v)):
            raise ValueError("Value cannot be NaN")
        return v


class CKDInput(BaseModel):
    """Chronic Kidney Disease input."""
    age: float = Field(..., ge=1, le=120, description="Age (1-120 years)")
    hemo: float = Field(..., ge=3.0, le=20.0, description="Hemoglobin (3-20 g/dL)")
    pcv: float = Field(..., ge=10, le=55, description="Packed cell volume (10-55%)")
    rbcc: float = Field(..., ge=2.0, le=8.0, description="Red blood cell count (2-8 millions/µL)")
    sc: float = Field(..., ge=0.5, le=10.0, description="Serum creatinine (0.5-10 mg/dL)")


class CLDInput(BaseModel):
    """Chronic Liver Disease input."""
    alkphos: float = Field(..., ge=30, le=500, description="Alkaline phosphatase (30-500 U/L)")
    sgot: float = Field(..., ge=10, le=300, description="SGOT enzyme (10-300 U/L)")
    sgpt: float = Field(..., ge=5, le=300, description="SGPT enzyme (5-300 U/L)")
    total_bilirubin: float = Field(..., ge=0.1, le=20.0, description="Total bilirubin (0.1-20 mg/dL)")
    total_proteins: float = Field(..., ge=4.0, le=10.0, description="Total proteins (4-10 g/dL)")
    albumin: float = Field(..., ge=2.0, le=6.0, description="Albumin (2-6 g/dL)")


class HeartInput(BaseModel):
    """Heart disease prediction input."""
    age: float = Field(..., ge=1, le=120, description="Age (1-120 years)")
    chol: float = Field(..., ge=100, le=400, description="Cholesterol (100-400 mg/dL)")
    trestbps: float = Field(..., ge=80, le=200, description="Resting BP (80-200 mmHg)")
    cp: float = Field(..., ge=0, le=3, description="Chest pain type (0-3)")
    thalachh: float = Field(..., ge=60, le=220, description="Max heart rate (60-220 bpm)")


# ─────────────────────────────────────────────────────────────────
# Response Schemas
# ─────────────────────────────────────────────────────────────────

class PredictionResponse(BaseModel):
    """Standard prediction response."""
    disease: str
    result: str  # Positive/Negative
    probability: float  # 0-100
    risk_level: str  # Low/Medium/High
    confidence: str
    model_version: str
    timestamp: datetime
    
    model_config = ConfigDict(protected_namespaces=(), from_attributes=True)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    models_loaded: list
    database_connected: bool
    version: str


# ─────────────────────────────────────────────────────────────────
# Prediction Logic
# ─────────────────────────────────────────────────────────────────

def make_prediction(
    disease: str,
    features: list,
    feature_names: list,
    db: Session,
    client_id: str = None
) -> dict:
    """
    Make a prediction and log it to database.
    
    Args:
        disease: Disease type
        features: Feature values
        feature_names: Feature names
        db: Database session
        client_id: Client identifier for tracking
    
    Returns:
        Prediction result
    """
    start_time = time.time()
    
    try:
        # Lazy load model and scaler
        model, scaler = get_model_and_scaler(disease)
        
        # Prepare input
        arr = pd.DataFrame([features], columns=feature_names)
        arr_scaled = scaler.transform(arr)
        
        # Get prediction
        pred_class = model.predict(arr_scaled)[0]
        pred_proba = model.predict_proba(arr_scaled)[0][1]
        
        # Determine result
        result = 'Positive' if pred_class == 1 else 'Negative'
        probability = round(float(pred_proba) * 100, 2)
        
        # Risk stratification
        if pred_proba > 0.7:
            risk_level = "High"
            confidence = "Very High"
        elif pred_proba > 0.5:
            risk_level = "High"
            confidence = "High"
        elif pred_proba > 0.4:
            risk_level = "Medium"
            confidence = "Medium"
        else:
            risk_level = "Low"
            confidence = "Low"
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Get model version from database
        model_meta = db.query(ModelMetadata).filter(
            ModelMetadata.disease == disease,
            ModelMetadata.is_active == True
        ).first()
        model_version = model_meta.model_version if model_meta else "1.0"
        
        # Log to database
        prediction_record = Prediction(
            disease=disease,
            result=result,
            probability=probability,
            risk_level=risk_level,
            features=dict(zip(feature_names, features)),
            model_version=model_version,
            latency_ms=latency_ms,
            client_id=client_id
        )
        db.add(prediction_record)
        db.commit()
        
        # Audit log
        pred_logger.info(
            f"Prediction | Disease: {disease} | Result: {result} | "
            f"Prob: {probability}% | Risk: {risk_level} | Latency: {latency_ms:.2f}ms | "
            f"Client: {client_id}"
        )
        
        return {
            "disease": disease,
            "result": result,
            "probability": probability,
            "risk_level": risk_level,
            "confidence": confidence,
            "model_version": model_version,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        app_logger.error(f"Prediction error for {disease}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


# ─────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint."""
    return {
        "message": "Whole Body Diagnosis API",
        "version": "2.0.0",
        "docs": "/api/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.
    
    Returns:
        - status: API status
        - models_loaded: Available models
        - database_connected: Database connectivity
    """
    try:
        # Check database (using text() for SQLAlchemy 2.0 compatibility)
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        app_logger.error(f"Database health check failed: {str(e)}")
        db_ok = False
    
    return HealthResponse(
        status="healthy" if db_ok else "degraded",
        timestamp=datetime.utcnow(),
        models_loaded=list(MODEL_CACHE.keys()),
        database_connected=db_ok,
        version="2.0.0"
    )


@app.post("/predict/diabetes", response_model=PredictionResponse, tags=["Predictions"])
async def predict_diabetes(
    data: DiabetesInput,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
    x_client_id: str = Header(None)
):
    """Predict diabetes likelihood."""
    try:
        features = [data.hbA1c_level, data.blood_glucose_level, data.age]
        names = ['hbA1c_level', 'blood_glucose_level', 'age']
        result = make_prediction('diabetes', features, names, db, x_client_id)
        return PredictionResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Diabetes prediction failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Model failed to load or predict. Error: {str(e)}" if settings.DEBUG else "Diagnosis service temporarily unavailable"
        )


@app.post("/predict/ckd", response_model=PredictionResponse, tags=["Predictions"])
async def predict_ckd(
    data: CKDInput,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
    x_client_id: str = Header(None)
):
    """Predict Chronic Kidney Disease likelihood."""
    try:
        features = [data.age, data.hemo, data.pcv, data.rbcc, data.sc]
        names = ['age', 'hemo', 'pcv', 'rbcc', 'sc']
        result = make_prediction('ckd', features, names, db, x_client_id)
        return PredictionResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"CKD prediction failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Model failed to load or predict. Error: {str(e)}" if settings.DEBUG else "Diagnosis service temporarily unavailable"
        )


@app.post("/predict/cld", response_model=PredictionResponse, tags=["Predictions"])
async def predict_cld(
    data: CLDInput,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
    x_client_id: str = Header(None)
):
    """Predict Chronic Liver Disease likelihood."""
    try:
        features = [data.alkphos, data.sgot, data.sgpt, data.total_bilirubin, 
                    data.total_proteins, data.albumin]
        names = ['alkphos', 'sgot', 'sgpt', 'total_bilirubin', 'total_proteins', 'albumin']
        result = make_prediction('cld', features, names, db, x_client_id)
        return PredictionResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"CLD prediction failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Model failed to load or predict. Error: {str(e)}" if settings.DEBUG else "Diagnosis service temporarily unavailable"
        )


@app.post("/predict/heart", response_model=PredictionResponse, tags=["Predictions"])
async def predict_heart(
    data: HeartInput,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
    x_client_id: str = Header(None)
):
    """Predict Heart Disease likelihood."""
    try:
        features = [data.age, data.chol, data.trestbps, data.cp, data.thalachh]
        names = ['age', 'chol', 'trestbps', 'cp', 'thalachh']
        result = make_prediction('heart', features, names, db, x_client_id)
        return PredictionResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Heart prediction failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Model failed to load or predict. Error: {str(e)}" if settings.DEBUG else "Diagnosis service temporarily unavailable"
        )


@app.get("/models/info", tags=["Models"])
async def models_info(api_key: str = Depends(verify_api_key)):
    """Get information about available models."""
    return {
        "diabetes": {
            "features": 3,
            "inputs": ["hbA1c_level", "blood_glucose_level", "age"],
            "description": "Type 2 Diabetes prediction from lab and demographic data"
        },
        "ckd": {
            "features": 5,
            "inputs": ["age", "hemo", "pcv", "rbcc", "sc"],
            "description": "Chronic Kidney Disease prediction from lab values"
        },
        "cld": {
            "features": 6,
            "inputs": ["alkphos", "sgot", "sgpt", "total_bilirubin", "total_proteins", "albumin"],
            "description": "Chronic Liver Disease prediction from liver function tests"
        },
        "heart": {
            "features": 5,
            "inputs": ["age", "chol", "trestbps", "cp", "thalachh"],
            "description": "Heart Disease prediction from cardiovascular metrics"
        }
    }


# ─────────────────────────────────────────────────────────────────
# Error Handlers
# ─────────────────────────────────────────────────────────────────

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle validation errors."""
    app_logger.warning(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    app_logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    app_logger.info(f"Starting API on {settings.API_HOST}:{settings.API_PORT}")
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )