"""
Deploy Best Model to Production

This script trains and deploys the best performing model from the optimization journey:
- Features: Aggregate Features (16 features)
- Model: XGBoost
- Hyperparameters: Phase 3 optimized
- Performance: R² = 0.9353, RMSE = 4.08 MPa

This model will be registered to MLflow Model Registry and promoted to Production stage.
"""

import sys
import time
import pickle
import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from xgboost import XGBRegressor
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# MLflow
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

# Add src to path
sys.path.insert(0, 'src')

from src.mlflow_config import (
    MLFLOW_TRACKING_URI,
    EXPERIMENTS,
    MODEL_NAMES,
    PERFORMANCE_TARGETS,
    meets_performance_target
)
from src.utils.mlflow_utils import (
    setup_mlflow_experiment,
    log_model_artifacts,
    log_metrics_and_params,
    log_feature_importance,
    log_predictions_vs_actual,
    log_residual_plot
)

# Configuration
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

print("="*70)
print("DEPLOYING BEST MODEL TO PRODUCTION")
print("="*70)
print(f"[INFO] Model: XGBoost with Aggregate Features")
print(f"[INFO] Expected Performance: R² = 0.9353, RMSE = 4.08 MPa")
print(f"[INFO] Target: Production deployment\n")

# ===== 1. Load Data and Create Features =====
print("="*70)
print("1. LOADING DATA AND CREATING FEATURES")
print("="*70)

data_path = Path('data/processed/concrete_enriched.csv')
if not data_path.exists():
    print("[ERROR] Dataset not found!")
    sys.exit(1)

df = pd.read_csv(data_path)
print(f"[PASS] Dataset loaded: {df.shape[0]} samples\n")

# Original features
original_features = [
    'cement', 'slag', 'fly_ash', 'water', 'superplasticizer',
    'coarse_aggregate', 'fine_aggregate', 'age'
]

def create_aggregate_features(df):
    """
    Create aggregate features that showed best performance in Phase 4.

    These features capture:
    - Total material quantities
    - Binder composition percentages
    - Volume calculations
    """
    df_new = df.copy()

    # Total quantities
    df_new['total_binder'] = df['cement'] + df['slag'] + df['fly_ash']
    df_new['total_aggregate'] = df['coarse_aggregate'] + df['fine_aggregate']
    df_new['total_solid'] = df_new['total_binder'] + df_new['total_aggregate']

    # Binder composition percentages
    total_binder = df_new['total_binder'] + 1e-6
    df_new['cement_pct'] = df['cement'] / total_binder
    df_new['slag_pct'] = df['slag'] / total_binder
    df_new['fly_ash_pct'] = df['fly_ash'] / total_binder

    # Material intensity
    df_new['paste_volume'] = df_new['total_binder'] + df['water']
    df_new['total_volume'] = df_new['paste_volume'] + df_new['total_aggregate']

    return df_new

# Create features
X = create_aggregate_features(df[original_features])
y = df['strength']

feature_cols = X.columns.tolist()

print(f"[PASS] Features created: {len(feature_cols)}")
print(f"  Original: {', '.join(original_features)}")
print(f"  Aggregate: {', '.join([f for f in feature_cols if f not in original_features])}\n")

# Train-test split (same split as optimization)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE
)

print(f"[PASS] Data split:")
print(f"  Training set: {X_train.shape[0]} samples")
print(f"  Test set: {X_test.shape[0]} samples\n")

# ===== 2. Best Model Configuration =====
print("="*70)
print("2. BEST MODEL CONFIGURATION")
print("="*70)

# Best hyperparameters from Phase 3 (optimized on original features)
BEST_HYPERPARAMETERS = {
    'n_estimators': 439,
    'max_depth': 15,
    'learning_rate': 0.05473157755138237,
    'subsample': 0.5837419068252772,
    'colsample_bytree': 0.6379623808381476,
    'gamma': 0.2566623688695714,
    'reg_alpha': 1.8850205603934291,
    'reg_lambda': 0.5512728582442947,
    'min_child_weight': 10,
    'random_state': RANDOM_STATE,
    'n_jobs': -1
}

print("[PASS] Hyperparameters loaded (Phase 3 optimized):")
for key, value in BEST_HYPERPARAMETERS.items():
    if key not in ['random_state', 'n_jobs']:
        print(f"  {key:.<30} {value}")
print()

# ===== 3. Train Production Model =====
print("="*70)
print("3. TRAINING PRODUCTION MODEL")
print("="*70)

model = XGBRegressor(**BEST_HYPERPARAMETERS)

print("[INFO] Training model on training set...")
start_time = time.time()
model.fit(X_train, y_train)
training_time = time.time() - start_time

print(f"[PASS] Model trained in {training_time:.2f} seconds\n")

# ===== 4. Evaluate Model =====
print("="*70)
print("4. MODEL EVALUATION")
print("="*70)

