"""
MLflow Configuration Module

Centralized configuration for MLflow tracking across the Material Passport Generator project.
"""

import os

# MLflow Tracking Configuration
MLFLOW_TRACKING_URI = "file:./mlruns"
ARTIFACT_LOCATION = "./mlflow_artifacts"

# Experiment Names
EXPERIMENTS = {
    "baseline_models": "Concrete-Baseline-Models",
    "deep_learning": "Concrete-Deep-Learning",
    "hyperparameter_tuning": "Concrete-HPO",
    "feature_engineering": "Concrete-Feature-Engineering",
    "ensemble": "Concrete-Ensemble-Models"
}

# Model Registry Names
MODEL_NAMES = {
    "linear_regression": "concrete_strength_linear_regression",
    "random_forest": "concrete_strength_random_forest",
    "xgboost": "concrete_strength_xgboost",
    "simple_nn": "concrete_strength_simple_nn",
    "deep_nn": "concrete_strength_deep_nn",
    "multitask_nn": "concrete_strength_multitask_nn",
    "ensemble_stacking": "concrete_strength_ensemble_stacking",
    "ensemble_weighted": "concrete_strength_ensemble_weighted"
}

# Tagging Taxonomy
TAG_MODEL_FAMILY = "model_family"
TAG_MODEL_TYPE = "model_type"
TAG_TUNING_METHOD = "tuning_method"
TAG_FEATURE_SET = "feature_set"
TAG_DATASET_VERSION = "dataset_version"
TAG_CREATOR = "creator"
TAG_STATUS = "status"
TAG_PRIORITY = "priority"

# Tag Values
MODEL_FAMILIES = ["baseline", "deep_learning", "ensemble"]
TUNING_METHODS = ["default", "grid_search", "random_search", "optuna", "manual"]
FEATURE_SETS = ["original", "engineered", "selected", "optimized"]
STATUS_VALUES = ["experimental", "validated", "production"]
PRIORITY_VALUES = ["low", "medium", "high"]

# Performance Thresholds
PERFORMANCE_TARGETS = {
    "primary_r2": 0.92,
    "primary_rmse": 4.5,
    "stretch_r2": 0.94,
    "stretch_rmse": 4.0,
    "minimum_improvement_r2": 0.01,
    "minimum_improvement_rmse": 0.3
}

# Promotion Criteria for Model Registry
PROMOTION_CRITERIA = {
    "min_test_r2": 0.90,
    "max_test_rmse": 5.0,
    "max_outlier_rate": 0.05,
    "min_prediction": 0,
    "max_prediction": 150  # MPa
}

# Directory Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
MLRUNS_DIR = os.path.join(PROJECT_ROOT, "mlruns")
ARTIFACTS_DIR = os.path.join(PROJECT_ROOT, "mlflow_artifacts")

def get_tracking_uri():
    """Get the MLflow tracking URI."""
    return MLFLOW_TRACKING_URI

def get_experiment_name(experiment_key):
    """
    Get the experiment name for a given key.

    Args:
        experiment_key (str): Key for the experiment (e.g., 'baseline_models')

    Returns:
        str: Experiment name

    Raises:
        KeyError: If experiment_key is not valid
    """
    if experiment_key not in EXPERIMENTS:
        raise KeyError(f"Invalid experiment key: {experiment_key}. "
                      f"Valid keys: {list(EXPERIMENTS.keys())}")
    return EXPERIMENTS[experiment_key]

def get_model_name(model_key):
    """
    Get the registered model name for a given key.

    Args:
        model_key (str): Key for the model (e.g., 'xgboost')

    Returns:
        str: Registered model name

    Raises:
        KeyError: If model_key is not valid
    """
    if model_key not in MODEL_NAMES:
        raise KeyError(f"Invalid model key: {model_key}. "
                      f"Valid keys: {list(MODEL_NAMES.keys())}")
    return MODEL_NAMES[model_key]

def validate_tags(tags):
    """
    Validate MLflow tags against the defined taxonomy.

    Args:
        tags (dict): Dictionary of tags to validate

    Returns:
        bool: True if all tags are valid

    Raises:
        ValueError: If any tag has an invalid value
    """
    if TAG_MODEL_FAMILY in tags:
        if tags[TAG_MODEL_FAMILY] not in MODEL_FAMILIES:
            raise ValueError(f"Invalid {TAG_MODEL_FAMILY}: {tags[TAG_MODEL_FAMILY]}. "
                           f"Valid values: {MODEL_FAMILIES}")

    if TAG_TUNING_METHOD in tags:
        if tags[TAG_TUNING_METHOD] not in TUNING_METHODS:
            raise ValueError(f"Invalid {TAG_TUNING_METHOD}: {tags[TAG_TUNING_METHOD]}. "
                           f"Valid values: {TUNING_METHODS}")

    if TAG_FEATURE_SET in tags:
        if tags[TAG_FEATURE_SET] not in FEATURE_SETS:
            raise ValueError(f"Invalid {TAG_FEATURE_SET}: {tags[TAG_FEATURE_SET]}. "
                           f"Valid values: {FEATURE_SETS}")

    if TAG_STATUS in tags:
        if tags[TAG_STATUS] not in STATUS_VALUES:
            raise ValueError(f"Invalid {TAG_STATUS}: {tags[TAG_STATUS]}. "
                           f"Valid values: {STATUS_VALUES}")

    if TAG_PRIORITY in tags:
        if tags[TAG_PRIORITY] not in PRIORITY_VALUES:
            raise ValueError(f"Invalid {TAG_PRIORITY}: {tags[TAG_PRIORITY]}. "
                           f"Valid values: {PRIORITY_VALUES}")

    return True

def meets_performance_target(r2, rmse, target_type="primary"):
    """
    Check if model performance meets target thresholds.

    Args:
        r2 (float): R² score
        rmse (float): RMSE value
        target_type (str): Type of target ('primary' or 'stretch')

    Returns:
        bool: True if performance meets target
    """
    if target_type == "primary":
        return r2 >= PERFORMANCE_TARGETS["primary_r2"] and rmse <= PERFORMANCE_TARGETS["primary_rmse"]
    elif target_type == "stretch":
        return r2 >= PERFORMANCE_TARGETS["stretch_r2"] and rmse <= PERFORMANCE_TARGETS["stretch_rmse"]
    else:
        raise ValueError(f"Invalid target_type: {target_type}. Use 'primary' or 'stretch'")

def meets_promotion_criteria(test_r2, test_rmse, outlier_rate, predictions):
    """
    Check if model meets criteria for promotion to production.

    Args:
        test_r2 (float): Test set R² score
        test_rmse (float): Test set RMSE
        outlier_rate (float): Proportion of outlier predictions
        predictions (array-like): Model predictions

    Returns:
        bool: True if model meets all promotion criteria
    """
    import numpy as np

    # Check performance thresholds
    performance_ok = (test_r2 >= PROMOTION_CRITERIA["min_test_r2"] and
                     test_rmse <= PROMOTION_CRITERIA["max_test_rmse"])

    # Check outlier rate
    outliers_ok = outlier_rate <= PROMOTION_CRITERIA["max_outlier_rate"]

    # Check prediction range
    predictions = np.array(predictions)
    range_ok = (np.all(predictions >= PROMOTION_CRITERIA["min_prediction"]) and
               np.all(predictions <= PROMOTION_CRITERIA["max_prediction"]))

    # Check for invalid values
    valid_ok = not (np.isnan(predictions).any() or np.isinf(predictions).any())

    return performance_ok and outliers_ok and range_ok and valid_ok
