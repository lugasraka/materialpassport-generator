#!/usr/bin/env python
# coding: utf-8

# # 02. Baseline ML Models with MLflow Tracking
# 
# **Objective:** Build and compare baseline ML models for predicting concrete compressive strength **with comprehensive MLflow experiment tracking**
# 
# **Models:**
# 1. Linear Regression (baseline)
# 2. Random Forest Regressor
# 3. XGBoost Regressor
# 
# **New in this version:**
# - MLflow experiment tracking for all models
# - Automated logging of parameters, metrics, and artifacts
# - Model registry integration
# - Feature importance and visualization tracking
# 
# **Contents:**
# 1. Setup & MLflow Configuration
# 2. Data Loading & Preprocessing
# 3. Train-Test Split
# 4. Feature Scaling
# 5. Model Training with MLflow
# 6. Model Evaluation & Comparison
# 7. Feature Importance Analysis
# 8. Cross-Validation
# 9. Model Registry

# ## 1. Setup & MLflow Configuration

# In[ ]:


# Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import joblib
import warnings
import sys
import time
warnings.filterwarnings('ignore')

# ML libraries
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from xgboost import XGBRegressor

# MLflow imports
import mlflow
import mlflow.sklearn

# Add src to path
sys.path.insert(0, 'src')

# Import MLflow utilities
from src.mlflow_config import (
    MLFLOW_TRACKING_URI,
    EXPERIMENTS,
    MODEL_NAMES,
    TAG_MODEL_FAMILY,
    TAG_MODEL_TYPE,
    TAG_TUNING_METHOD,
    TAG_FEATURE_SET,
    TAG_DATASET_VERSION
)
from src.utils.mlflow_utils import (
    setup_mlflow_experiment,
    log_model_artifacts,
    log_metrics_and_params,
    log_feature_importance,
    log_predictions_vs_actual,
    log_residual_plot,
    compare_runs
)

# Set plotting style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette('Set2')

# Random seed for reproducibility
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

print("[PASS] Libraries imported successfully")
print("[PASS] MLflow utilities imported")


# In[ ]:


# Setup MLflow experiment
experiment_id = setup_mlflow_experiment('baseline_models')

print(f"\n[PASS] MLflow tracking configured:")
print(f"  Tracking URI: {MLFLOW_TRACKING_URI}")
print(f"  Experiment: {EXPERIMENTS['baseline_models']}")
print(f"  Experiment ID: {experiment_id}")
print(f"\nTo view results: mlflow ui --port 5000")
print(f"Then open: http://localhost:5000")


# ## 2. Data Loading & Preprocessing

# In[ ]:


# Load the enriched dataset
data_path = Path('data/processed/concrete_enriched.csv')

if not data_path.exists():
    print("Dataset not found! Please run:")
    print("  python src/data/download_dataset.py")
    sys.exit(1)
else:
    df = pd.read_csv(data_path)
    print(f"[PASS] Dataset loaded: {df.shape[0]} instances, {df.shape[1]} features")
    print(f"\nDataset shape: {df.shape}")


# In[ ]:


# Define features and target
feature_cols = [
    'cement', 'slag', 'fly_ash', 'water',
    'superplasticizer', 'coarse_aggregate',
    'fine_aggregate', 'age'
]

target_col = 'strength'

# Prepare features and target
X = df[feature_cols].copy()
y = df[target_col].copy()

print("Features:")
print(feature_cols)
print(f"\nX shape: {X.shape}")
print(f"y shape: {y.shape}")
print(f"\nTarget statistics:")
print(f"  Min: {y.min():.2f} MPa")
print(f"  Max: {y.max():.2f} MPa")
print(f"  Mean: {y.mean():.2f} MPa")
print(f"  Std: {y.std():.2f} MPa")


# ## 3. Train-Test Split

# In[ ]:


# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE
)

print(f"Training set size: {X_train.shape[0]} samples")
print(f"Test set size: {X_test.shape[0]} samples")
print(f"\nTrain/Test split ratio: {X_train.shape[0]/X_test.shape[0]:.1f}:1")


# ## 4. Feature Scaling

# In[ ]:


# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("[PASS] Features scaled using StandardScaler")
print(f"\nScaled feature means (should be ~0):")
print(np.mean(X_train_scaled, axis=0).round(2))
print(f"\nScaled feature std (should be ~1):")
print(np.std(X_train_scaled, axis=0).round(2))


