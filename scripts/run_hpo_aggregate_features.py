"""
Phase 4.5: Hyperparameter Optimization with Aggregate Features

Objective: Achieve STRETCH TARGET (R² > 0.94, RMSE < 4.0 MPa)
Current Best: Aggregate features with default hyperparameters (R² = 0.9353, RMSE = 4.08 MPa)

This script runs Optuna optimization (200 trials) specifically with aggregate features,
which showed the best performance in Phase 4 feature engineering.

Aggregate Features = Original 8 + 8 derived features:
- total_binder, total_aggregate, total_solid
- cement_pct, slag_pct, fly_ash_pct
- paste_volume, total_volume
"""

import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from xgboost import XGBRegressor
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

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
print("PHASE 4.5: HYPERPARAMETER OPTIMIZATION WITH AGGREGATE FEATURES")
print("="*70)
print(f"[INFO] MLflow Tracking URI: {MLFLOW_TRACKING_URI}")
print(f"[INFO] STRETCH TARGET: R² > {PERFORMANCE_TARGETS['stretch_r2']}, RMSE < {PERFORMANCE_TARGETS['stretch_rmse']} MPa")
print(f"[INFO] Current Best (Aggregates): R² = 0.9353, RMSE = 4.08 MPa")
print(f"[INFO] Gap to close: +0.47% R², -0.08 MPa RMSE\n")

# ===== 1. Load and Prepare Data with Aggregate Features =====
print("="*70)
print("1. LOADING AND PREPARING DATA WITH AGGREGATE FEATURES")
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
    """Create aggregate statistical features (best performing from Phase 4)"""
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
print(f"  Original features: {', '.join(original_features[:4])}... ({len(original_features)} total)")
print(f"  Aggregate features: {', '.join([f for f in feature_cols if f not in original_features])}")
print()

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE
)

print(f"[PASS] Data split:")
print(f"  Training set: {X_train.shape[0]} samples")
print(f"  Test set: {X_test.shape[0]} samples")
print(f"  Total features: {X_train.shape[1]}\n")

# ===== 2. Setup Optuna Optimization =====
print("="*70)
print("2. XGBOOST HYPERPARAMETER OPTIMIZATION (200 TRIALS)")
print("="*70)

exp_id = setup_mlflow_experiment(
    'hyperparameter_tuning',
    tags={'phase': '4.5', 'model': 'xgboost', 'features': 'aggregates', 'method': 'optuna'}
)
print(f"[PASS] Experiment: {EXPERIMENTS['hyperparameter_tuning']}\n")

# Global variables for objective
X_train_global = X_train
y_train_global = y_train

def objective(trial):
    """Optuna objective function for XGBoost hyperparameter optimization"""
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

    model = XGBRegressor(**params)

    # 5-fold cross-validation
    cv_scores = cross_val_score(
        model, X_train_global, y_train_global,
        cv=5, scoring='r2', n_jobs=-1
    )
    cv_r2_mean = cv_scores.mean()

    trial.report(cv_r2_mean, step=0)

    if trial.should_prune():
        raise optuna.TrialPruned()

    return cv_r2_mean

print("[PASS] Objective function defined")

# Create Optuna study
study = optuna.create_study(
    study_name="xgboost_aggregate_features_optimization",
    direction='maximize',
    pruner=optuna.pruners.MedianPruner(n_startup_trials=10, n_warmup_steps=3),
    sampler=optuna.samplers.TPESampler(seed=RANDOM_STATE)
)

print(f"[PASS] Optuna study created")
print(f"[INFO] Starting optimization with 200 trials...")
print(f"[INFO] Targeting stretch goal: R² > 0.94, RMSE < 4.0 MPa\n")

# Run optimization
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
    show_progress_bar=False
)

optimization_time = time.time() - start_time

print(f"[PASS] Optimization complete in {optimization_time/60:.2f} minutes")
print(f"[INFO] Total trials: {len(study.trials)}")
print(f"[INFO] Complete trials: {len([t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE])}")
print(f"[INFO] Pruned trials: {len([t for t in study.trials if t.state == optuna.trial.TrialState.PRUNED])}\n")

# ===== 3. Evaluate Best Model =====
print("="*70)
print("3. EVALUATING BEST MODEL")
print("="*70)

best_params = study.best_params
best_cv_r2 = study.best_value

print("[PASS] BEST HYPERPARAMETERS FOUND:")
print("="*70)
for param, value in best_params.items():
    print(f"  {param:.<30} {value}")
print("="*70)
print(f"  Best CV R²: {best_cv_r2:.4f}\n")

# Train best model
best_model = XGBRegressor(
    **best_params,
    random_state=RANDOM_STATE,
    n_jobs=-1
)

start_train = time.time()
best_model.fit(X_train, y_train)
training_time = time.time() - start_train

# Predictions and metrics
y_pred_train = best_model.predict(X_train)
y_pred_test = best_model.predict(X_test)

train_r2 = r2_score(y_train, y_pred_train)
test_r2 = r2_score(y_test, y_pred_test)
test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
test_mae = mean_absolute_error(y_test, y_pred_test)

