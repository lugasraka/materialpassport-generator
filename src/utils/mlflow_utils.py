"""
MLflow Utility Functions

Helper functions for MLflow operations including experiment setup,
logging, model management, and comparison.
"""

import mlflow
import mlflow.sklearn
import mlflow.pytorch
from mlflow.tracking import MlflowClient
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import time
from typing import Dict, List, Optional, Tuple, Any

from src.mlflow_config import (
    MLFLOW_TRACKING_URI,
    EXPERIMENTS,
    MODEL_NAMES,
    TAG_MODEL_FAMILY,
    TAG_MODEL_TYPE,
    TAG_TUNING_METHOD,
    TAG_FEATURE_SET,
    TAG_DATASET_VERSION,
    validate_tags
)


def setup_mlflow_experiment(experiment_key: str, tags: Optional[Dict[str, str]] = None) -> str:
    """
    Initialize MLflow experiment and set tracking URI.

    Args:
        experiment_key (str): Key for the experiment (e.g., 'baseline_models')
        tags (dict, optional): Tags to set on the experiment

    Returns:
        str: Experiment ID
    """
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

    experiment_name = EXPERIMENTS[experiment_key]

    # Create or get experiment
    experiment = mlflow.get_experiment_by_name(experiment_name)

    if experiment is None:
        experiment_id = mlflow.create_experiment(
            name=experiment_name,
            tags=tags
        )
        print(f"Created new experiment: {experiment_name} (ID: {experiment_id})")
    else:
        experiment_id = experiment.experiment_id
        print(f"Using existing experiment: {experiment_name} (ID: {experiment_id})")

    mlflow.set_experiment(experiment_name)

    return experiment_id


def log_model_artifacts(
    model,
    model_type: str,
    scaler=None,
    feature_names: Optional[List[str]] = None,
    register_model: bool = True,
    model_name: Optional[str] = None
):
    """
    Log model, scaler, and related artifacts to MLflow.

    Args:
        model: Trained model (sklearn, pytorch, etc.)
        model_type (str): Type of model ('sklearn', 'pytorch', 'pyfunc')
        scaler: Fitted scaler object (optional)
        feature_names (list, optional): List of feature names
        register_model (bool): Whether to register model in registry
        model_name (str, optional): Name for model registry

    Returns:
        str: Model URI
    """
    # Determine which MLflow module to use
    if model_type == 'sklearn':
        if register_model and model_name:
            model_uri = mlflow.sklearn.log_model(
                model,
                "model",
                registered_model_name=model_name
            ).model_uri
        else:
            model_uri = mlflow.sklearn.log_model(model, "model").model_uri

        # Log scaler if provided
        if scaler is not None:
            mlflow.sklearn.log_model(scaler, "scaler")

    elif model_type == 'pytorch':
        if register_model and model_name:
            model_uri = mlflow.pytorch.log_model(
                model,
                "model",
                registered_model_name=model_name
            ).model_uri
        else:
            model_uri = mlflow.pytorch.log_model(model, "model").model_uri

        # Log scaler if provided
        if scaler is not None:
            mlflow.sklearn.log_model(scaler, "scaler")

    else:
        raise ValueError(f"Unsupported model_type: {model_type}")

    # Log feature names
    if feature_names is not None:
        mlflow.log_dict({"features": feature_names}, "feature_names.json")

    return model_uri


def log_metrics_and_params(
    params: Dict[str, Any],
    metrics: Dict[str, float],
    tags: Optional[Dict[str, str]] = None
):
    """
    Batch log parameters, metrics, and tags to MLflow.

    Args:
        params (dict): Dictionary of parameters
        metrics (dict): Dictionary of metrics
        tags (dict, optional): Dictionary of tags
    """
    # Log parameters
    if params:
        # Convert non-JSON serializable values to strings
        params_clean = {}
        for k, v in params.items():
            if isinstance(v, (list, tuple, np.ndarray)):
                params_clean[k] = str(v)
            elif isinstance(v, (int, float, str, bool)):
                params_clean[k] = v
            else:
                params_clean[k] = str(v)

        mlflow.log_params(params_clean)

    # Log metrics
    if metrics:
        mlflow.log_metrics(metrics)

    # Log and validate tags
    if tags:
        validate_tags(tags)
        mlflow.set_tags(tags)


