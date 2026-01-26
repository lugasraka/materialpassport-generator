"""
Load all trained ML models on application startup using production artifacts.
"""
import json
import joblib
import torch
from pathlib import Path
import sys
from typing import Optional, Dict, Any

class ModelLoader:
    """Loads and manages ML models from production artifacts"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, Any] = {}
        self.production_metadata: Optional[Dict] = None
        self.production_features: Optional[Dict] = None
        
        print("Initializing ModelLoader...")
    
    def load_all_models(self, models_dir: str = "../../models"):
        """Load all 6 trained models from models/ directory"""
        models_path = Path(models_dir)
        
        if not models_path.exists():
            raise FileNotFoundError(f"Models directory not found: {models_path}")
        
        # Load production metadata
        metadata_file = models_path / "production_metadata.json"
        if metadata_file.exists():
            with open(metadata_file, "r") as f:
                self.production_metadata = json.load(f)
                print(f"✓ Loaded production metadata from {len(self.production_metadata)} models")
        else:
            print("⚠ Production metadata not found - using default model list")
            self.production_metadata = {
                "linear_regression": {"test_r2": 0.6276, "test_rmse": 9.80, "test_mae": 7.75, "features": "8 original"},
                "random_forest": {"test_r2": 0.8793, "test_rmse": 5.58, "test_mae": 3.99, "features": "8 original"},
                "xgboost": {"test_r2": 0.9353, "test_rmse": 4.08, "test_mae": 2.82, "features": "16 aggregate", "best_for_production": True},
                "simple_nn": {"test_r2": 0.8625, "test_rmse": 5.95, "test_mae": 4.18, "features": "8 original"},
                "deep_nn": {"test_r2": 0.8565, "test_rmse": 6.08, "test_mae": 4.27, "features": "8 original"},
                "multitask_nn": {"strength_r2": 0.8667, "strength_rmse": 5.86, "recyclability_accuracy": 0.87, "features": "8 original"}
            }
        
        # Load production features schema
        features_file = models_path / "production_features.json"
        if features_file.exists():
            with open(features_file, "r") as f:
                self.production_features = json.load(f)
                print(f"✓ Loaded production features schema")
        else:
            print("⚠ Production features not found - using default feature list")
        
        # Load Linear Regression
        lr_file = models_path / "linear_regression.pkl"
        if lr_file.exists():
            self.models["linear_regression"] = joblib.load(lr_file)
            print("✓ Loaded Linear Regression")
        else:
            print(f"✗ Model not found: {lr_file}")
        
        # Load Random Forest
        rf_file = models_path / "random_forest.pkl"
        if rf_file.exists():
            self.models["random_forest"] = joblib.load(rf_file)
            print("✓ Loaded Random Forest")
        else:
            print(f"✗ Model not found: {rf_file}")
        
        # Load XGBoost (best model - default)
        xgb_file = models_path / "xgboost.pkl"
        if xgb_file.exists():
            self.models["xgboost"] = joblib.load(xgb_file)
            print("✓ Loaded XGBoost (Best Model)")
        else:
            print(f"✗ Model not found: {xgb_file}")
        
        # Load Simple NN
        simple_nn_file = models_path / "simple_nn.pth"
        if simple_nn_file.exists():
            self.models["simple_nn"] = torch.load(simple_nn_file, map_location="cpu")
            self.models["simple_nn"].eval()
            print("✓ Loaded Simple NN")
        else:
            print(f"✗ Model not found: {simple_nn_file}")
        
        # Load Deep NN
        deep_nn_file = models_path / "deep_nn.pth"
        if deep_nn_file.exists():
            self.models["deep_nn"] = torch.load(deep_nn_file, map_location="cpu")
            self.models["deep_nn"].eval()
            print("✓ Loaded Deep NN")
        else:
            print(f"✗ Model not found: {deep_nn_file}")
        
        # Load Multi-task NN
        multitask_file = models_path / "multitask_nn.pth"
        if multitask_file.exists():
            self.models["multitask_nn"] = torch.load(multitask_file, map_location="cpu")
            self.models["multitask_nn"].eval()
            print("✓ Loaded Multi-task NN")
        else:
            print(f"✗ Model not found: {multitask_file}")
        
        # Load scalers
        scaler_x_file = models_path / "scaler_X.pkl"
        if scaler_x_file.exists():
            self.scalers["X"] = joblib.load(scaler_x_file)
            print("✓ Loaded scaler_X")
        
        scaler_y_str_file = models_path / "scaler_y_str.pkl"
        if scaler_y_str_file.exists():
            self.scalers["y_str"] = joblib.load(scaler_y_str_file)
            print("✓ Loaded scaler_y_str")
        
        scaler_y_circ_file = models_path / "scaler_y_circ.pkl"
        if scaler_y_circ_file.exists():
            self.scalers["y_circ"] = joblib.load(scaler_y_circ_file)
            print("✓ Loaded scaler_y_circ")
        
        print(f"✓ All models loaded: {len(self.models)} models, {len(self.scalers)} scalers")
        return True
    
    def get_model(self, model_name: str):
        """Return specific model by name"""
        model = self.models.get(model_name)
        if model is None:
            raise ValueError(f"Model not found: {model_name}. "
                           f"Available models: {list(self.models.keys())}")
        return model
    
    def get_best_model(self):
        """Return best performing model (XGBoost)"""
        if "xgboost" in self.models:
            print("✓ Using best model: XGBoost")
            return self.models["xgboost"]
        elif self.models:
            print(f"⚠ XGBoost not found, using first available: {list(self.models.keys())[0]}")
            return list(self.models.values())[0]
        raise RuntimeError("No models loaded")
    
    def get_model_metadata(self, model_name: str) -> Dict:
        """Return metadata for a specific model"""
        if self.production_metadata:
            return self.production_metadata.get(model_name, {})
        return {}
    
    def get_production_features(self) -> Dict:
        """Return production features schema"""
        if self.production_features:
            return self.production_features
        return {}
    
    def get_scaler(self, scaler_name: str):
        """Return specific scaler by name"""
        scaler = self.scalers.get(scaler_name)
        if scaler is None:
            raise ValueError(f"Scaler not found: {scaler_name}. "
                           f"Available scalers: {list(self.scalers.keys())}")
        return scaler
    
    def get_available_models(self) -> list:
        """Return list of available model names"""
        return list(self.models.keys())