cv_scores = cross_val_score(best_model, X_train, y_train, cv=5, scoring='r2')
cv_r2_mean = cv_scores.mean()
cv_r2_std = cv_scores.std()

print("[PASS] OPTIMIZED MODEL PERFORMANCE:")
print("="*70)
print(f"  Train R²: {train_r2:.4f}")
print(f"  Test R²: {test_r2:.4f}")
print(f"  Test RMSE: {test_rmse:.2f} MPa")
print(f"  Test MAE: {test_mae:.2f} MPa")
print(f"  CV R² (mean ± std): {cv_r2_mean:.4f} ± {cv_r2_std:.4f}")
print(f"  Training time: {training_time:.2f} seconds")
print("="*70)

# Check targets
meets_primary = meets_performance_target(test_r2, test_rmse, 'primary')
meets_stretch = meets_performance_target(test_r2, test_rmse, 'stretch')

if meets_stretch:
    print(f"\n[SUCCESS] STRETCH TARGET ACHIEVED!")
    print(f"  R² > 0.94: {test_r2:.4f} (target: 0.94)")
    print(f"  RMSE < 4.0: {test_rmse:.2f} MPa (target: 4.0 MPa)")
elif meets_primary:
    print(f"\n[SUCCESS] Primary target achieved!")
    print(f"  R² > 0.92: {test_r2:.4f}")
    print(f"  RMSE < 4.5: {test_rmse:.2f} MPa")
    print(f"\n[INFO] Stretch target status:")
    print(f"  R² gap: {0.94 - test_r2:.4f} (need {(0.94 - test_r2) / test_r2 * 100:+.2f}%)")
    print(f"  RMSE gap: {test_rmse - 4.0:.2f} MPa (need {(4.0 - test_rmse) / test_rmse * 100:+.2f}%)")
else:
    print(f"\n[INFO] Targets not met")

# Compare with Phase 4 baseline (aggregate features, default hyperparameters)
phase4_r2 = 0.9353
phase4_rmse = 4.08
r2_improvement = (test_r2 - phase4_r2) / phase4_r2 * 100
rmse_improvement = (phase4_rmse - test_rmse) / phase4_rmse * 100

print(f"\n[COMPARISON] vs. Phase 4 (Aggregate features, default hyperparams):")
print(f"  R² improvement: {r2_improvement:+.2f}%")
print(f"  RMSE improvement: {rmse_improvement:+.2f}%")

# Compare with original baseline
baseline_r2 = 0.9088
baseline_rmse = 4.85
total_r2_improvement = (test_r2 - baseline_r2) / baseline_r2 * 100
total_rmse_improvement = (baseline_rmse - test_rmse) / baseline_rmse * 100

print(f"\n[TOTAL IMPROVEMENT] vs. Original Baseline (Phase 2):")
print(f"  R² improvement: {total_r2_improvement:+.2f}%")
print(f"  RMSE improvement: {total_rmse_improvement:+.2f}%")

# ===== 4. Log to MLflow =====
print("\n" + "="*70)
print("4. LOGGING TO MLFLOW")
print("="*70)

with mlflow.start_run(run_name="xgboost_aggregate_features_optuna_best") as run:
    params = {
        **best_params,
        'model_type': 'xgboost',
        'feature_set': 'engineered',
        'feature_details': 'aggregate_features',
        'n_features': len(feature_cols),
        'test_size': 0.2,
        'cv_folds': 5,
        'optimization_method': 'optuna',
        'optimization_trials': len(study.trials),
        'optimization_time_minutes': optimization_time / 60
    }

    metrics = {
        'train_r2': train_r2,
        'test_r2': test_r2,
        'test_rmse': test_rmse,
        'test_mae': test_mae,
        'cv_r2_mean': cv_r2_mean,
        'cv_r2_std': cv_r2_std,
        'training_time_seconds': training_time,
        'r2_improvement_vs_phase4_pct': r2_improvement,
        'rmse_improvement_vs_phase4_pct': rmse_improvement,
        'r2_improvement_vs_baseline_pct': total_r2_improvement,
        'rmse_improvement_vs_baseline_pct': total_rmse_improvement
    }

    tags = {
        'model_family': 'baseline',
        'model_type': 'xgboost',
        'tuning_method': 'optuna',
        'feature_set': 'engineered',
        'phase': '4.5',
        'feature_details': 'aggregate_features',
        'target_met': 'stretch' if meets_stretch else ('primary' if meets_primary else 'no'),
        'best_overall': 'true' if meets_stretch else 'false'
    }

    log_metrics_and_params(params, metrics, tags)
    print(f"[PASS] Logged {len(params)} parameters, {len(metrics)} metrics, {len(tags)} tags")

    # Register model if it meets stretch goal or is better than previous best
    should_register = meets_stretch or (test_r2 > 0.9353)

    log_model_artifacts(
        model=best_model,
        model_type='sklearn',
        feature_names=feature_cols,
        register_model=should_register,
        model_name=MODEL_NAMES['xgboost'] if should_register else None
    )

    if should_register:
        print(f"[PASS] Model registered: {MODEL_NAMES['xgboost']} (new version)")
    else:
        print(f"[PASS] Model artifacts logged (not registered)")

    # Log plots
    fig = log_feature_importance(best_model, feature_cols, top_n=16)
    if fig:
        plt.close(fig)
        print(f"[PASS] Logged feature importance plot")

    fig = log_predictions_vs_actual(y_test.values, y_pred_test,
                                   title="Predictions vs Actual (Aggregate Features)")
    plt.close(fig)
    print(f"[PASS] Logged predictions vs actual plot")

    fig = log_residual_plot(y_test.values, y_pred_test)
    plt.close(fig)
    print(f"[PASS] Logged residual plot")

    run_id = run.info.run_id
    print(f"\n[PASS] MLflow Run ID: {run_id}")

