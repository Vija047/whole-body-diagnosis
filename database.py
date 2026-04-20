"""
Database models for storing predictions and audit logs.
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool
from config import get_settings

settings = get_settings()

Base = declarative_base()


class Prediction(Base):
    """Store all predictions for audit trail and performance tracking."""
    
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    disease = Column(String(50), index=True, nullable=False)
    result = Column(String(20), nullable=False)  # Positive/Negative
    probability = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)  # Low/Medium/High
    features = Column(JSON, nullable=False)  # Input features
    actual_result = Column(String(20), nullable=True)  # Ground truth (optional)
    model_version = Column(String(50), nullable=True)
    latency_ms = Column(Float, nullable=False)  # Request latency
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    client_id = Column(String(100), nullable=True)  # For tracking clients


class ModelMetadata(Base):
    """Track deployed model versions and performance."""
    
    __tablename__ = "model_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    disease = Column(String(50), index=True, nullable=False, unique=True)
    model_version = Column(String(50), nullable=False)
    accuracy = Column(Float, nullable=False)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    f1_score = Column(Float, nullable=False)
    auc_score = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    deployed_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DriftAlert(Base):
    """Log data drift detections."""
    
    __tablename__ = "drift_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    disease = Column(String(50), index=True, nullable=False)
    drift_score = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    retraining_triggered = Column(Boolean, default=False)
    retraining_completed = Column(Boolean, default=False)
    notes = Column(String(500), nullable=True)


# Database setup
def get_database_url():
    """Get database URL, defaulting to SQLite for dev."""
    url = settings.DATABASE_URL
    
    # For SQLite, create directory if needed
    if url.startswith("sqlite"):
        db_path = url.replace("sqlite:///", "")
        import os
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    
    return url


engine_args = {
    "echo": settings.DEBUG
}

if not settings.DATABASE_URL.startswith("sqlite"):
    engine_args["poolclass"] = QueuePool
    engine_args["pool_size"] = settings.DB_POOL_SIZE
    engine_args["max_overflow"] = settings.DB_MAX_OVERFLOW

engine = create_engine(
    get_database_url(),
    **engine_args
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create database tables."""
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully!")
