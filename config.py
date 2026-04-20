"""
Configuration management for the ML Ops system.
Loads settings from environment variables with sensible defaults.
"""

import os
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration from environment variables."""
    
    # API Settings
    API_HOST: str = Field(default="0.0.0.0", description="API host")
    API_PORT: int = Field(default=8000, description="API port")
    API_KEY: str = Field(default="dev-key-change-in-production", description="API key for authentication")
    DEBUG: bool = Field(default=False, description="Debug mode")
    ALLOWED_ORIGINS: str = Field(default="*", description="CORS allowed origins (comma-separated)")


    
    # Model Paths
    MODELS_DIR: str = Field(default="models", description="Directory containing model files")
    DATA_DIR: str = Field(default="data", description="Directory containing data files")
    
    # Drift Detection
    DRIFT_THRESHOLD: float = Field(default=0.30, description="Drift threshold for retraining (0-1)")
    DRIFT_CHECK_INTERVAL: int = Field(default=3600, description="Drift check interval in seconds")
    
    # Database (PostgreSQL for production)
    DATABASE_URL: str = Field(
        default="sqlite:///./predictions.db",
        description="Database connection string"
    )
    DB_POOL_SIZE: int = Field(default=20, description="Database connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=10, description="Database max overflow connections")
    
    # MLflow
    MLFLOW_TRACKING_URI: str = Field(default="http://localhost:5001", description="MLflow tracking server")
    MLFLOW_REGISTRY_URI: str = Field(default="sqlite:///./mlflow.db", description="MLflow registry database")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_DIR: str = Field(default="logs", description="Log directory")
    
    # Testing
    TESTING: bool = Field(default=False, description="Testing mode")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


if __name__ == "__main__":
    settings = get_settings()
    print("Configuration loaded successfully:")
    for key, value in settings.dict().items():
        if "key" in key.lower() or "password" in key.lower() or "url" in key.lower():
            print(f"  {key}: ***")
        else:
            print(f"  {key}: {value}")
