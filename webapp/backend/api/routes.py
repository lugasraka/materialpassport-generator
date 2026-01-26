"""
API route definitions for Material Passport Generator.
"""
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Dict
from datetime import datetime
from uuid import uuid4

from .schemas import (
    PredictionRequest, Passport, ModelsResponse, HealthResponse,
    ModelInfo, PredictionRequest
)
from ..services.prediction_service import PredictionService
from ..services.sustainability_service import SustainabilityService
from ..services.passport_service import PassportService
from ..services.mlflow_service import MLflowService
from ..models.loader import ModelLoader
from ..utils.qr_generator import generate_qr_code
from ..utils.pdf_generator import generate_passport_pdf

router = APIRouter(prefix="/api/v1", tags=["passport"])

# Global services (will be initialized in main.py)
model_loader = None
prediction_service = None
sustainability_service = None
passport_service = None
mlflow_service = None

def init_services(loader, pred_svc, sust_svc, pass_svc, mlflow_svc):
    """Initialize services - called from main.py"""
    global model_loader, prediction_service, sustainability_service, passport_service, mlflow_service
    model_loader = loader
    prediction_service = pred_svc
    sustainability_service = sust_svc
    passport_service = pass_svc
    mlflow_service = mlflow_svc

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat() + "Z",
        version="1.0.0"
    )

@router.get("/models", response_model=ModelsResponse)
async def get_models():
    """List all available prediction models with performance metrics"""
    try:
        models = []
        
        for model_name in model_loader.get_available_models():
            metadata = model_loader.get_model_metadata(model_name)
            
            model_info = ModelInfo(
                name=model_name,
                type=_get_model_type(model_name),
                description=_get_model_description(model_name),
                performance=ModelPerformance(
                    r2=metadata.get("test_r2", 0.0),
                    rmse=metadata.get("test_rmse", 0.0),
                    mae=metadata.get("test_mae", None)
                ),
                features=metadata.get("features", "8 original"),
                best_for_production=metadata.get("best_for_production", False)
            )
            
            # Mark best model
            if model_name == "xgboost":
                model_info.best_for_production = True
        
        return ModelsResponse(models=models)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get models: {str(e)}"
        )

@router.post("/passport/generate", response_model=Passport, status_code=status.HTTP_201_CREATED)
async def generate_passport(request: PredictionRequest):
    """Generate a new material passport"""
    try:
        # Generate passport
        start_time = datetime.utcnow()
        passport = passport_service.generate_passport(
            request.composition.dict(),
            request.model_name
        )
        end_time = datetime.utcnow()
        processing_time_ms = (end_time - start_time).total_seconds() * 1000
        
        # Log to MLflow
        mlflow_service.log_passport_generation(
            model_name=request.model_name,
            processing_time_ms=processing_time_ms,
            passport_id=passport["id"],
            success=True
        )
        
        return passport
    
    except ValueError as e:
        # Log error to MLflow
        mlflow_service.log_passport_generation(
            model_name=request.model_name,
            processing_time_ms=0,
            passport_id="",
            success=False
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}"
        )
    
    except Exception as e:
        # Log error to MLflow
        mlflow_service.log_error(
            model_name=request.model_name,
            error_type="generation_error",
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate passport: {str(e)}"
        )

@router.get("/passport/{passport_id}", response_model=Passport)
async def get_passport(passport_id: str):
    """Retrieve a previously generated passport by ID"""
    try:
        passport = passport_service.get_passport(passport_id)
        
        if passport is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Passport not found: {passport_id}"
            )
        
        return passport
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve passport: {str(e)}"
        )

@router.get("/passport/{passport_id}/pdf")
async def download_passport_pdf(passport_id: str):
    """Download passport as PDF document"""
    try:
        passport = passport_service.get_passport(passport_id)
        
        if passport is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Passport not found: {passport_id}"
            )
        
        # Generate PDF
        pdf_bytes = generate_passport_pdf(passport)
        
        # Return as streaming response
        filename = f"material_passport_{passport_id}.pdf"
        return StreamingResponse(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}"
        )

@router.get("/passport/{passport_id}/qr")
async def get_qr_code(passport_id: str):
    """Get QR code image for passport verification"""
    try:
        passport = passport_service.get_passport(passport_id)
        
        if passport is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Passport not found: {passport_id}"
            )
        
        # Generate QR code
        qr_bytes = generate_qr_code(passport_id, "https://material-passport.app/passport/")
        
        return StreamingResponse(
            content=qr_bytes,
            media_type="image/png",
            headers={
                "Content-Type": "image/png"
            }
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate QR code: {str(e)}"
        )

@router.post("/predict")
async def predict_raw(request: PredictionRequest):
    """Raw prediction endpoint for developers - no passport generation"""
    try:
        strength_prediction = prediction_service.predict_strength(
            request.composition.dict(),
            request.model_name
        )
        
        recyclability_prediction = prediction_service.predict_recyclability(
            request.composition.dict()
        )
        
        return {
            "strength": strength_prediction,
            "recyclability": recyclability_prediction
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )

def _get_model_type(model_name: str) -> str:
    """Get model type for a given model name"""
    if model_name in ["linear_regression", "random_forest", "xgboost"]:
        return "regression"
    elif model_name in ["simple_nn", "deep_nn", "multitask_nn"]:
        return "neural_network"
    else:
        return "unknown"

def _get_model_description(model_name: str) -> str:
    """Get description for a given model name"""
    descriptions = {
        "linear_regression": "Linear Regression model for compressive strength",
        "random_forest": "Random Forest ensemble model",
        "xgboost": "Gradient Boosted Trees (Best Production Model)",
        "simple_nn": "Simple Feedforward Neural Network",
        "deep_nn": "Deep Neural Network with more layers",
        "multitask_nn": "Multi-task learning (strength + recyclability)"
    }
    return descriptions.get(model_name, "Model for concrete strength prediction")
