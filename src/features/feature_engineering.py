"""
Feature Engineering Functions
==============================

This module contains functions for creating engineered features
to improve ML model performance.

Features include:
- Interaction features
- Polynomial features
- Ratio features
- Domain-specific features
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import PolynomialFeatures


def create_interaction_features(df):
    """
    Create interaction features between key components.

    Interaction features capture the combined effect of multiple features.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with original features

    Returns:
    --------
    pd.DataFrame
        DataFrame with added interaction features
    """
    df_new = df.copy()

    # Cement-Water interaction (hydration potential)
    df_new['cement_water_interaction'] = df['cement'] * df['water']

    # Recycled materials and age (pozzolanic reaction)
    df_new['recycled_age_interaction'] = (df['slag'] + df['fly_ash']) * df['age']

    # Cement and superplasticizer (workability and strength)
    df_new['cement_superplasticizer'] = df['cement'] * df['superplasticizer']

    # Total binder and water (binding efficiency)
    df_new['binder_water_interaction'] = (df['cement'] + df['slag'] + df['fly_ash']) * df['water']

    # Aggregates interaction (total aggregate effect)
    df_new['aggregates_interaction'] = df['coarse_aggregate'] * df['fine_aggregate']

    return df_new


def create_polynomial_features(df, degree=2, features=None):
    """
    Create polynomial features for specified columns.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with original features
    degree : int, default=2
        Degree of polynomial features
    features : list, optional
        List of feature names to create polynomials for.
        If None, uses key features.

    Returns:
    --------
    pd.DataFrame
        DataFrame with added polynomial features
    """
    df_new = df.copy()

    if features is None:
        # Key features for polynomial expansion
        features = ['cement', 'age', 'water']

    for feature in features:
        if feature in df.columns:
            # Create squared and cubed terms
            df_new[f'{feature}_squared'] = df[feature] ** 2
            if degree >= 3:
                df_new[f'{feature}_cubed'] = df[feature] ** 3

    return df_new


def create_ratio_features(df):
    """
    Create ratio features based on domain knowledge.

    Ratios are important in concrete science and can capture
    relationships better than absolute values.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with original features

    Returns:
    --------
    pd.DataFrame
        DataFrame with added ratio features
    """
    df_new = df.copy()

    # Avoid division by zero
    epsilon = 1e-8

    # Water-Cement Ratio (most important in concrete science)
    df_new['water_cement_ratio'] = df['water'] / (df['cement'] + epsilon)

    # Water-Binder Ratio
    total_binder = df['cement'] + df['slag'] + df['fly_ash'] + epsilon
    df_new['water_binder_ratio'] = df['water'] / total_binder

    # Superplasticizer-Cement Ratio
    df_new['superplasticizer_cement_ratio'] = df['superplasticizer'] / (df['cement'] + epsilon)

    # Recycled Content Ratio
    df_new['recycled_binder_ratio'] = (df['slag'] + df['fly_ash']) / total_binder

    # Aggregate Ratios
    df_new['fine_coarse_aggregate_ratio'] = df['fine_aggregate'] / (df['coarse_aggregate'] + epsilon)
    total_aggregate = df['coarse_aggregate'] + df['fine_aggregate'] + epsilon
    df_new['aggregate_binder_ratio'] = total_aggregate / total_binder

    # Cement Replacement Ratio (sustainability metric)
    df_new['cement_replacement_ratio'] = (df['slag'] + df['fly_ash']) / (df['cement'] + epsilon)

    # Age-based ratios
    df_new['cement_per_age'] = df['cement'] / (df['age'] + epsilon)
    df_new['water_per_age'] = df['water'] / (df['age'] + epsilon)

    return df_new


def create_aggregate_features(df):
    """
    Create aggregate features combining multiple components.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with original features

    Returns:
    --------
    pd.DataFrame
        DataFrame with added aggregate features
    """
    df_new = df.copy()

    # Total binder content
    df_new['total_binder'] = df['cement'] + df['slag'] + df['fly_ash']

    # Total aggregate content
    df_new['total_aggregate'] = df['coarse_aggregate'] + df['fine_aggregate']

    # Total recycled content
    df_new['total_recycled'] = df['slag'] + df['fly_ash']

    # Total mix weight (approximate)
    df_new['total_mix_weight'] = (
        df['cement'] + df['slag'] + df['fly_ash'] +
        df['water'] + df['superplasticizer'] +
        df['coarse_aggregate'] + df['fine_aggregate']
    )

    # Paste content (cement + water + superplasticizer)
    df_new['paste_content'] = df['cement'] + df['water'] + df['superplasticizer']

    return df_new


def create_binned_features(df):
    """
    Create categorical features by binning continuous variables.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with original features

    Returns:
    --------
    pd.DataFrame
        DataFrame with added binned features
    """
    df_new = df.copy()

    # Age categories
    df_new['age_category'] = pd.cut(
        df['age'],
        bins=[0, 7, 28, 90, float('inf')],
        labels=['early', 'standard', 'medium', 'late']
    )

    # Water-cement ratio categories
    if 'water_cement_ratio' in df.columns:
        df_new['w_c_category'] = pd.cut(
            df['water_cement_ratio'],
            bins=[0, 0.4, 0.5, 0.6, float('inf')],
            labels=['very_low', 'low', 'medium', 'high']
        )

    # Recycled content categories
    if 'total_recycled' in df.columns:
        df_new['recycled_category'] = pd.cut(
            df['total_recycled'],
            bins=[0, 50, 100, 150, float('inf')],
            labels=['none_low', 'medium', 'high', 'very_high']
        )

    return df_new


def create_log_features(df, features=None):
    """
    Create log-transformed features for skewed distributions.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with original features
    features : list, optional
        List of features to log-transform

    Returns:
    --------
    pd.DataFrame
        DataFrame with added log features
    """
    df_new = df.copy()

    if features is None:
        features = ['cement', 'slag', 'fly_ash', 'age']

    for feature in features:
        if feature in df.columns:
            # Add small constant to avoid log(0)
            df_new[f'{feature}_log'] = np.log1p(df[feature])

    return df_new


def create_all_features(df, include_polynomial=True, include_binned=True, include_log=False):
    """
    Create all engineered features at once.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with original features
    include_polynomial : bool, default=True
        Whether to include polynomial features
    include_binned : bool, default=True
        Whether to include binned categorical features
    include_log : bool, default=False
        Whether to include log-transformed features

    Returns:
    --------
    pd.DataFrame
        DataFrame with all engineered features
    """
    df_enriched = df.copy()

    # Add aggregate features first (needed for ratios)
    df_enriched = create_aggregate_features(df_enriched)

    # Add ratio features
    df_enriched = create_ratio_features(df_enriched)

    # Add interaction features
    df_enriched = create_interaction_features(df_enriched)

    # Add polynomial features
    if include_polynomial:
        df_enriched = create_polynomial_features(df_enriched, degree=2)

    # Add binned features
    if include_binned:
        df_enriched = create_binned_features(df_enriched)

    # Add log features
    if include_log:
        df_enriched = create_log_features(df_enriched)

    return df_enriched


def get_feature_names(original_features=None):
    """
    Get a list of all possible engineered feature names.

    Parameters:
    -----------
    original_features : list, optional
        List of original feature names

    Returns:
    --------
    dict
        Dictionary with categories of feature names
    """
    if original_features is None:
        original_features = [
            'cement', 'slag', 'fly_ash', 'water',
            'superplasticizer', 'coarse_aggregate',
            'fine_aggregate', 'age'
        ]

    feature_groups = {
        'original': original_features,
        'aggregate': [
            'total_binder', 'total_aggregate', 'total_recycled',
            'total_mix_weight', 'paste_content'
        ],
        'ratio': [
            'water_cement_ratio', 'water_binder_ratio',
            'superplasticizer_cement_ratio', 'recycled_binder_ratio',
            'fine_coarse_aggregate_ratio', 'aggregate_binder_ratio',
            'cement_replacement_ratio', 'cement_per_age', 'water_per_age'
        ],
        'interaction': [
            'cement_water_interaction', 'recycled_age_interaction',
            'cement_superplasticizer', 'binder_water_interaction',
            'aggregates_interaction'
        ],
        'polynomial': [
            'cement_squared', 'age_squared', 'water_squared'
        ],
        'categorical': [
            'age_category', 'w_c_category', 'recycled_category'
        ]
    }

    return feature_groups


def select_features_by_importance(df, target, n_features=20, method='random_forest'):
    """
    Select top features based on importance scores.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with all features
    target : pd.Series
        Target variable
    n_features : int, default=20
        Number of top features to select
    method : str, default='random_forest'
        Method to use for feature importance

    Returns:
    --------
    list
        List of top feature names
    """
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.feature_selection import SelectKBest, f_regression

    # Get numeric columns only
    numeric_df = df.select_dtypes(include=[np.number])

    if method == 'random_forest':
        # Use Random Forest feature importance
        rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(numeric_df, target)

        # Get feature importance
        importance_df = pd.DataFrame({
            'feature': numeric_df.columns,
            'importance': rf.feature_importances_
        }).sort_values('importance', ascending=False)

        top_features = importance_df.head(n_features)['feature'].tolist()

    elif method == 'f_regression':
        # Use F-statistic
        selector = SelectKBest(f_regression, k=min(n_features, numeric_df.shape[1]))
        selector.fit(numeric_df, target)

        # Get selected features
        selected_mask = selector.get_support()
        top_features = numeric_df.columns[selected_mask].tolist()

    else:
        raise ValueError(f"Unknown method: {method}")

    return top_features


# Example usage
if __name__ == "__main__":
    # Example with sample data
    sample_data = {
        'cement': [200, 250, 300],
        'slag': [50, 100, 150],
        'fly_ash': [30, 60, 90],
        'water': [150, 175, 200],
        'superplasticizer': [5, 7, 10],
        'coarse_aggregate': [900, 950, 1000],
        'fine_aggregate': [700, 750, 800],
        'age': [7, 28, 90]
    }

    df = pd.DataFrame(sample_data)

    print("Original features:")
    print(df.columns.tolist())
    print(f"Shape: {df.shape}")

    # Create all features
    df_enriched = create_all_features(df)

    print(f"\nEnriched features:")
    print(df_enriched.columns.tolist())
    print(f"Shape: {df_enriched.shape}")
    print(f"\nAdded {df_enriched.shape[1] - df.shape[1]} new features")
