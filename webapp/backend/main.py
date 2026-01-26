"""
Material Passport Generator API

FastAPI backend for serving ML models and generating material passports.
"""
import sys
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path for absolute imports
sys.path.insert(0, str(Path(__file__).parent))

from models.loader import ModelLoader
from services.prediction_service import PredictionService
from services.sustainability_service import SustainabilityService
from services.passport_service import PassportService
from services.mlflow_service import MLflowService
from api.routes import router as api_router
from utils.config import Settings, get_settings

# Initialize FastAPI
app = FastAPI(
    title=Settings().app_name,
    version=Settings().app_version,
    description="AI-powered material passport generation for building materials"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Settings().cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=Settings().api_prefix)


@app.on_event("startup")
async def startup_event():
    """Initialize all services on application startup"""
    print("=" * 60)
    print("Starting Material Passport Generator API...")
    print("=" * 60)
    
    # Load settings
    settings = get_settings()
    print(f"App: {settings.app_name} v{settings.app_version}")
    print(f"API Prefix: {settings.api_prefix}")
    print(f"Host: {settings.host}:{settings.port}")
    print(f"MLflow: {settings.mlflow_enabled}")
    print("=" * 60)
    
    try:
        # Initialize MLflow service
        mlflow_service = MLflowService(
            experiment_name=settings.mlflow_experiment_name
        )
        print("✓ MLflow service initialized")
        
        # Initialize model loader
        model_loader = ModelLoader()
        models_loaded = model_loader.load_all_models(settings.models_dir)
        print(f"✓ Models loaded: {len(model_loader.get_available_models())} models")
        
        # Initialize prediction service
        prediction_service = PredictionService(
            model_loader=model_loader,
            mlflow_service=mlflow_service
        )
        print("✓ Prediction service initialized")
        
        # Initialize sustainability service
        sustainability_service = SustainabilityService()
        print("✓ Sustainability service initialized")
        
        # Initialize passport service
        passport_service = PassportService(
            prediction_service=prediction_service,
            sustainability_service=sustainability_service,
            mlflow_service=mlflow_service
        )
        print("✓ Passport service initialized")
        
        # Set global services for API routes
        import api.routes as routes
        routes.init_services(
            loader=model_loader,
            pred_svc=prediction_service,
            sust_svc=sustainability_service,
            pass_svc=passport_service,
            mlflow_svc=mlflow_service
        )
        
        print("=" * 60)
        print("✓ All services initialized successfully")
        print("=" * 60)
        print(f"\nAPI Documentation: http://{settings.host}:{settings.port}{settings.api_prefix}/docs")
        print(f"Health Check: http://{settings.host}:{settings.port}{settings.api_prefix}/health")
        print("=" * 60)
    
    except Exception as e:
        print("=" * 60)
        print("✗ Failed to initialize services")
        print(f"Error: {e}")
        print("=" * 60)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    settings = get_settings()
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "healthy",
        "endpoints": {
            "health": f"{settings.api_prefix}/health",
            "models": f"{settings.api_prefix}/models",
            "docs": f"{settings.api_prefix}/docs"
        },
        "message": "Backend API is running. Use Swagger UI at /api/v1/docs for interactive testing."
    }


if __name__ == "__main__":
    # Run the API server
    import uvicorn
    settings = get_settings()
    
    print("=" * 60)
    print("Material Passport Generator API")
    print("=" * 60)
    print(f"Server: {settings.app_name} v{settings.app_version}")
    print(f"Host: {settings.host}:{settings.port}")
    print(f"Docs: http://{settings.host}:{settings.port}{settings.api_prefix}/docs")
    print("=" * 60)
    
    # Run server with auto-reload for development
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="info"
    )
