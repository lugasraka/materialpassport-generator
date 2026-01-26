"""
Phase 3: Hyperparameter Optimization with Optuna + MLflow

Objective: Systematically optimize hyperparameters to achieve performance targets:
- Primary Target: R² > 0.92, RMSE < 4.5 MPa
- Stretch Target: R² > 0.94, RMSE < 4.0 MPa

Current Best Baseline: XGBoost (R² = 0.9088, RMSE = 4.85 MPa)

This script uses Optuna for Bayesian hyperparameter optimization with MLflow tracking.
"""

import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
import matplotlib.pyplot as plt
import seaborn as sns

# MLflow and Optuna
import mlflow
import mlflow.sklearn
import optuna
from optuna.integration.mlflow import MLflowCallback

# Add src to path
sys.path.insert(0, 'src')

from src.mlflow_config import (
    MLFLOW_TRACKING_URI,
    EXPERIMENTS,
    MODEL_NAMES,
    PERFORMANCE_TARGETS,
    get_tracking_uri,
    get_experiment_name,
    get_model_name,
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

print("[INFO] All imports successful")
print(f"[INFO] MLflow Tracking URI: {MLFLOW_TRACKING_URI}")
print(f"[INFO] Performance Targets: R² > {PERFORMANCE_TARGETS['primary_r2']}, RMSE < {PERFORMANCE_TARGETS['primary_rmse']} MPa")

# ===== 1. Load and Prepare Data =====
print("\n" + "="*70)
print("1. LOADING AND PREPARING DATA")
print("="*70)

data_path = Path('data/processed/concrete_enriched.csv')

if not data_path.exists():
    print("[ERROR] Dataset not found!")
    print(f"[ERROR] Expected path: {data_path.absolute()}")
    sys.exit(1)
else:
    df = pd.read_csv(data_path)
    print(f"[PASS] Dataset loaded: {df.shape[0]} samples, {df.shape[1]} features")

# Feature columns (8 original features)
feature_cols = [
    'cement', 'slag', 'fly_ash', 'water', 'superplasticizer',
    'coarse_aggregate', 'fine_aggregate', 'age'
]

X = df[feature_cols]
y = df['strength']

# Train-test split (80-20)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE
)

print(f"[PASS] Data split:")
print(f"  Training set: {X_train.shape[0]} samples")
print(f"  Test set: {X_test.shape[0]} samples")
print(f"  Features: {X_train.shape[1]}")

# ===== 2. XGBoost Hyperparameter Optimization with Optuna =====
print("\n" + "="*70)
print("2. XGBOOST HYPERPARAMETER OPTIMIZATION")
print("="*70)

# Setup MLflow experiment
exp_id = setup_mlflow_experiment(
    'hyperparameter_tuning',
    tags={'phase': '3', 'model': 'xgboost', 'method': 'optuna'}
)
print(f"[PASS] Experiment setup: {EXPERIMENTS['hyperparameter_tuning']} (ID: {exp_id})")

# Global variables for Optuna objective
X_train_global = X_train
y_train_global = y_train
X_test_global = X_test
y_test_global = y_test

def objective(trial):
    """
    Optuna objective function for XGBoost hyperparameter optimization.
    Returns: CV R² score (to be maximized)
    """
    # Suggest hyperparameters
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 100, 500),
        'max_depth': trial.suggest_int('max_depth', 3, 15),
        'learning_rate': trial.suggest_float('learning_rate', 0.001, 0.3, log=True),
        'subsample': trial.suggest_float('subsample', 0.5, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
        'gamma': trial.suggest_float('gamma', 0, 1),
        'reg_alpha': trial.suggest_float('reg_alpha', 0, 2),
        'reg_lambda': trial.suggest_float('reg_lambda', 0, 2),
        'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
        'random_state': RANDOM_STATE,
        'n_jobs': -1
    }

    # Create model
    model = XGBRegressor(**params)

    # 5-fold cross-validation on training set
    cv_scores = cross_val_score(
        model, X_train_global, y_train_global,
        cv=5, scoring='r2', n_jobs=-1
    )
    cv_r2_mean = cv_scores.mean()

    # Report intermediate value for pruning
    trial.report(cv_r2_mean, step=0)

    # Handle pruning
    if trial.should_prune():
        raise optuna.TrialPruned()

    return cv_r2_mean

print("[PASS] Objective function defined")

# Create Optuna study
study_name = "xgboost_concrete_strength_optimization"

study = optuna.create_study(
    study_name=study_name,
    direction='maximize',  # Maximize R²
    pruner=optuna.pruners.MedianPruner(n_startup_trials=10, n_warmup_steps=3),
    sampler=optuna.samplers.TPESampler(seed=RANDOM_STATE)
)

print(f"[PASS] Optuna study created: {study_name}")
print(f"[INFO] Starting optimization with 200 trials...")
print(f"[INFO] This may take 15-30 minutes depending on your hardware\n")

