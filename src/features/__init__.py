"""
Feature Engineering Module
===========================

This module provides functions for creating engineered features
for the Material Passport Generator project.
"""

from .feature_engineering import (
    create_interaction_features,
    create_polynomial_features,
    create_ratio_features,
    create_all_features,
    get_feature_names
)

__all__ = [
    'create_interaction_features',
    'create_polynomial_features',
    'create_ratio_features',
    'create_all_features',
    'get_feature_names'
]
