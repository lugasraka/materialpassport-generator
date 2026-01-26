"""
Handle ML predictions using loaded models with MLflow logging.
"""
import numpy as np
from typing import Dict, Optional, List, Tuple, Any
import sys

class PredictionService:
    """Handle ML predictions using loaded models"""
    
    def __init__(self, model_loader, mlflow_service=None):
        self.model_loader = model_loader
        self.mlflow_service = mlflow_service
        
        print("PredictionService initialized")
    
    def predict_strength(self, composition: dict, model_name: str = "xgboost"):
        """
        Predict compressive strength.
        
        Args:
            composition: Material composition dict with features
            model_name: Name of model to use (default: xgboost)
        
        Returns:
            Dict with prediction value, unit, model, and confidence
        """
        try:
            # Preprocess input
            features = self._preprocess_input(composition)
            
            # Scale features using scaler_X
            if "X" in self.model_loader.scalers:
                features_scaled = self.model_loader.scalers["X"].transform([features])
            else:
                features_scaled = np.array(features).reshape(1, -1)
            
            # Get model
            model = self.model_loader.get_model(model_name) or self.model_loader.get_best_model()
            
            # Run prediction
            if model_name in ["xgboost", "random_forest", "linear_regression"]:
                # Sklearn models
                prediction = model.predict(features_scaled)[0]
            elif model_name in ["simple_nn", "deep_nn", "multitask_nn"]:
                # PyTorch models
                import torch
                with torch.no_grad():
                    input_tensor = torch.tensor(features_scaled, dtype=torch.float32)
                    prediction = model(input_tensor).detach().cpu().numpy()[0]
            else:
                raise ValueError(f"Unknown model: {model_name}")
            
            # Log prediction to MLflow
            if self.mlflow_service:
                self.mlflow_service.log_prediction(
                    model_name=model_name,
                    input_features=composition,
                    prediction=prediction,
                    prediction_type="strength"
                )
            
            # Get confidence from model metadata
            confidence = self._get_confidence(model_name)
            
            return {
                "value": float(prediction),
                "unit": "MPa",
                "model": model_name,
                "confidence": confidence
            }
            
        except Exception as e:
            print(f"✗ Error predicting strength: {e}")
            if self.mlflow_service:
                self.mlflow_service.log_error(model_name, "prediction", str(e))
            raise
    
    def predict_recyclability(self, composition: dict):
        """
        Predict recyclability score using multi-task NN.
        
        Args:
            composition: Material composition dict with features
        
        Returns:
            Dict with score (0-100), grade (A-F), and model name
        """
        try:
            # Use multi-task NN for recyclability prediction
            model_name = "multitask_nn"
            model = self.model_loader.get_model(model_name)
            
            # Preprocess input
            features = self._preprocess_input(composition)
            
            # Scale features
            if "X" in self.model_loader.scalers:
                features_scaled = self.model_loader.scalers["X"].transform([features])
            else:
                features_scaled = np.array(features).reshape(1, -1)
            
            # Predict with PyTorch
            import torch
            with torch.no_grad():
                input_tensor = torch.tensor(features_scaled, dtype=torch.float32)
                # Multi-task NN outputs: [strength, recyclability]
                prediction = model(input_tensor).detach().cpu().numpy()
            
            # Recyclability is the second output
            # Scale from model output (0-1) to 0-100
            score = int(prediction[0][1] * 100)
            score = max(0, min(100, score))
            
            # Calculate grade
            grade = self._calculate_grade(score)
            
            # Log prediction to MLflow
            if self.mlflow_service:
                self.mlflow_service.log_prediction(
                    model_name=model_name,
                    input_features=composition,
                    prediction={"score": score, "grade": grade},
                    prediction_type="recyclability"
                )
            
            return {"score": score, "grade": grade, "model": model_name}
            
        except Exception as e:
            print(f"✗ Error predicting recyclability: {e}")
            if self.mlflow_service:
                self.mlflow_service.log_error(model_name, "recyclability", str(e))
            raise
    
    def get_model_comparison(self, composition: dict) -> Dict:
        """
        Compare predictions from all models for a given composition.
        
        Args:
            composition: Material composition dict with features
        
        Returns:
            Dict with predictions from each model
        """
        predictions = {}
        
        for model_name in self.model_loader.get_available_models():
            try:
                if model_name == "multitask_nn":
                    # Multi-task NN gives strength + recyclability
                    result = self.predict_recyclability(composition)
                    predictions[model_name] = {
                        "strength": None,
                        "recyclability": result
                    }
                else:
                    strength_result = self.predict_strength(composition, model_name)
                    predictions[model_name] = {
                        "strength": strength_result,
                        "recyclability": None
                    }
            except Exception as e:
                print(f"✗ Error with model {model_name}: {e}")
                predictions[model_name] = {"error": str(e)}
        
        return predictions
    
    def _preprocess_input(self, composition: dict) -> list:
        """Convert composition dict to feature array"""
        feature_order = [
            "cement", "blast_furnace_slag", "fly_ash",
            "water", "superplasticizer", "coarse_aggregate",
            "fine_aggregate", "age"
        ]
        return [composition[feat] for feat in feature_order]
    
    def _get_confidence(self, model_name: str) -> float:
        """Get confidence score based on model metadata"""
        try:
            metadata = self.model_loader.get_model_metadata(model_name)
            # Use R² as proxy for confidence
            r2 = metadata.get("test_r2", 0.85)
            return max(0.0, min(1.0, r2))
        except Exception:
            return 0.85  # Default confidence
    
    def _calculate_grade(self, score: int) -> str:
        """Calculate sustainability grade from recyclability score"""
        if score >= 80: return "A"
        elif score >= 60: return "B"
        elif score >= 40: return "C"
        elif score >= 20: return "D"
        else: return "F"