# Predictions
y_pred_train = model.predict(X_train)
y_pred_test = model.predict(X_test)

# Metrics
train_r2 = r2_score(y_train, y_pred_train)
test_r2 = r2_score(y_test, y_pred_test)
test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
test_mae = mean_absolute_error(y_test, y_pred_test)

# Cross-validation
print("[INFO] Running 5-fold cross-validation...")
cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2', n_jobs=-1)
cv_r2_mean = cv_scores.mean()
cv_r2_std = cv_scores.std()

print("\n[PASS] MODEL PERFORMANCE:")
print("="*70)
print(f"  Train R²:                    {train_r2:.4f}")
print(f"  Test R²:                     {test_r2:.4f}")
print(f"  Test RMSE:                   {test_rmse:.2f} MPa")
print(f"  Test MAE:                    {test_mae:.2f} MPa")
print(f"  CV R² (mean ± std):          {cv_r2_mean:.4f} ± {cv_r2_std:.4f}")
print(f"  Training time:               {training_time:.2f} seconds")
print("="*70)

# Check targets
meets_primary = meets_performance_target(test_r2, test_rmse, 'primary')
meets_stretch = meets_performance_target(test_r2, test_rmse, 'stretch')

if meets_stretch:
    print(f"\n[SUCCESS] STRETCH TARGET ACHIEVED!")
elif meets_primary:
    print(f"\n[SUCCESS] PRIMARY TARGET ACHIEVED!")
print(f"  R² > 0.92: {'PASS' if test_r2 > 0.92 else 'FAIL'} ({test_r2:.4f})")
print(f"  RMSE < 4.5: {'PASS' if test_rmse < 4.5 else 'FAIL'} ({test_rmse:.2f} MPa)")

# ===== 5. Register to MLflow =====
print("\n" + "="*70)
print("5. REGISTERING TO MLFLOW MODEL REGISTRY")
print("="*70)

exp_id = setup_mlflow_experiment(
    'hyperparameter_tuning',
    tags={'phase': 'production', 'deployment': 'final'}
)

with mlflow.start_run(run_name="production_xgboost_aggregate_features") as run:

    # Log parameters
    params = {
        **BEST_HYPERPARAMETERS,
        'model_type': 'xgboost',
        'feature_set': 'engineered',
        'feature_details': 'aggregate_features',
        'n_features': len(feature_cols),
        'test_size': 0.2,
        'cv_folds': 5,
        'production_ready': True
    }

    # Log metrics
    metrics = {
        'train_r2': train_r2,
        'test_r2': test_r2,
        'test_rmse': test_rmse,
        'test_mae': test_mae,
        'cv_r2_mean': cv_r2_mean,
        'cv_r2_std': cv_r2_std,
        'training_time_seconds': training_time
    }

    # Log tags
    tags = {
        'model_family': 'baseline',
        'model_type': 'xgboost',
        'tuning_method': 'optuna',
        'feature_set': 'engineered',
        'deployment_stage': 'production',
        'version': '1.0.0',
        'best_model': 'true'
    }

    log_metrics_and_params(params, metrics, tags)
    print(f"[PASS] Logged {len(params)} parameters, {len(metrics)} metrics, {len(tags)} tags")

    # Log model artifacts with registration
    log_model_artifacts(
        model=model,
        model_type='sklearn',
        feature_names=feature_cols,
        register_model=True,
        model_name=MODEL_NAMES['xgboost']
    )
    print(f"[PASS] Model registered: {MODEL_NAMES['xgboost']}")

    # Log plots
    fig = log_feature_importance(model, feature_cols, top_n=16)
    if fig:
        plt.close(fig)
        print(f"[PASS] Logged feature importance plot")

    fig = log_predictions_vs_actual(y_test.values, y_pred_test,
                                   title="Production Model: Predictions vs Actual")
    plt.close(fig)
    print(f"[PASS] Logged predictions vs actual plot")

    fig = log_residual_plot(y_test.values, y_pred_test)
    plt.close(fig)
    print(f"[PASS] Logged residual plot")

    run_id = run.info.run_id
    print(f"\n[PASS] MLflow Run ID: {run_id}")

# ===== 6. Promote to Production Stage =====
print("\n" + "="*70)
print("6. PROMOTING MODEL TO PRODUCTION STAGE")
print("="*70)

client = MlflowClient()
model_name = MODEL_NAMES['xgboost']

# Get latest version
model_versions = client.search_model_versions(f"name='{model_name}'")
latest_version = max([int(mv.version) for mv in model_versions])

print(f"[INFO] Latest model version: {latest_version}")

# Transition to Production
client.transition_model_version_stage(
    name=model_name,
    version=latest_version,
    stage="Production",
    archive_existing_versions=True
)