# Run optimization with MLflow callback
mlflowc = MLflowCallback(
    tracking_uri=MLFLOW_TRACKING_URI,
    metric_name="cv_r2",
    create_experiment=False,
    mlflow_kwargs={"experiment_id": exp_id}
)

start_time = time.time()

study.optimize(
    objective,
    n_trials=200,
    callbacks=[mlflowc],
    show_progress_bar=True
)

optimization_time = time.time() - start_time

print(f"\n[PASS] Optimization complete in {optimization_time/60:.2f} minutes")
print(f"[INFO] Total trials: {len(study.trials)}")
print(f"[INFO] Pruned trials: {len([t for t in study.trials if t.state == optuna.trial.TrialState.PRUNED])}")
print(f"[INFO] Complete trials: {len([t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE])}")

# ===== 3. Evaluate Best Model =====
print("\n" + "="*70)
print("3. EVALUATING BEST MODEL")
print("="*70)

# Get best hyperparameters
best_params = study.best_params
best_cv_r2 = study.best_value

print("[PASS] BEST HYPERPARAMETERS FOUND:")
print("=" * 70)
for param, value in best_params.items():
    print(f"  {param:.<30} {value}")
print("=" * 70)
print(f"  Best CV R²: {best_cv_r2:.4f}\n")

# Train best model on full training set
best_model = XGBRegressor(
    **best_params,
    random_state=RANDOM_STATE,
    n_jobs=-1
)

start_time_train = time.time()
best_model.fit(X_train, y_train)
training_time = time.time() - start_time_train

# Predictions
y_pred_train = best_model.predict(X_train)
y_pred_test = best_model.predict(X_test)

# Calculate metrics
train_r2 = r2_score(y_train, y_pred_train)
test_r2 = r2_score(y_test, y_pred_test)
test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
test_mae = mean_absolute_error(y_test, y_pred_test)

# Cross-validation
cv_scores = cross_val_score(best_model, X_train, y_train, cv=5, scoring='r2')
cv_r2_mean = cv_scores.mean()
cv_r2_std = cv_scores.std()

print("[PASS] OPTIMIZED MODEL PERFORMANCE:")
print("=" * 70)
print(f"  Train R²: {train_r2:.4f}")
print(f"  Test R²: {test_r2:.4f}")
print(f"  Test RMSE: {test_rmse:.2f} MPa")
print(f"  Test MAE: {test_mae:.2f} MPa")
print(f"  CV R² (mean ± std): {cv_r2_mean:.4f} ± {cv_r2_std:.4f}")
print(f"  Training time: {training_time:.2f} seconds")
print("=" * 70)

# Check if performance targets met
meets_primary = meets_performance_target(test_r2, test_rmse, 'primary')
meets_stretch = meets_performance_target(test_r2, test_rmse, 'stretch')

if meets_stretch:
    print("\n[SUCCESS] Stretch target achieved! R² > 0.94, RMSE < 4.0 MPa")
elif meets_primary:
    print("\n[SUCCESS] Primary target achieved! R² > 0.92, RMSE < 4.5 MPa")
else:
    print(f"\n[INFO] Target not met. Need R² > {PERFORMANCE_TARGETS['primary_r2']}, RMSE < {PERFORMANCE_TARGETS['primary_rmse']} MPa")

# Compare with baseline
baseline_r2 = 0.9088
baseline_rmse = 4.85
r2_improvement = (test_r2 - baseline_r2) / baseline_r2 * 100
rmse_improvement = (baseline_rmse - test_rmse) / baseline_rmse * 100

print(f"\n[COMPARISON] vs. Baseline XGBoost:")
print(f"  R² improvement: {r2_improvement:+.2f}%")
print(f"  RMSE improvement: {rmse_improvement:+.2f}%")

# ===== 4. Log Best Model to MLflow =====
print("\n" + "="*70)
print("4. LOGGING TO MLFLOW")
print("="*70)

