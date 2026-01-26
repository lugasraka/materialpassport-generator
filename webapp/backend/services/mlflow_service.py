"""
MLflow production logging service.
Compatible with existing MLflow configuration from src/mlflow_config.py
"""
import os
import json
from typing import Dict, Any

# Import MLflow with compatibility handling
try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    print("⚠ MLflow not available - logging disabled")

class MLflowService:
    """Service for logging production predictions to MLflow"""
    
    def __init__(self, experiment_name: str = "material-passport-production"):
        """Initialize MLflow service for production logging"""
        self.experiment_name = experiment_name
        self.enabled = os.getenv("MLFLOW_ENABLED", "true").lower() == "true"
        
        if not MLFLOW_AVAILABLE:
            self.enabled = False
            print("⚠ MLflow not installed - logging disabled")
            return
        
        # Set MLflow tracking URI from environment or use default
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "../../mlruns")
        
        if self.enabled:
            try:
                mlflow.set_tracking_uri(tracking_uri)
                # Create or get experiment
                mlflow.set_experiment(experiment_name)
                print(f"✓ MLflow service initialized: {experiment_name}")
            except Exception as e:
                print(f"⚠ Failed to initialize MLflow: {e}")
                self.enabled = False
        else:
            print("⚠ MLflow logging disabled")
    
    def log_prediction(self, model_name: str, input_features: Dict,
                      prediction: Any, prediction_type: str):
        """Log a prediction to MLflow for production monitoring"""
        if not self.enabled or not MLFLOW_AVAILABLE:
            return
        
        try:
            with mlflow.start_run(run_name=f"{model_name}_{prediction_type}_prod"):
                # Log input features
                for feature_name, value in input_features.items():
                    mlflow.log_param(f"input_{feature_name}", value)
                
                # Log model info
                mlflow.log_param("model_name", model_name)
                mlflow.log_param("prediction_type", prediction_type)
                mlflow.set_tag("environment", "production")
                
                # Log prediction output
                if isinstance(prediction, (int, float)):
                    mlflow.log_metric("prediction_value", float(prediction))
                elif isinstance(prediction, (list, tuple)) and len(prediction) > 0:
                    mlflow.log_metric("prediction_value", float(prediction[0]))
                elif isinstance(prediction, dict):
                    for key, value in prediction.items():
                        if isinstance(value, (int, float)):
                            mlflow.log_metric(f"prediction_{key}", float(value))
                
                print(f"✓ Logged {model_name} {prediction_type} prediction to MLflow")
        except Exception as e:
            print(f"⚠ Failed to log prediction to MLflow: {e}")
    
    def log_model_performance(self, model_name: str, metrics: Dict[str, float]):
        """Log performance metrics for production models"""
        if not self.enabled or not MLFLOW_AVAILABLE:
            return
        
        try:
            with mlflow.start_run(run_name=f"{model_name}_performance"):
                mlflow.log_params({"model_name": model_name})
                for key, value in metrics.items():
                    mlflow.log_metric(key, value)
                mlflow.set_tag("environment", "production")
                print(f"✓ Logged {model_name} performance metrics to MLflow")
        except Exception as e:
            print(f"⚠ Failed to log model performance to MLflow: {e}")
    
    def log_error(self, model_name: str, error_type: str, error_message: str):
        """Log prediction errors for monitoring"""
        if not self.enabled or not MLFLOW_AVAILABLE:
            return
        
        try:
            with mlflow.start_run(run_name=f"{model_name}_error"):
                mlflow.log_params({
                    "model_name": model_name,
                    "error_type": error_type
                })
                mlflow.set_tag("error", error_message)
                mlflow.set_tag("environment", "production")
                print(f"✓ Logged {model_name} error to MLflow: {error_type}")
        except Exception as e:
            print(f"⚠ Failed to log error to MLflow: {e}")
    
    def log_passport_generation(self, model_name: str, processing_time_ms: float,
                             passport_id: str, success: bool):
        """Log passport generation event"""
        if not self.enabled or not MLFLOW_AVAILABLE:
            return
        
        try:
            with mlflow.start_run(run_name="passport_generation"):
                mlflow.log_param("model_name", model_name)
                mlflow.log_metric("processing_time_ms", processing_time_ms)
                mlflow.log_metric("success", 1 if success else 0)
                mlflow.set_tag("passport_id", passport_id)
                mlflow.set_tag("environment", "production")
                print(f"✓ Logged passport generation to MLflow: {passport_id}")
        except Exception as e:
            print(f"⚠ Failed to log passport generation to MLflow: {e}")