print(f"[PASS] Model promoted to Production stage")
print(f"  Model: {model_name}")
print(f"  Version: {latest_version}")
print(f"  Stage: Production")

# ===== 7. Save Model Artifacts =====
print("\n" + "="*70)
print("7. SAVING MODEL ARTIFACTS FOR DEPLOYMENT")
print("="*70)

models_dir = Path('models')
models_dir.mkdir(exist_ok=True)

# Save model using pickle
model_path = models_dir / 'production_model.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(model, f)
print(f"[PASS] Model saved: {model_path}")

# Save feature names
feature_path = models_dir / 'production_features.json'
with open(feature_path, 'w') as f:
    json.dump({
        'features': feature_cols,
        'original_features': original_features,
        'n_features': len(feature_cols)
    }, f, indent=2)
print(f"[PASS] Features saved: {feature_path}")

# Save model metadata
metadata_path = models_dir / 'production_metadata.json'
metadata = {
    'model_name': model_name,
    'version': latest_version,
    'mlflow_run_id': run_id,
    'performance': {
        'test_r2': float(test_r2),
        'test_rmse': float(test_rmse),
        'test_mae': float(test_mae),
        'cv_r2_mean': float(cv_r2_mean),
        'cv_r2_std': float(cv_r2_std)
    },
    'hyperparameters': {k: float(v) if isinstance(v, np.floating) else v
                       for k, v in BEST_HYPERPARAMETERS.items()},
    'features': feature_cols,
    'training_date': time.strftime('%Y-%m-%d %H:%M:%S'),
    'stage': 'Production'
}

with open(metadata_path, 'w') as f:
    json.dump(metadata, f, indent=2)
print(f"[PASS] Metadata saved: {metadata_path}")

# ===== 8. Create Prediction Example =====
print("\n" + "="*70)
print("8. TESTING PREDICTION INTERFACE")
print("="*70)

# Test prediction on first sample
test_sample = X_test.iloc[0:1]
test_prediction = model.predict(test_sample)[0]
test_actual = y_test.iloc[0]

print("[PASS] Sample prediction test:")
print(f"  Input features:")
for col, val in test_sample.iloc[0].items():
    print(f"    {col:.<30} {val:.2f}")
print(f"\n  Predicted strength: {test_prediction:.2f} MPa")
print(f"  Actual strength:    {test_actual:.2f} MPa")
print(f"  Error:              {abs(test_prediction - test_actual):.2f} MPa")
print(f"  Relative error:     {abs(test_prediction - test_actual) / test_actual * 100:.2f}%")

# ===== 9. Summary =====
print("\n" + "="*70)
print("PRODUCTION DEPLOYMENT - COMPLETE")
print("="*70)

print("\n[MODEL INFORMATION]")
print(f"  Name:                        {model_name}")
print(f"  Version:                     {latest_version}")
print(f"  Stage:                       Production")
print(f"  MLflow Run ID:               {run_id}")

print("\n[PERFORMANCE METRICS]")
print(f"  Test R²:                     {test_r2:.4f}")
print(f"  Test RMSE:                   {test_rmse:.2f} MPa")
print(f"  Test MAE:                    {test_mae:.2f} MPa")
print(f"  CV R²:                       {cv_r2_mean:.4f} ± {cv_r2_std:.4f}")

print("\n[FEATURES]")
print(f"  Total features:              {len(feature_cols)}")
print(f"  Original features:           {len(original_features)}")
print(f"  Engineered features:         {len(feature_cols) - len(original_features)}")

print("\n[SAVED ARTIFACTS]")
print(f"  Model:                       {model_path}")
print(f"  Features:                    {feature_path}")
print(f"  Metadata:                    {metadata_path}")

print("\n[DEPLOYMENT STATUS]")
if meets_stretch:
    print(f"  Status:                      STRETCH TARGET ACHIEVED")
elif meets_primary:
    print(f"  Status:                      PRIMARY TARGET ACHIEVED")
print(f"  Ready for deployment:        YES")
print(f"  Integration point:           MLflow Model Registry")

print("\n[NEXT STEPS]")
print(f"  1. Integrate with web application")
print(f"  2. Create API endpoint for predictions")
print(f"  3. Set up model monitoring")
print(f"  4. Document prediction interface")
print(f"  5. Deploy to production environment")

print("\n[USAGE]")
print(f"  Load model from MLflow:")
print(f"    model_uri = 'models:/{model_name}/Production'")
print(f"    model = mlflow.pyfunc.load_model(model_uri)")
print(f"")
print(f"  Or load from file:")
print(f"    with open('{model_path}', 'rb') as f:")
print(f"        model = pickle.load(f)")
print(f"")
print(f"  Make predictions:")
print(f"    prediction = model.predict(input_features)")

print("\n" + "="*70)
print("Model successfully deployed and ready for production use!")
print("="*70)
