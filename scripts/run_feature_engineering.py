"""
Phase 4: Feature Engineering Experiments with MLflow

Objective: Test multiple feature sets to achieve stretch target (R² > 0.94, RMSE < 4.0 MPa)
Current Best: XGBoost with optimized hyperparameters (R² = 0.9314, RMSE = 4.20 MPa)

This script tests 7 feature sets:
1. Original (8 features) - baseline
2. Interaction features
3. Ratio features
4. Polynomial features (degree 2)
5. Aggregate features
6. All engineered features combined
7. Selected best features (based on feature importance)
"""

import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.feature_selection import SelectKBest, f_regression
from xgboost import XGBRegressor
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# MLflow
import mlflow
import mlflow.sklearn

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

# Best hyperparameters from Phase 3
BEST_PARAMS = {
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

print("="*70)
print("PHASE 4: FEATURE ENGINEERING EXPERIMENTS")
print("="*70)
print(f"[INFO] MLflow Tracking URI: {MLFLOW_TRACKING_URI}")
print(f"[INFO] Performance Targets: R² > {PERFORMANCE_TARGETS['primary_r2']}, RMSE < {PERFORMANCE_TARGETS['primary_rmse']} MPa")
print(f"[INFO] Stretch Target: R² > {PERFORMANCE_TARGETS['stretch_r2']}, RMSE < {PERFORMANCE_TARGETS['stretch_rmse']} MPa")
print(f"[INFO] Current Best: R² = 0.9314, RMSE = 4.20 MPa\n")

# ===== 1. Load and Prepare Data =====
print("="*70)
print("1. LOADING DATA")
print("="*70)

data_path = Path('data/processed/concrete_enriched.csv')

if not data_path.exists():
    print("[ERROR] Dataset not found!")
    sys.exit(1)

df = pd.read_csv(data_path)
print(f"[PASS] Dataset loaded: {df.shape[0]} samples, {df.shape[1]} features\n")

# Original features
original_features = [
    'cement', 'slag', 'fly_ash', 'water', 'superplasticizer',
    'coarse_aggregate', 'fine_aggregate', 'age'
]

# ===== 2. Feature Engineering Functions =====
print("="*70)
print("2. DEFINING FEATURE SETS")
print("="*70)

def create_interaction_features(df):
    """Create interaction features between key components"""
    df_new = df.copy()

    # Cement interactions (most important)
    df_new['cement_water'] = df['cement'] * df['water']
    df_new['cement_age'] = df['cement'] * df['age']
    df_new['cement_superplasticizer'] = df['cement'] * df['superplasticizer']

    # Water interactions
    df_new['water_age'] = df['water'] * df['age']
    df_new['water_superplasticizer'] = df['water'] * df['superplasticizer']

    # Binder interactions
    df_new['cement_slag'] = df['cement'] * df['slag']
    df_new['cement_fly_ash'] = df['cement'] * df['fly_ash']

    # Aggregate interactions
    df_new['coarse_fine_aggregate'] = df['coarse_aggregate'] * df['fine_aggregate']

    return df_new

def create_ratio_features(df):
    """Create ratio features"""
    df_new = df.copy()

    # Water-to-binder ratios
    total_binder = df['cement'] + df['slag'] + df['fly_ash']
    df_new['water_cement_ratio'] = df['water'] / (df['cement'] + 1e-6)
    df_new['water_binder_ratio'] = df['water'] / (total_binder + 1e-6)

    # Binder composition ratios
    df_new['slag_cement_ratio'] = df['slag'] / (df['cement'] + 1e-6)
    df_new['fly_ash_cement_ratio'] = df['fly_ash'] / (df['cement'] + 1e-6)
    df_new['supplementary_binder_ratio'] = (df['slag'] + df['fly_ash']) / (total_binder + 1e-6)

    # Aggregate ratios
    total_aggregate = df['coarse_aggregate'] + df['fine_aggregate']
    df_new['fine_aggregate_ratio'] = df['fine_aggregate'] / (total_aggregate + 1e-6)
    df_new['aggregate_binder_ratio'] = total_aggregate / (total_binder + 1e-6)

    # Superplasticizer efficiency
    df_new['superplasticizer_cement_ratio'] = df['superplasticizer'] / (df['cement'] + 1e-6)

    # Age factors
    df_new['cement_age_ratio'] = df['cement'] / (df['age'] + 1e-6)

    return df_new

def create_aggregate_features(df):
    """Create aggregate statistical features"""
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

def create_polynomial_features(df, degree=2):
    """Create polynomial features"""
    poly = PolynomialFeatures(degree=degree, include_bias=False)
    feature_names = df.columns.tolist()

    poly_features = poly.fit_transform(df)
    poly_feature_names = poly.get_feature_names_out(feature_names)

    return pd.DataFrame(poly_features, columns=poly_feature_names, index=df.index)

# ===== 3. Define Feature Sets =====
feature_sets = {}

# Set 1: Original features (baseline)
feature_sets['original'] = {
    'name': 'Original 8 Features',
    'description': 'Baseline with original features only',
    'features': original_features
}

# Set 2: Original + Interaction features
df_interactions = create_interaction_features(df[original_features])
interaction_cols = [col for col in df_interactions.columns if col not in original_features]
feature_sets['interactions'] = {
    'name': 'Original + Interactions',
    'description': 'Original features plus interaction terms',
    'features': original_features + interaction_cols
}

# Set 3: Original + Ratio features
df_ratios = create_ratio_features(df[original_features])
ratio_cols = [col for col in df_ratios.columns if col not in original_features]
feature_sets['ratios'] = {
    'name': 'Original + Ratios',
    'description': 'Original features plus ratio features',
    'features': original_features + ratio_cols
}

# Set 4: Original + Aggregate features
df_aggregates = create_aggregate_features(df[original_features])
aggregate_cols = [col for col in df_aggregates.columns if col not in original_features]
feature_sets['aggregates'] = {
    'name': 'Original + Aggregates',
    'description': 'Original features plus aggregate statistics',
    'features': original_features + aggregate_cols
}

# Set 5: Polynomial features (degree 2)
# We'll create this during training to avoid memory issues

# Set 6: All engineered features combined
df_all = df[original_features].copy()
df_all = create_interaction_features(df_all)
df_all = create_ratio_features(df_all)
df_all = create_aggregate_features(df_all)
all_cols = df_all.columns.tolist()
feature_sets['all_combined'] = {
    'name': 'All Engineered Features',
    'description': 'Original + interactions + ratios + aggregates',
    'features': all_cols
}

print(f"[PASS] Feature sets defined:")
for key, fset in feature_sets.items():
    if key != 'polynomial':
        print(f"  {key:.<20} {len(fset['features']):>3} features - {fset['name']}")
print(f"  {'polynomial':.<20} TBD features - Polynomial degree 2 (calculated during training)")
print()

# ===== 4. Setup MLflow Experiment =====
exp_id = setup_mlflow_experiment(
    'feature_engineering',
    tags={'phase': '4', 'model': 'xgboost', 'method': 'feature_engineering'}
)
print(f"[PASS] Experiment: {EXPERIMENTS['feature_engineering']} (ID: {exp_id})\n")

# ===== 5. Train and Evaluate Each Feature Set =====
print("="*70)
print("3. TRAINING MODELS WITH DIFFERENT FEATURE SETS")
print("="*70)

results = []

def train_and_evaluate(X_train, X_test, y_train, y_test, feature_set_name, feature_set_info):
    """Train model and evaluate performance"""

    print(f"\n[{feature_set_name.upper()}] {feature_set_info['name']}")
    print(f"  Description: {feature_set_info['description']}")
    print(f"  Features: {len(X_train.columns)}")

    # Train model
    model = XGBRegressor(**BEST_PARAMS)

    start_time = time.time()
    model.fit(X_train, y_train)
    training_time = time.time() - start_time

    # Predictions
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)

    # Metrics
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    test_mae = mean_absolute_error(y_test, y_pred_test)

    # Cross-validation
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2', n_jobs=-1)
    cv_r2_mean = cv_scores.mean()
    cv_r2_std = cv_scores.std()

    print(f"  Train R²: {train_r2:.4f}")
    print(f"  Test R²: {test_r2:.4f}")
    print(f"  Test RMSE: {test_rmse:.2f} MPa")
    print(f"  CV R²: {cv_r2_mean:.4f} ± {cv_r2_std:.4f}")

    # Check targets
    meets_primary = meets_performance_target(test_r2, test_rmse, 'primary')
    meets_stretch = meets_performance_target(test_r2, test_rmse, 'stretch')

    if meets_stretch:
        print(f"  [SUCCESS] Stretch target achieved!")
    elif meets_primary:
        print(f"  [SUCCESS] Primary target achieved!")

    # Log to MLflow
    with mlflow.start_run(run_name=f"xgboost_{feature_set_name}") as run:
        params = {
            **BEST_PARAMS,
            'feature_set': feature_set_name,
            'feature_set_name': feature_set_info['name'],
            'n_features': len(X_train.columns),
            'test_size': 0.2,
            'cv_folds': 5
        }

        metrics = {
            'train_r2': train_r2,
            'test_r2': test_r2,
            'test_rmse': test_rmse,
            'test_mae': test_mae,
            'cv_r2_mean': cv_r2_mean,
            'cv_r2_std': cv_r2_std,
            'training_time_seconds': training_time
        }

        tags = {
            'model_family': 'baseline',
            'model_type': 'xgboost',
            'feature_engineering': feature_set_name,
            'target_met': 'stretch' if meets_stretch else ('primary' if meets_primary else 'no')
        }

        log_metrics_and_params(params, metrics, tags)

        # Log model artifacts (only register if it beats current best)
        register = meets_stretch or (test_r2 > 0.9314)
        log_model_artifacts(
            model=model,
            model_type='sklearn',
            feature_names=X_train.columns.tolist(),
            register_model=False  # Don't auto-register, we'll do it manually for best
        )

        # Log plots
        if len(X_train.columns) <= 50:  # Only for reasonable number of features
            fig = log_feature_importance(model, X_train.columns.tolist(), top_n=20)
            if fig:
                plt.close(fig)

        fig = log_predictions_vs_actual(y_test.values, y_pred_test,
                                       title=f"Predictions vs Actual ({feature_set_info['name']})")
        plt.close(fig)

        fig = log_residual_plot(y_test.values, y_pred_test)
        plt.close(fig)

        run_id = run.info.run_id

    # Store results
    result = {
        'feature_set': feature_set_name,
        'feature_set_name': feature_set_info['name'],
        'n_features': len(X_train.columns),
        'train_r2': train_r2,
        'test_r2': test_r2,
        'test_rmse': test_rmse,
        'test_mae': test_mae,
        'cv_r2_mean': cv_r2_mean,
        'cv_r2_std': cv_r2_std,
        'training_time': training_time,
        'meets_primary': meets_primary,
        'meets_stretch': meets_stretch,
        'run_id': run_id
    }

    return result