# Start MLflow run for best model
with mlflow.start_run(run_name="xgboost_optuna_best") as run:

    # Log all hyperparameters
    params = {
        **best_params,
        'model_type': 'xgboost',
        'feature_set': 'original_8_features',
        'test_size': 0.2,
        'cv_folds': 5,
        'optimization_method': 'optuna',
        'optimization_trials': len(study.trials),
        'optimization_time_minutes': optimization_time / 60
    }

    # Log all metrics
    metrics = {
        'train_r2': train_r2,
        'test_r2': test_r2,
        'test_rmse': test_rmse,
        'test_mae': test_mae,
        'cv_r2_mean': cv_r2_mean,
        'cv_r2_std': cv_r2_std,
        'training_time_seconds': training_time,
        'r2_improvement_pct': r2_improvement,
        'rmse_improvement_pct': rmse_improvement
    }

    # Log tags
    tags = {
        'model_family': 'baseline',
        'model_type': 'xgboost',
        'tuning_method': 'optuna',
        'feature_set': 'original',
        'target_met': 'stretch' if meets_stretch else ('primary' if meets_primary else 'no'),
        'best_so_far': 'true'
    }

    log_metrics_and_params(params, metrics, tags)
    print(f"[PASS] Logged {len(params)} parameters")
    print(f"[PASS] Logged {len(metrics)} metrics")
    print(f"[PASS] Logged {len(tags)} tags")

    # Log model and artifacts
    log_model_artifacts(
        model=best_model,
        model_type='sklearn',
        feature_names=feature_cols,
        register_model=True,
        model_name=MODEL_NAMES['xgboost']
    )
    print(f"[PASS] Logged model to registry: {MODEL_NAMES['xgboost']}")

    # Log feature importance
    fig = log_feature_importance(best_model, feature_cols)
    if fig:
        plt.close(fig)
        print(f"[PASS] Logged feature importance plot")

    # Log predictions vs actual
    fig = log_predictions_vs_actual(y_test.values, y_pred_test)
    plt.close(fig)
    print(f"[PASS] Logged predictions vs actual plot")

    # Log residual plot
    fig = log_residual_plot(y_test.values, y_pred_test)
    plt.close(fig)
    print(f"[PASS] Logged residual plot")

    run_id = run.info.run_id
    print(f"\n[PASS] MLflow Run ID: {run_id}")

# ===== 5. Optuna Optimization Visualizations =====
print("\n" + "="*70)
print("5. CREATING OPTUNA VISUALIZATIONS")
print("="*70)

try:
    import plotly

    # Optimization history
    fig = optuna.visualization.plot_optimization_history(study)
    fig.update_layout(title="Optuna Optimization History")
    mlflow.log_figure(fig, "optuna_optimization_history.html")
    print("[PASS] Logged optimization history plot")

    # Parameter importance
    fig = optuna.visualization.plot_param_importances(study)
    fig.update_layout(title="Hyperparameter Importance")
    mlflow.log_figure(fig, "optuna_param_importances.html")
    print("[PASS] Logged parameter importance plot")

    # Parallel coordinate plot
    fig = optuna.visualization.plot_parallel_coordinate(study)
    fig.update_layout(title="Parallel Coordinate Plot")
    mlflow.log_figure(fig, "optuna_parallel_coordinate.html")
    print("[PASS] Logged parallel coordinate plot")

    # Slice plot
    fig = optuna.visualization.plot_slice(study)
    fig.update_layout(title="Parameter Slice Plot")
    mlflow.log_figure(fig, "optuna_slice_plot.html")
    print("[PASS] Logged slice plot")

except Exception as e:
    print(f"[WARN] Could not create all Optuna visualizations: {e}")

# ===== 6. Summary =====
print("\n" + "="*70)
print("PHASE 3: HYPERPARAMETER OPTIMIZATION - COMPLETE")
print("="*70)

print("\n[RESULTS]")
print(f"  Baseline XGBoost:     R² = 0.9088, RMSE = 4.85 MPa")
print(f"  Optimized XGBoost:    R² = {test_r2:.4f}, RMSE = {test_rmse:.2f} MPa")
print(f"  Improvement:          R² {r2_improvement:+.2f}%, RMSE {rmse_improvement:+.2f}%")

print("\n[OPTUNA OPTIMIZATION]")
print(f"  Total trials:         {len(study.trials)}")
print(f"  Complete trials:      {len([t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE])}")
print(f"  Pruned trials:        {len([t for t in study.trials if t.state == optuna.trial.TrialState.PRUNED])}")
print(f"  Optimization time:    {optimization_time/60:.2f} minutes")
print(f"  Best CV R²:           {best_cv_r2:.4f}")

print("\n[MLFLOW TRACKING]")
print(f"  Experiment:           {EXPERIMENTS['hyperparameter_tuning']}")
print(f"  Run ID:               {run_id}")
print(f"  Model registered:     {MODEL_NAMES['xgboost']} (version 2)")
print(f"  Artifacts logged:     Model, plots, Optuna visualizations")

print("\n[TARGET STATUS]")
if meets_stretch:
    print(f"  [SUCCESS] Stretch target achieved! R² > 0.94, RMSE < 4.0 MPa")
elif meets_primary:
    print(f"  [SUCCESS] Primary target achieved! R² > 0.92, RMSE < 4.5 MPa")
else:
    print(f"  [INFO] Targets not met. Consider:")
    print(f"    - Feature engineering (Phase 4)")
    print(f"    - Ensemble methods (Phase 5)")
    print(f"    - More optimization trials (increase from 200)")

print("\n[NEXT STEPS]")
print("  - Phase 4: Feature Engineering (7 feature sets to test)")
print("  - Phase 5: Ensemble methods (stacking, weighted averaging)")
print("  - Phase 6: Model registry promotion workflow")
print("\n" + "="*70)

print("\n[INFO] To view results in MLflow UI:")
print("  1. Open terminal in project directory")
print("  2. Run: mlflow ui --port 5000")
print("  3. Open: http://localhost:5000")