def log_feature_importance(
    model,
    feature_names: List[str],
    top_n: int = 20,
    figsize: Tuple[int, int] = (10, 8)
) -> Optional[plt.Figure]:
    """
    Log feature importance plot for tree-based models.

    Args:
        model: Trained model with feature_importances_ attribute
        feature_names (list): List of feature names
        top_n (int): Number of top features to plot
        figsize (tuple): Figure size

    Returns:
        Figure: Matplotlib figure object
    """
    if not hasattr(model, 'feature_importances_'):
        print(f"Model {type(model).__name__} does not have feature_importances_")
        return None

    # Create importance dataframe
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    # Log as JSON
    mlflow.log_dict(importance_df.to_dict(orient='records'), "feature_importance.json")

    # Create plot
    fig, ax = plt.subplots(figsize=figsize)
    top_features = importance_df.head(top_n)

    ax.barh(range(len(top_features)), top_features['importance'])
    ax.set_yticks(range(len(top_features)))
    ax.set_yticklabels(top_features['feature'])
    ax.set_xlabel('Importance')
    ax.set_title(f'Top {top_n} Feature Importances')
    ax.invert_yaxis()

    plt.tight_layout()

    # Log figure
    mlflow.log_figure(fig, "feature_importance.png")

    return fig


def log_predictions_vs_actual(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    title: str = "Predictions vs Actual",
    figsize: Tuple[int, int] = (10, 8)
) -> plt.Figure:
    """
    Create and log predictions vs actual plot.

    Args:
        y_true (array): True values
        y_pred (array): Predicted values
        title (str): Plot title
        figsize (tuple): Figure size

    Returns:
        Figure: Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Scatter plot
    ax.scatter(y_true, y_pred, alpha=0.5, edgecolors='k', linewidths=0.5)

    # Perfect prediction line
    min_val = min(y_true.min(), y_pred.min())
    max_val = max(y_true.max(), y_pred.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect Prediction')

    ax.set_xlabel('Actual Values (MPa)')
    ax.set_ylabel('Predicted Values (MPa)')
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    # Log figure
    mlflow.log_figure(fig, "predictions_vs_actual.png")

    return fig


def log_residual_plot(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    figsize: Tuple[int, int] = (12, 5)
) -> plt.Figure:
    """
    Create and log residual analysis plots.

    Args:
        y_true (array): True values
        y_pred (array): Predicted values
        figsize (tuple): Figure size

    Returns:
        Figure: Matplotlib figure object
    """
    residuals = y_true - y_pred

    fig, axes = plt.subplots(1, 2, figsize=figsize)

    # Residuals vs Predicted
    axes[0].scatter(y_pred, residuals, alpha=0.5, edgecolors='k', linewidths=0.5)
    axes[0].axhline(y=0, color='r', linestyle='--', lw=2)
    axes[0].set_xlabel('Predicted Values (MPa)')
    axes[0].set_ylabel('Residuals (MPa)')
    axes[0].set_title('Residual Plot')
    axes[0].grid(True, alpha=0.3)

    # Residual histogram
    axes[1].hist(residuals, bins=30, edgecolor='black', alpha=0.7)
    axes[1].axvline(x=0, color='r', linestyle='--', lw=2)
    axes[1].set_xlabel('Residuals (MPa)')
    axes[1].set_ylabel('Frequency')
    axes[1].set_title('Residual Distribution')
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()

    # Log figure
    mlflow.log_figure(fig, "residual_analysis.png")

    return fig


def load_best_model(
    experiment_name: str,
    metric: str = "test_r2",
    ascending: bool = False,
    model_filter: Optional[str] = None
):
    """
    Load the best model from an experiment based on a metric.

    Args:
        experiment_name (str): Name of the experiment
        metric (str): Metric to optimize (e.g., 'test_r2', 'test_rmse')
        ascending (bool): Whether to sort ascending (True) or descending (False)
        model_filter (str, optional): Filter runs by model_type parameter

    Returns:
        Loaded model object
    """
    client = MlflowClient()

    # Get experiment
    experiment = client.get_experiment_by_name(experiment_name)
    if experiment is None:
        raise ValueError(f"Experiment '{experiment_name}' not found")

    # Build filter string
    filter_string = f"metrics.{metric} > 0"
    if model_filter:
        filter_string += f" and params.model_type = '{model_filter}'"

    # Search for best run
    order = "ASC" if ascending else "DESC"
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string=filter_string,
        order_by=[f"metrics.{metric} {order}"],
        max_results=1
    )

    if not runs:
        raise ValueError(f"No runs found in experiment '{experiment_name}' with metric '{metric}'")

    best_run = runs[0]
    run_id = best_run.info.run_id

    print(f"Loading best model from run: {run_id}")
    print(f"  {metric}: {best_run.data.metrics.get(metric, 'N/A')}")

    # Load model
    model_uri = f"runs:/{run_id}/model"
    model = mlflow.pyfunc.load_model(model_uri)

    return model, best_run


def compare_runs(
    experiment_names: List[str],
    metrics: Optional[List[str]] = None,
    max_results: int = 100
) -> pd.DataFrame:
    """
    Compare runs across one or more experiments.

    Args:
        experiment_names (list): List of experiment names
        metrics (list, optional): Specific metrics to include in comparison
        max_results (int): Maximum number of runs to return

    Returns:
        DataFrame: Comparison of runs
    """
    client = MlflowClient()

    if metrics is None:
        metrics = ['test_r2', 'test_rmse', 'test_mae', 'cv_r2_mean', 'training_time_seconds']

    all_runs = []

    for exp_name in experiment_names:
        experiment = client.get_experiment_by_name(exp_name)
        if experiment is None:
            print(f"Warning: Experiment '{exp_name}' not found")
            continue

        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            filter_string="",
            order_by=["metrics.test_r2 DESC"],
            max_results=max_results
        )
        all_runs.extend(runs)

    # Create comparison dataframe
    comparison_data = []
    for run in all_runs:
        row = {
            'run_id': run.info.run_id,
            'run_name': run.data.tags.get('mlflow.runName', 'unnamed'),
            'experiment_name': run.info.experiment_id,
            'model_type': run.data.params.get('model_type', 'unknown'),
            'start_time': pd.to_datetime(run.info.start_time, unit='ms')
        }

        # Add metrics
        for metric in metrics:
            row[metric] = run.data.metrics.get(metric, None)

        # Add key parameters
        row['feature_set'] = run.data.params.get('feature_set', 'unknown')
        row['tuning_method'] = run.data.tags.get('tuning_method', 'unknown')

        comparison_data.append(row)

    comparison_df = pd.DataFrame(comparison_data)

    # Sort by test_r2 if available
    if 'test_r2' in comparison_df.columns:
        comparison_df = comparison_df.sort_values('test_r2', ascending=False)

    return comparison_df


def register_model_from_run(
    run_id: str,
    model_name: str,
    description: str = "",
    stage: str = "None"
) -> Any:
    """
    Register a model from a specific run.

    Args:
        run_id (str): MLflow run ID
        model_name (str): Name for the registered model
        description (str): Model description
        stage (str): Initial stage ('None', 'Staging', 'Production', 'Archived')

    Returns:
        ModelVersion: Registered model version
    """
    client = MlflowClient()

    # Register model
    model_uri = f"runs:/{run_id}/model"

    result = mlflow.register_model(
        model_uri=model_uri,
        name=model_name
    )

    # Update description
    if description:
        client.update_model_version(
            name=model_name,
            version=result.version,
            description=description
        )

    # Transition to stage
    if stage != "None":
        client.transition_model_version_stage(
            name=model_name,
            version=result.version,
            stage=stage
        )

    print(f"Registered {model_name} version {result.version} in stage '{stage}'")
    print(f"  Run ID: {run_id}")
    print(f"  Description: {description}")

    return result


def promote_model_to_production(
    model_name: str,
    version: int,
    archive_existing: bool = True
) -> bool:
    """
    Promote a model version to production.

    Args:
        model_name (str): Registered model name
        version (int): Version number to promote
        archive_existing (bool): Whether to archive existing production models

    Returns:
        bool: True if promotion successful
    """
    client = MlflowClient()

    try:
        # Archive existing production models if requested
        if archive_existing:
            production_versions = client.get_latest_versions(model_name, stages=["Production"])
            for prod_version in production_versions:
                client.transition_model_version_stage(
                    name=model_name,
                    version=prod_version.version,
                    stage="Archived"
                )
                print(f"Archived {model_name} v{prod_version.version}")

        # Promote new version to production
        client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage="Production"
        )

        print(f"Promoted {model_name} v{version} to Production")
        return True

    except Exception as e:
        print(f"Error promoting model: {e}")
        return False


def create_comparison_dashboard(
    comparison_df: pd.DataFrame,
    figsize: Tuple[int, int] = (16, 12)
) -> plt.Figure:
    """
    Create a comprehensive comparison dashboard for model runs.

    Args:
        comparison_df (DataFrame): DataFrame with run comparison data
        figsize (tuple): Figure size

    Returns:
        Figure: Matplotlib figure object
    """
    fig, axes = plt.subplots(2, 2, figsize=figsize)

    # Top 10 models by R²
    if 'test_r2' in comparison_df.columns:
        top_10 = comparison_df.nlargest(10, 'test_r2')
        axes[0, 0].barh(range(len(top_10)), top_10['test_r2'])
        axes[0, 0].set_yticks(range(len(top_10)))
        axes[0, 0].set_yticklabels(top_10['run_name'], fontsize=8)
        axes[0, 0].set_xlabel('Test R²')
        axes[0, 0].set_title('Top 10 Models - Test R²')
        axes[0, 0].invert_yaxis()

    # RMSE comparison
    if 'test_rmse' in comparison_df.columns:
        top_10_rmse = comparison_df.nsmallest(10, 'test_rmse')
        axes[0, 1].barh(range(len(top_10_rmse)), top_10_rmse['test_rmse'])
        axes[0, 1].set_yticks(range(len(top_10_rmse)))
        axes[0, 1].set_yticklabels(top_10_rmse['run_name'], fontsize=8)
        axes[0, 1].set_xlabel('Test RMSE (MPa)')
        axes[0, 1].set_title('Top 10 Models - Test RMSE')
        axes[0, 1].invert_yaxis()

    # Performance vs Training Time
    if 'training_time_seconds' in comparison_df.columns and 'test_r2' in comparison_df.columns:
        axes[1, 0].scatter(comparison_df['training_time_seconds'], comparison_df['test_r2'], alpha=0.6)
        axes[1, 0].set_xlabel('Training Time (seconds)')
        axes[1, 0].set_ylabel('Test R²')
        axes[1, 0].set_title('Performance vs Training Time')
        axes[1, 0].grid(True, alpha=0.3)

    # Model family comparison
    if 'model_type' in comparison_df.columns and 'test_r2' in comparison_df.columns:
        family_stats = comparison_df.groupby('model_type')['test_r2'].agg(['mean', 'max', 'count'])
        family_stats = family_stats.sort_values('max', ascending=False)

        x = range(len(family_stats))
        axes[1, 1].bar(x, family_stats['max'], alpha=0.7, label='Best')
        axes[1, 1].bar(x, family_stats['mean'], alpha=0.5, label='Mean')
        axes[1, 1].set_xticks(x)
        axes[1, 1].set_xticklabels(family_stats.index, rotation=45, ha='right', fontsize=8)
        axes[1, 1].set_ylabel('Test R²')
        axes[1, 1].set_title('Performance by Model Family')
        axes[1, 1].legend()

    plt.tight_layout()

    return fig


def time_training(func):
    """
    Decorator to time model training and log to MLflow.

    Usage:
        @time_training
        def train_model():
            # training code
            pass
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        training_time = time.time() - start_time

        mlflow.log_metric("training_time_seconds", training_time)
        print(f"Training completed in {training_time:.2f} seconds")

        return result

    return wrapper