# ## 5. Model Training with MLflow
# 
# ### Model 1: Linear Regression

# In[ ]:


print("="*60)
print("MODEL 1: LINEAR REGRESSION WITH MLFLOW")
print("="*60)

# Start MLflow run
with mlflow.start_run(run_name="linear_regression_baseline") as run:
    # Record start time
    start_time = time.time()

    # Train model
    lr_model = LinearRegression()
    lr_model.fit(X_train_scaled, y_train)

    # Calculate training time
    training_time = time.time() - start_time

    # Predictions
    y_train_pred_lr = lr_model.predict(X_train_scaled)
    y_test_pred_lr = lr_model.predict(X_test_scaled)

    # Evaluation metrics
    train_r2_lr = r2_score(y_train, y_train_pred_lr)
    test_r2_lr = r2_score(y_test, y_test_pred_lr)
    train_rmse_lr = np.sqrt(mean_squared_error(y_train, y_train_pred_lr))
    test_rmse_lr = np.sqrt(mean_squared_error(y_test, y_test_pred_lr))
    test_mae_lr = mean_absolute_error(y_test, y_test_pred_lr)

    # Cross-validation
    cv_scores_lr = cross_val_score(lr_model, X_train_scaled, y_train, 
                                    cv=5, scoring='r2')

    # Log parameters
    params = {
        'model_type': 'linear_regression',
        'feature_set': 'original_8_features',
        'n_features': X_train.shape[1],
        'test_size': 0.2,
        'random_state': RANDOM_STATE,
        'scaling': 'StandardScaler',
        'fit_intercept': True
    }

    # Log metrics
    metrics = {
        'train_r2': train_r2_lr,
        'test_r2': test_r2_lr,
        'train_rmse': train_rmse_lr,
        'test_rmse': test_rmse_lr,
        'test_mae': test_mae_lr,
        'cv_r2_mean': cv_scores_lr.mean(),
        'cv_r2_std': cv_scores_lr.std(),
        'training_time_seconds': training_time,
        'overfitting_gap': train_r2_lr - test_r2_lr
    }

    # Log tags
    tags = {
        TAG_MODEL_FAMILY: 'baseline',
        TAG_MODEL_TYPE: 'linear_regression',
        TAG_TUNING_METHOD: 'default',
        TAG_FEATURE_SET: 'original',
        TAG_DATASET_VERSION: 'v1.0'
    }

    log_metrics_and_params(params, metrics, tags)

    # Log model and artifacts
    log_model_artifacts(
        model=lr_model,
        model_type='sklearn',
        scaler=scaler,
        feature_names=feature_cols,
        register_model=True,
        model_name=MODEL_NAMES['linear_regression']
    )

    # Log visualizations
    fig = log_predictions_vs_actual(
        y_test.values, y_test_pred_lr,
        title="Linear Regression: Predictions vs Actual"
    )
    plt.close(fig)

    fig = log_residual_plot(y_test.values, y_test_pred_lr)
    plt.close(fig)

    # Log feature coefficients
    coef_dict = {f'coef_{feat}': coef for feat, coef in zip(feature_cols, lr_model.coef_)}
    mlflow.log_params(coef_dict)

    run_id_lr = run.info.run_id

    print(f"\n[PASS] MLflow run completed: {run_id_lr}")
    print(f"\nTraining Performance:")
    print(f"  R² Score: {train_r2_lr:.4f}")
    print(f"  RMSE: {train_rmse_lr:.4f} MPa")
    print(f"\nTest Performance:")
    print(f"  R² Score: {test_r2_lr:.4f}")
    print(f"  RMSE: {test_rmse_lr:.4f} MPa")
    print(f"  MAE: {test_mae_lr:.4f} MPa")
    print(f"\nCross-Validation:")
    print(f"  Mean R²: {cv_scores_lr.mean():.4f} (+/- {cv_scores_lr.std():.4f})")


# ### Model 2: Random Forest

# In[ ]:


print("="*60)
print("MODEL 2: RANDOM FOREST WITH MLFLOW")
print("="*60)

