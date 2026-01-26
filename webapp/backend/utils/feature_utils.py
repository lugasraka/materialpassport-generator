"""
Feature engineering utilities.
"""
import numpy as np
from typing import Dict, List

def create_aggregate_features(composition: Dict) -> Dict:
    """
    Create aggregate features from original material composition.
    
    Args:
        composition: Material composition dict with 8 original features
    
    Returns:
        Dict with 8 original + 8 aggregate features
    """
    features = composition.copy()
    
    # Total binders
    features['total_binder'] = (
        composition.get('cement', 0) +
        composition.get('blast_furnace_slag', 0) +
        composition.get('fly_ash', 0)
    )
    
    # Total aggregates
    features['total_aggregate'] = (
        composition.get('coarse_aggregate', 0) +
        composition.get('fine_aggregate', 0)
    )
    
    # Total solids (non-water)
    features['total_solid'] = features['total_binder'] + features['total_aggregate']
    
    # Cement percentage
    features['cement_pct'] = (
        (composition.get('cement', 0) / features['total_binder']) * 100
        if features['total_binder'] > 0 else 0
    )
    
    # Slag percentage
    features['slag_pct'] = (
        (composition.get('blast_furnace_slag', 0) / features['total_binder']) * 100
        if features['total_binder'] > 0 else 0
    )
    
    # Fly ash percentage
    features['fly_ash_pct'] = (
        (composition.get('fly_ash', 0) / features['total_binder']) * 100
        if features['total_binder'] > 0 else 0
    )
    
    # Paste volume (cement + water)
    features['paste_volume'] = (
        composition.get('cement', 0) +
        composition.get('water', 0)
    )
    
    # Total volume
    features['total_volume'] = features['paste_volume'] + features['total_aggregate']
    
    # Water-to-cement ratio
    features['w_cement_ratio'] = (
        (composition.get('water', 0) / composition.get('cement', 0))
        if composition.get('cement', 0) > 0 else 0
    )
    
    return features

def scale_features(features: Dict, scaler=None) -> np.ndarray:
    """
    Scale features using scaler.
    
    Args:
        features: Feature dict with engineered features
        scaler: Scaler object (from joblib)
    
    Returns:
        Scaled feature array
    """
    feature_order = [
        'cement', 'blast_furnace_slag', 'fly_ash', 'water', 'superplasticizer',
        'coarse_aggregate', 'fine_aggregate', 'age',
        'total_binder', 'total_aggregate', 'total_solid',
        'cement_pct', 'slag_pct', 'fly_ash_pct',
        'paste_volume', 'total_volume', 'w_cement_ratio'
    ]
    
    if scaler is None:
        return np.array([features.get(f, 0) for f in feature_order])
    
    feature_array = np.array([features.get(f, 0) for f in feature_order])
    return scaler.transform(feature_array.reshape(1, -1))

def get_feature_names(feature_set: str = "aggregate") -> List[str]:
    """
    Get feature names for a given feature set.
    
    Args:
        feature_set: Type of feature set ('original' or 'aggregate')
    
    Returns:
        List of feature names
    """
    if feature_set == "original":
        return [
            'cement', 'blast_furnace_slag', 'fly_ash', 'water', 'superplasticizer',
            'coarse_aggregate', 'fine_aggregate', 'age'
        ]
    elif feature_set == "aggregate":
        return [
            'cement', 'blast_furnace_slag', 'fly_ash', 'water', 'superplasticizer',
            'coarse_aggregate', 'fine_aggregate', 'age',
            'total_binder', 'total_aggregate', 'total_solid',
            'cement_pct', 'slag_pct', 'fly_ash_pct',
            'paste_volume', 'total_volume', 'w_cement_ratio'
        ]
    else:
        raise ValueError(f"Unknown feature set: {feature_set}")
