"""
Configuration management for the API.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Configuration
    app_name: str = "Material Passport Generator API"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "https://*.vercel.app", "https://*.onrender.com"]
    
    # Model paths (relative to backend directory)
    models_dir: str = "../../models"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # MLflow configuration
    mlflow_enabled: bool = True
    mlflow_tracking_uri: str = "../../mlruns"
    mlflow_experiment_name: str = "material-passport-production"
    
    # Production model (best performing model)
    default_model: str = "xgboost"
    
    # PDF generation
    passport_title: str = "Digital Material Passport"
    passport_author: str = "Material Passport Generator"
    
    # QR code base URL
    qr_code_base_url: str = "https://material-passport.app/passport/"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()