with mlflow.start_run(run_name="random_forest_baseline") as run:
    start_time = time.time()

    # Train model
    rf_model = RandomForestRegressor(
        n_estimators=100,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=RANDOM_STATE,
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)

    training_time = time.time() - start_time

    # Predictions
    y_train_pred_rf = rf_model.predict(X_train)
    y_test_pred_rf = rf_model.predict(X_test)

    # Metrics
    train_r2_rf = r2_score(y_train, y_train_pred_rf)
    test_r2_rf = r2_score(y_test, y_test_pred_rf)
    train_rmse_rf = np.sqrt(mean_squared_error(y_train, y_train_pred_rf))
    test_rmse_rf = np.sqrt(mean_squared_error(y_test, y_test_pred_rf))
    test_mae_rf = mean_absolute_error(y_test, y_test_pred_rf)

    # Cross-validation
    cv_scores_rf = cross_val_score(rf_model, X_train, y_train, 
                                    cv=5, scoring='r2')

    # Log parameters
    params = {
        'model_type': 'random_forest',
        'feature_set': 'original_8_features',
        'n_features': X_train.shape[1],
        'test_size': 0.2,
        'random_state': RANDOM_STATE,
        'n_estimators': rf_model.n_estimators,
        'max_depth': rf_model.max_depth,
        'min_samples_split': rf_model.min_samples_split,
        'min_samples_leaf': rf_model.min_samples_leaf,
        'scaling': 'None'
    }

    metrics = {
        'train_r2': train_r2_rf,
        'test_r2': test_r2_rf,
        'train_rmse': train_rmse_rf,
        'test_rmse': test_rmse_rf,
        'test_mae': test_mae_rf,
        'cv_r2_mean': cv_scores_rf.mean(),
        'cv_r2_std': cv_scores_rf.std(),
        'training_time_seconds': training_time,
        'overfitting_gap': train_r2_rf - test_r2_rf
    }

    tags = {
        TAG_MODEL_FAMILY: 'baseline',
        TAG_MODEL_TYPE: 'random_forest',
        TAG_TUNING_METHOD: 'default',
        TAG_FEATURE_SET: 'original',
        TAG_DATASET_VERSION: 'v1.0'
    }

    log_metrics_and_params(params, metrics, tags)

    # Log model
    log_model_artifacts(
        model=rf_model,
        model_type='sklearn',
        feature_names=feature_cols,
        register_model=True,
        model_name=MODEL_NAMES['random_forest']
    )

    # Log visualizations
    fig = log_predictions_vs_actual(
        y_test.values, y_test_pred_rf,
        title="Random Forest: Predictions vs Actual"
    )
    plt.close(fig)

    fig = log_residual_plot(y_test.values, y_test_pred_rf)
    plt.close(fig)

    # Log feature importance
    fig = log_feature_importance(rf_model, feature_cols, top_n=8)
    plt.close(fig)

    run_id_rf = run.info.run_id

    print(f"\n[PASS] MLflow run completed: {run_id_rf}")
    print(f"\nTraining Performance:")
    print(f"  R² Score: {train_r2_rf:.4f}")
    print(f"  RMSE: {train_rmse_rf:.4f} MPa")
    print(f"\nTest Performance:")
    print(f"  R² Score: {test_r2_rf:.4f}")
    print(f"  RMSE: {test_rmse_rf:.4f} MPa")
    print(f"  MAE: {test_mae_rf:.4f} MPa")
    print(f"\nCross-Validation:")
    print(f"  Mean R²: {cv_scores_rf.mean():.4f} (+/- {cv_scores_rf.std():.4f})")


# ### Model 3: XGBoost

# In[ ]:


print("="*60)
print("MODEL 3: XGBOOST WITH MLFLOW")
print("="*60)

