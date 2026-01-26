"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime

class MaterialComposition(BaseModel):
    """Material composition input"""
    cement: float = Field(..., gt=0, description="Cement in kg/m³")
    blast_furnace_slag: float = Field(0, ge=0, description="Blast Furnace Slag in kg/m³")
    fly_ash: float = Field(0, ge=0, description="Fly Ash in kg/m³")
    water: float = Field(..., gt=0, description="Water in kg/m³")
    superplasticizer: float = Field(0, ge=0, description="Superplasticizer in kg/m³")
    coarse_aggregate: float = Field(..., gt=0, description="Coarse Aggregate in kg/m³")
    fine_aggregate: float = Field(..., gt=0, description="Fine Aggregate in kg/m³")
    age: int = Field(..., gt=0, description="Age in days")

class PredictionRequest(BaseModel):
    """Request for generating a passport"""
    composition: MaterialComposition
    model_name: Optional[str] = Field("xgboost", description="Model name (default: xgboost)")

class Prediction(BaseModel):
    """Model prediction result"""
    value: float
    unit: str = Field(default="MPa", description="Unit of prediction")
    confidence: float = Field(default=0.85, ge=0, le=1, description="Confidence score 0-1")
    model: str = Field(..., description="Model name used")

class Recyclability(BaseModel):
    """Recyclability prediction result"""
    score: int = Field(..., ge=0, le=100, description="Recyclability score 0-100")
    grade: str = Field(..., description="Sustainability grade A-F")
    model: str = Field(..., description="Model name used")

class Predictions(BaseModel):
    """All predictions"""
    compressive_strength: Prediction
    recyclability: Recyclability

class RecycledContent(BaseModel):
    """Recycled content information"""
    percentage: float = Field(..., ge=0, le=100, description="Percentage of recycled content")
    materials: List[str] = Field(default_factory=list, description="List of recycled materials")

class SustainabilityMetrics(BaseModel):
    """Sustainability metrics"""
    circularity_score: int = Field(..., ge=0, le=100, description="Circularity score 0-100")
    co2_emissions: Dict[str, float] = Field(..., description="CO2 emissions")
    recycled_content: RecycledContent
    sustainability_grade: str = Field(..., description="Sustainability grade A-F")

class Passport(BaseModel):
    """Complete material passport"""
    id: str = Field(..., description="Unique passport ID")
    material_type: str = Field(default="Concrete", description="Material type")
    composition: MaterialComposition
    predictions: Predictions
    sustainability_metrics: SustainabilityMetrics
    certification: str = Field(default="Circular Economy Compliant", description="Certification status")
    generated_at: str = Field(..., description="Generation timestamp")
    qr_code_url: str = Field(..., description="QR code URL")

class ModelPerformance(BaseModel):
    """Model performance metrics"""
    r2: float = Field(..., description="R² score")
    rmse: float = Field(..., description="RMSE")
    mae: Optional[float] = Field(None, description="MAE if available")

class ModelInfo(BaseModel):
    """Available model information"""
    name: str = Field(..., description="Model name")
    type: str = Field(..., description="Model type (regression, neural_network)")
    description: str = Field(..., description="Model description")
    performance: ModelPerformance = Field(..., description="Performance metrics")
    features: str = Field(..., description="Feature set used")
    best_for_production: bool = Field(default=False, description="Recommended for production")

class ModelsResponse(BaseModel):
    """Response with all available models"""
    models: List[ModelInfo]

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(default="healthy", description="Service status")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(..., description="API version")