# Prepare target
y = df['strength']

# Train-test split
X_train_idx, X_test_idx, y_train, y_test = train_test_split(
    df.index, y, test_size=0.2, random_state=RANDOM_STATE
)

# Test each feature set
for key, fset in feature_sets.items():
    if key == 'original':
        X_full = df[original_features].copy()
    elif key == 'interactions':
        X_full = create_interaction_features(df[original_features])
    elif key == 'ratios':
        X_full = create_ratio_features(df[original_features])
    elif key == 'aggregates':
        X_full = create_aggregate_features(df[original_features])
    elif key == 'all_combined':
        X_full = df[original_features].copy()
        X_full = create_interaction_features(X_full)
        X_full = create_ratio_features(X_full)
        X_full = create_aggregate_features(X_full)

    X_full = X_full[fset['features']]
    X_train = X_full.loc[X_train_idx]
    X_test = X_full.loc[X_test_idx]

    result = train_and_evaluate(X_train, X_test, y_train, y_test, key, fset)
    results.append(result)

# Test polynomial features separately (can be large)
print(f"\n[POLYNOMIAL] Polynomial Features (degree 2)")
print(f"  Description: Polynomial expansion of original features")

X_orig_train = df.loc[X_train_idx, original_features]
X_orig_test = df.loc[X_test_idx, original_features]

poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly_train = poly.fit_transform(X_orig_train)
X_poly_test = poly.transform(X_orig_test)

poly_feature_names = poly.get_feature_names_out(original_features)
X_poly_train_df = pd.DataFrame(X_poly_train, columns=poly_feature_names, index=X_train_idx)
X_poly_test_df = pd.DataFrame(X_poly_test, columns=poly_feature_names, index=X_test_idx)

print(f"  Features: {len(poly_feature_names)}")

result = train_and_evaluate(
    X_poly_train_df, X_poly_test_df, y_train, y_test,
    'polynomial',
    {'name': 'Polynomial Features (degree 2)', 'description': 'Polynomial expansion', 'features': poly_feature_names}
)
results.append(result)

# ===== 6. Feature Selection - Select Best K Features =====
print(f"\n[SELECTED] Selected Best Features")
print(f"  Description: Top K features from all combined features")

# Use all combined features as base
X_full_train = df.loc[X_train_idx, original_features].copy()
X_full_train = create_interaction_features(X_full_train)
X_full_train = create_ratio_features(X_full_train)
X_full_train = create_aggregate_features(X_full_train)

X_full_test = df.loc[X_test_idx, original_features].copy()
X_full_test = create_interaction_features(X_full_test)
X_full_test = create_ratio_features(X_full_test)
X_full_test = create_aggregate_features(X_full_test)