with mlflow.start_run(run_name="xgboost_baseline") as run:
    start_time = time.time()

    # Train model
    xgb_model = XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=RANDOM_STATE,
        n_jobs=-1
    )
    xgb_model.fit(X_train, y_train)

    training_time = time.time() - start_time

    # Predictions
    y_train_pred_xgb = xgb_model.predict(X_train)
    y_test_pred_xgb = xgb_model.predict(X_test)

    # Metrics
    train_r2_xgb = r2_score(y_train, y_train_pred_xgb)
    test_r2_xgb = r2_score(y_test, y_test_pred_xgb)
    train_rmse_xgb = np.sqrt(mean_squared_error(y_train, y_train_pred_xgb))
    test_rmse_xgb = np.sqrt(mean_squared_error(y_test, y_test_pred_xgb))
    test_mae_xgb = mean_absolute_error(y_test, y_test_pred_xgb)

    # Cross-validation
    cv_scores_xgb = cross_val_score(xgb_model, X_train, y_train, 
                                     cv=5, scoring='r2')

    # Log parameters
    params = {
        'model_type': 'xgboost',
        'feature_set': 'original_8_features',
        'n_features': X_train.shape[1],
        'test_size': 0.2,
        'random_state': RANDOM_STATE,
        'n_estimators': xgb_model.n_estimators,
        'max_depth': xgb_model.max_depth,
        'learning_rate': xgb_model.learning_rate,
        'subsample': xgb_model.subsample,
        'colsample_bytree': xgb_model.colsample_bytree,
        'scaling': 'None'
    }

    metrics = {
        'train_r2': train_r2_xgb,
        'test_r2': test_r2_xgb,
        'train_rmse': train_rmse_xgb,
        'test_rmse': test_rmse_xgb,
        'test_mae': test_mae_xgb,
        'cv_r2_mean': cv_scores_xgb.mean(),
        'cv_r2_std': cv_scores_xgb.std(),
        'training_time_seconds': training_time,
        'overfitting_gap': train_r2_xgb - test_r2_xgb
    }

    tags = {
        TAG_MODEL_FAMILY: 'baseline',
        TAG_MODEL_TYPE: 'xgboost',
        TAG_TUNING_METHOD: 'default',
        TAG_FEATURE_SET: 'original',
        TAG_DATASET_VERSION: 'v1.0'
    }

    log_metrics_and_params(params, metrics, tags)

    # Log model
    log_model_artifacts(
        model=xgb_model,
        model_type='sklearn',
        feature_names=feature_cols,
        register_model=True,
        model_name=MODEL_NAMES['xgboost']
    )

    # Log visualizations
    fig = log_predictions_vs_actual(
        y_test.values, y_test_pred_xgb,
        title="XGBoost: Predictions vs Actual"
    )
    plt.close(fig)

    fig = log_residual_plot(y_test.values, y_test_pred_xgb)
    plt.close(fig)

    # Log feature importance
    fig = log_feature_importance(xgb_model, feature_cols, top_n=8)
    plt.close(fig)

    run_id_xgb = run.info.run_id

    print(f"\n[PASS] MLflow run completed: {run_id_xgb}")
    print(f"\nTraining Performance:")
    print(f"  R² Score: {train_r2_xgb:.4f}")
    print(f"  RMSE: {train_rmse_xgb:.4f} MPa")
    print(f"\nTest Performance:")
    print(f"  R² Score: {test_r2_xgb:.4f}")
    print(f"  RMSE: {test_rmse_xgb:.4f} MPa")
    print(f"  MAE: {test_mae_xgb:.4f} MPa")
    print(f"\nCross-Validation:")
    print(f"  Mean R²: {cv_scores_xgb.mean():.4f} (+/- {cv_scores_xgb.std():.4f})")


# ## 6. Model Comparison with MLflow

# In[ ]:


# Compare all runs using MLflow
print("="*60)
print("COMPARING RUNS FROM MLFLOW")
print("="*60)

comparison_df = compare_runs(
    experiment_names=[EXPERIMENTS['baseline_models']],
    metrics=['test_r2', 'test_rmse', 'test_mae', 'cv_r2_mean', 'training_time_seconds'],
    max_results=10
)

# Filter for baseline runs only
baseline_runs = comparison_df[
    comparison_df['run_name'].str.contains('baseline')
].copy()

print(f"\nFound {len(baseline_runs)} baseline model runs:\n")
print(baseline_runs[[
    'run_name', 'model_type', 'test_r2', 'test_rmse', 
    'test_mae', 'cv_r2_mean', 'training_time_seconds'
]].to_string(index=False))

# Identify best model
if len(baseline_runs) > 0:
    best_idx = baseline_runs['test_r2'].idxmax()
    best_model = baseline_runs.loc[best_idx, 'model_type']
    best_r2 = baseline_runs.loc[best_idx, 'test_r2']
    best_rmse = baseline_runs.loc[best_idx, 'test_rmse']

    print(f"\n{'='*60}")
    print(f"[PASS] Best Model: {best_model}")
    print(f"  Test R²: {best_r2:.4f}")
    print(f"  Test RMSE: {best_rmse:.4f} MPa")
    print(f"{'='*60}")


