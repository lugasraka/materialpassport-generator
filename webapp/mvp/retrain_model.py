"""
Retrain XGBoost Model Script
=============================

This script retrains the XGBoost model for concrete compressive strength prediction.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelRetrainer:
    """Retrain XGBoost model for concrete strength prediction"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / 'data'
        self.models_dir = self.project_root / 'models'
        
        # Create models directory if it doesn't exist
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
    def load_data(self):
        """Load and prepare dataset"""
        logger.info("Loading dataset...")
        
        # Try processed data first
        processed_path = self.data_dir / 'processed' / 'concrete_enriched.csv'
        raw_path = self.data_dir / 'raw' / 'concrete_data.csv'
        
        if processed_path.exists():
            df = pd.read_csv(processed_path)
            logger.info(f"✓ Loaded processed data from {processed_path}")
        elif raw_path.exists():
            df = pd.read_csv(raw_path)
            logger.info(f"✓ Loaded raw data from {raw_path}")
            
            # Rename columns if needed
            column_mapping = {
                'Cement': 'cement',
                'Blast Furnace Slag': 'slag',
                'Fly Ash': 'fly_ash',
                'Water': 'water',
                'Superplasticizer': 'superplasticizer',
                'Coarse Aggregate': 'coarse_aggregate',
                'Fine Aggregate': 'fine_aggregate',
                'Age': 'age',
                'Concrete compressive strength': 'strength'
            }
            
            if all(col in df.columns for col in column_mapping.keys()):
                df = df.rename(columns=column_mapping)
        else:
            raise FileNotFoundError("No dataset found. Please run download_dataset.py first.")
        
        # Select features and target
        feature_cols = ['cement', 'slag', 'fly_ash', 'water', 'superplasticizer', 
                       'coarse_aggregate', 'fine_aggregate', 'age']
        target_col = 'strength'
        
        X = df[feature_cols]
        y = df[target_col]
        
        logger.info(f"Dataset shape: X={X.shape}, y={y.shape}")
        logger.info(f"Features: {list(X.columns)}")
        
        return X, y
    
    def train_model(self, X, y, test_size=0.2, random_state=42):
        """Train XGBoost model with proper configuration"""
        logger.info("Preparing data for training...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        logger.info(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
        
        # Scale features
        logger.info("Scaling features...")
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train XGBoost model
        logger.info("Training XGBoost model...")
        model = XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=1,
            random_state=random_state,
            n_jobs=-1
        )
        
        model.fit(X_train_scaled, y_train)
        logger.info("✓ Model training complete")
        
        # Evaluate model
        logger.info("Evaluating model...")
        
        # Training predictions
        y_train_pred = model.predict(X_train_scaled)
        train_r2 = r2_score(y_train, y_train_pred)
        train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
        train_mae = mean_absolute_error(y_train, y_train_pred)
        
        # Test predictions
        y_test_pred = model.predict(X_test_scaled)
        test_r2 = r2_score(y_test, y_test_pred)
        test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        test_mae = mean_absolute_error(y_test, y_test_pred)
        
        # Cross-validation
        logger.info("Running cross-validation...")
        cv_scores = cross_val_score(
            model, X_train_scaled, y_train, 
            cv=5, scoring='r2', n_jobs=-1
        )
        
        # Print results
        print("\n" + "="*60)
        print("MODEL PERFORMANCE")
        print("="*60)
        print("\nTraining Metrics:")
        print(f"  R² Score:  {train_r2:.4f}")
        print(f"  RMSE:      {train_rmse:.2f} MPa")
        print(f"  MAE:       {train_mae:.2f} MPa")
        
        print("\nTest Metrics:")
        print(f"  R² Score:  {test_r2:.4f}")
        print(f"  RMSE:      {test_rmse:.2f} MPa")
        print(f"  MAE:       {test_mae:.2f} MPa")
        
        print("\nCross-Validation:")
        print(f"  Mean R²:   {cv_scores.mean():.4f} (± {cv_scores.std():.4f})")
        print("="*60 + "\n")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("Feature Importance:")
        print(feature_importance.to_string(index=False))
        print()
        
        return model, scaler, {
            'train_r2': train_r2,
            'train_rmse': train_rmse,
            'test_r2': test_r2,
            'test_rmse': test_rmse,
            'cv_scores': cv_scores,
            'feature_importance': feature_importance
        }
    
    def save_models(self, model, scaler):
        """Save trained model and scaler"""
        logger.info("Saving models...")
        
        # Save XGBoost model
        model_path = self.models_dir / 'xgboost.pkl'
        joblib.dump(model, model_path)
        logger.info(f"✓ Model saved to {model_path}")
        
        # Save scaler
        scaler_path = self.models_dir / 'scaler.pkl'
        joblib.dump(scaler, scaler_path)
        logger.info(f"✓ Scaler saved to {scaler_path}")
        
        return model_path, scaler_path
    
    def test_predictions(self, model, scaler):
        """Test model with sample predictions"""
        print("\n" + "="*60)
        print("TESTING MODEL WITH SAMPLE PREDICTIONS")
        print("="*60)
        
        # Test cases from QUICKSTART.md
        test_cases = [
            {
                'name': 'Standard Concrete',
                'cement': 300, 'slag': 0, 'fly_ash': 0, 'water': 170,
                'superplasticizer': 0, 'coarse_aggregate': 950, 
                'fine_aggregate': 700, 'age': 28,
                'expected': '35-40 MPa'
            },
            {
                'name': 'High Strength',
                'cement': 400, 'slag': 100, 'fly_ash': 0, 'water': 160,
                'superplasticizer': 5, 'coarse_aggregate': 950, 
                'fine_aggregate': 700, 'age': 28,
                'expected': '45-50 MPa'
            },
            {
                'name': 'Eco-Friendly',
                'cement': 250, 'slag': 150, 'fly_ash': 100, 'water': 170,
                'superplasticizer': 5, 'coarse_aggregate': 950, 
                'fine_aggregate': 700, 'age': 90,
                'expected': '35-40 MPa'
            }
        ]
        
        for test in test_cases:
            # Create input DataFrame
            input_data = pd.DataFrame([{
                'cement': test['cement'],
                'slag': test['slag'],
                'fly_ash': test['fly_ash'],
                'water': test['water'],
                'superplasticizer': test['superplasticizer'],
                'coarse_aggregate': test['coarse_aggregate'],
                'fine_aggregate': test['fine_aggregate'],
                'age': test['age']
            }])
            
            # Scale and predict
            input_scaled = scaler.transform(input_data)
            prediction = model.predict(input_scaled)[0]
            
            print(f"\n{test['name']}:")
            print(f"  Composition: Cement={test['cement']}, Slag={test['slag']}, "
                  f"Fly Ash={test['fly_ash']}, Age={test['age']} days")
            print(f"  Expected:  {test['expected']}")
            print(f"  Predicted: {prediction:.2f} MPa")
        
        print("\n" + "="*60 + "\n")


def main():
    """Main execution"""
    print("\n" + "="*60)
    print("XGBOOST MODEL RETRAINING")
    print("="*60 + "\n")
    
    try:
        # Initialize retrainer
        retrainer = ModelRetrainer()
        
        # Load data
        X, y = retrainer.load_data()
        
        # Train model
        model, scaler, metrics = retrainer.train_model(X, y)
        
        # Save models
        retrainer.save_models(model, scaler)
        
        # Test predictions
        retrainer.test_predictions(model, scaler)
        
        print("✓ Model retraining complete!")
        print("\nNext steps:")
        print("  1. Restart the Streamlit app")
        print("  2. Test with different input compositions")
        print("  3. Verify predictions are now varying correctly")
        
    except Exception as e:
        logger.error(f"Error during retraining: {e}")
        raise


if __name__ == "__main__":
    main()