# Select best K features
k_best = 20  # Select top 20 features
selector = SelectKBest(score_func=f_regression, k=k_best)
X_selected_train = selector.fit_transform(X_full_train, y_train)
X_selected_test = selector.transform(X_full_test)

selected_feature_names = X_full_train.columns[selector.get_support()].tolist()
X_selected_train_df = pd.DataFrame(X_selected_train, columns=selected_feature_names, index=X_train_idx)
X_selected_test_df = pd.DataFrame(X_selected_test, columns=selected_feature_names, index=X_test_idx)

print(f"  Features: {k_best}")
print(f"  Selected: {', '.join(selected_feature_names[:5])}... (showing first 5)")

result = train_and_evaluate(
    X_selected_train_df, X_selected_test_df, y_train, y_test,
    'selected',
    {'name': f'Selected Best {k_best} Features', 'description': 'Feature selection', 'features': selected_feature_names}
)
results.append(result)

# ===== 7. Summary and Comparison =====
print("\n" + "="*70)
print("PHASE 4: FEATURE ENGINEERING - COMPLETE")
print("="*70)

# Create results DataFrame
results_df = pd.DataFrame(results)
results_df = results_df.sort_values('test_r2', ascending=False)

print("\n[RESULTS COMPARISON] (Sorted by Test R²)")
print("="*70)
print(f"{'Feature Set':<30} {'Features':>8} {'Test R²':>10} {'RMSE':>8} {'Target':>10}")
print("-"*70)

for _, row in results_df.iterrows():
    target_status = '✓ Stretch' if row['meets_stretch'] else ('✓ Primary' if row['meets_primary'] else 'Not Met')
    print(f"{row['feature_set_name']:<30} {row['n_features']:>8} {row['test_r2']:>10.4f} {row['test_rmse']:>8.2f} {target_status:>10}")

print("="*70)

# Best model
best_result = results_df.iloc[0]
print(f"\n[BEST MODEL]")
print(f"  Feature Set: {best_result['feature_set_name']}")
print(f"  Features: {best_result['n_features']}")
print(f"  Test R²: {best_result['test_r2']:.4f}")
print(f"  Test RMSE: {best_result['test_rmse']:.2f} MPa")
print(f"  CV R²: {best_result['cv_r2_mean']:.4f} ± {best_result['cv_r2_std']:.4f}")
print(f"  MLflow Run ID: {best_result['run_id']}")

# Compare with Phase 3 best
phase3_r2 = 0.9314
phase3_rmse = 4.20
improvement_r2 = (best_result['test_r2'] - phase3_r2) / phase3_r2 * 100
improvement_rmse = (phase3_rmse - best_result['test_rmse']) / phase3_rmse * 100

print(f"\n[COMPARISON] vs. Phase 3 Best (Original Features)")
print(f"  R² improvement: {improvement_r2:+.2f}%")
print(f"  RMSE improvement: {improvement_rmse:+.2f}%")

if best_result['meets_stretch']:
    print(f"\n[SUCCESS] Stretch target achieved! R² > 0.94, RMSE < 4.0 MPa")
elif best_result['meets_primary']:
    print(f"\n[SUCCESS] Primary target maintained! R² > 0.92, RMSE < 4.5 MPa")
else:
    print(f"\n[INFO] No improvement over Phase 3. Original features remain best.")

print(f"\n[NEXT STEPS]")
print(f"  - Phase 5: Ensemble methods (combine multiple models)")
print(f"  - Phase 6: Model registry and promotion workflow")
print(f"  - Deploy best model to production")

print("\n" + "="*70)