# ## 7. Visualize Model Comparison

# In[ ]:


# Create manual comparison for plotting
comparison_manual = pd.DataFrame({
    'Model': ['Linear Regression', 'Random Forest', 'XGBoost'],
    'Train R²': [train_r2_lr, train_r2_rf, train_r2_xgb],
    'Test R²': [test_r2_lr, test_r2_rf, test_r2_xgb],
    'Train RMSE': [train_rmse_lr, train_rmse_rf, train_rmse_xgb],
    'Test RMSE': [test_rmse_lr, test_rmse_rf, test_rmse_xgb],
    'Test MAE': [test_mae_lr, test_mae_rf, test_mae_xgb]
})

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# R² Score comparison
models = comparison_manual['Model']
x_pos = np.arange(len(models))
width = 0.35

axes[0].bar(x_pos - width/2, comparison_manual['Train R²'], width, label='Train', alpha=0.8)
axes[0].bar(x_pos + width/2, comparison_manual['Test R²'], width, label='Test', alpha=0.8)
axes[0].set_ylabel('R² Score')
axes[0].set_title('Model Performance: R² Score')
axes[0].set_xticks(x_pos)
axes[0].set_xticklabels(models, rotation=45)
axes[0].legend()
axes[0].grid(axis='y', alpha=0.3)

# RMSE comparison
axes[1].bar(x_pos - width/2, comparison_manual['Train RMSE'], width, label='Train', alpha=0.8)
axes[1].bar(x_pos + width/2, comparison_manual['Test RMSE'], width, label='Test', alpha=0.8)
axes[1].set_ylabel('RMSE (MPa)')
axes[1].set_title('Model Performance: RMSE')
axes[1].set_xticks(x_pos)
axes[1].set_xticklabels(models, rotation=45)
axes[1].legend()
axes[1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.show()


# ## 8. Save Models (Traditional Method)

# In[ ]:


# Save models using joblib (in addition to MLflow)
models_dir = Path('models')
models_dir.mkdir(parents=True, exist_ok=True)

joblib.dump(lr_model, models_dir / 'linear_regression.pkl')
joblib.dump(rf_model, models_dir / 'random_forest.pkl')
joblib.dump(xgb_model, models_dir / 'xgboost.pkl')
joblib.dump(scaler, models_dir / 'scaler.pkl')

print("[PASS] Models saved to models/ directory:")
print("  - linear_regression.pkl")
print("  - random_forest.pkl")
print("  - xgboost.pkl")
print("  - scaler.pkl")
print("\n[INFO] Models are also tracked in MLflow registry")


# ## 9. Summary & Next Steps

# In[ ]:


print("\n" + "="*60)
print("MLFLOW BASELINE MODELS COMPLETE")
print("="*60)

print("\n[PASS] MODEL PERFORMANCE:")
print(f"   • Linear Regression: R² = {test_r2_lr:.4f}, RMSE = {test_rmse_lr:.2f} MPa")
print(f"   • Random Forest: R² = {test_r2_rf:.4f}, RMSE = {test_rmse_rf:.2f} MPa")
print(f"   • XGBoost: R² = {test_r2_xgb:.4f}, RMSE = {test_rmse_xgb:.2f} MPa")

print("\n[PASS] MLFLOW TRACKING:")
print(f"   • Experiment: {EXPERIMENTS['baseline_models']}")
print(f"   • Runs logged: 3 (Linear Regression, Random Forest, XGBoost)")
print(f"   • Models registered: 3")
print(f"   • Artifacts: Parameters, metrics, models, plots")

print("\n[INFO] VIEW RESULTS:")
print("   1. Open terminal in project directory")
print("   2. Run: mlflow ui --port 5000")
print("   3. Open: http://localhost:5000")
print(f"   4. Navigate to experiment: {EXPERIMENTS['baseline_models']}")

print("\n[INFO] NEXT STEPS:")
print("   • Phase 2: Add deep learning models with MLflow")
print("   • Phase 3: Hyperparameter optimization with Optuna + MLflow")
print("   • Phase 4: Feature engineering experiments")
print("   • Phase 5: Ensemble models")

print("\n" + "="*60)
print("[PASS] Baseline models with MLflow tracking complete!")
print("="*60 + "\n")