# ===== 5. Optuna Visualizations =====
print("\n" + "="*70)
print("5. CREATING OPTUNA VISUALIZATIONS")
print("="*70)

try:
    # Optimization history
    fig = optuna.visualization.plot_optimization_history(study)
    fig.update_layout(title="Optuna Optimization History (Aggregate Features)")
    mlflow.log_figure(fig, "optuna_aggregate_optimization_history.html")
    print("[PASS] Logged optimization history")

    # Parameter importance
    fig = optuna.visualization.plot_param_importances(study)
    fig.update_layout(title="Hyperparameter Importance (Aggregate Features)")
    mlflow.log_figure(fig, "optuna_aggregate_param_importances.html")
    print("[PASS] Logged parameter importance")

    # Parallel coordinate
    fig = optuna.visualization.plot_parallel_coordinate(study)
    fig.update_layout(title="Parallel Coordinate Plot (Aggregate Features)")
    mlflow.log_figure(fig, "optuna_aggregate_parallel_coordinate.html")
    print("[PASS] Logged parallel coordinate plot")

except Exception as e:
    print(f"[WARN] Could not create all visualizations: {e}")

# ===== 6. Final Summary =====
print("\n" + "="*70)
print("PHASE 4.5: AGGREGATE FEATURES OPTIMIZATION - COMPLETE")
print("="*70)

print("\n[OPTIMIZATION JOURNEY]")
print(f"  Phase 2 Baseline:        R² = 0.9088, RMSE = 4.85 MPa")
print(f"  Phase 3 (HPO):           R² = 0.9314, RMSE = 4.20 MPa")
print(f"  Phase 4 (Aggregates):    R² = 0.9353, RMSE = 4.08 MPa")
print(f"  Phase 4.5 (Agg + HPO):   R² = {test_r2:.4f}, RMSE = {test_rmse:.2f} MPa")

print(f"\n[FINAL RESULTS]")
print(f"  Test R²:                 {test_r2:.4f}")
print(f"  Test RMSE:               {test_rmse:.2f} MPa")
print(f"  Test MAE:                {test_mae:.2f} MPa")
print(f"  CV R²:                   {cv_r2_mean:.4f} ± {cv_r2_std:.4f}")
print(f"  Features:                {len(feature_cols)} (8 original + 8 aggregate)")

print(f"\n[TOTAL IMPROVEMENT vs. Baseline]")
print(f"  R² improvement:          {total_r2_improvement:+.2f}%")
print(f"  RMSE improvement:        {total_rmse_improvement:+.2f}%")
print(f"  Absolute RMSE reduction: {baseline_rmse - test_rmse:.2f} MPa")

print(f"\n[TARGET STATUS]")
if meets_stretch:
    print(f"  [SUCCESS] STRETCH TARGET ACHIEVED!")
    print(f"    R² > 0.94: ACHIEVED ({test_r2:.4f})")
    print(f"    RMSE < 4.0: ACHIEVED ({test_rmse:.2f} MPa)")
elif meets_primary:
    print(f"  [SUCCESS] Primary target achieved")
    print(f"  [INFO] Stretch target not met:")
    print(f"    R² gap: {max(0, 0.94 - test_r2):.4f}")
    print(f"    RMSE gap: {max(0, test_rmse - 4.0):.2f} MPa")

print(f"\n[OPTUNA SUMMARY]")
print(f"  Total trials:            {len(study.trials)}")
print(f"  Complete trials:         {len([t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE])}")
print(f"  Optimization time:       {optimization_time/60:.2f} minutes")
print(f"  Best CV R²:              {best_cv_r2:.4f}")

print(f"\n[MLFLOW TRACKING]")
print(f"  Experiment:              {EXPERIMENTS['hyperparameter_tuning']}")
print(f"  Run ID:                  {run_id}")
if should_register:
    print(f"  Model registered:        {MODEL_NAMES['xgboost']} (latest version)")
print(f"  Artifacts:               Model, plots, Optuna visualizations")

print(f"\n[NEXT STEPS]")
if meets_stretch:
    print(f"  - Phase 5: Ensemble methods (optional - already at stretch goal)")
    print(f"  - Phase 6: Model registry promotion to Production")
    print(f"  - Deploy best model to web application")
else:
    print(f"  - Phase 5: Ensemble methods (combine multiple models)")
    print(f"  - Alternative: Accept current excellent performance and deploy")

print("\n" + "="*70)
