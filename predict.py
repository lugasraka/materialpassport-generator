"""
Concrete Strength Prediction Interface

This module provides a simple interface for predicting concrete strength
using the production-deployed XGBoost model with aggregate features.

Usage:
    python predict.py --cement 280 --slag 100 --fly_ash 0 --water 180 \\
                      --superplasticizer 10 --coarse_aggregate 1000 \\
                      --fine_aggregate 750 --age 28

Or import and use in Python:
    from predict import ConcreteStrengthPredictor
    predictor = ConcreteStrengthPredictor()
    strength = predictor.predict({
        'cement': 280, 'slag': 100, 'fly_ash': 0, 'water': 180,
        'superplasticizer': 10, 'coarse_aggregate': 1000,
        'fine_aggregate': 750, 'age': 28
    })
"""

import pickle
import json
import argparse
import pandas as pd
from pathlib import Path
from typing import Dict, Union


class ConcreteStrengthPredictor:
    """
    Production-ready concrete strength predictor.

    This class loads the trained model and provides a clean interface
    for making predictions with automatic feature engineering.
    """

    def __init__(self, model_path: str = None, metadata_path: str = None):
        """
        Initialize the predictor.

        Args:
            model_path: Path to the model pickle file. Defaults to 'models/production_model.pkl'
            metadata_path: Path to model metadata JSON. Defaults to 'models/production_metadata.json'
        """
        # Default paths
        if model_path is None:
            model_path = Path('models') / 'production_model.pkl'
        if metadata_path is None:
            metadata_path = Path('models') / 'production_metadata.json'

        # Load model
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)

        # Load metadata
        with open(metadata_path, 'r') as f:
            self.metadata = json.load(f)

        # Extract feature information
        self.feature_names = self.metadata['features']
        self.original_features = [
            'cement', 'slag', 'fly_ash', 'water', 'superplasticizer',
            'coarse_aggregate', 'fine_aggregate', 'age'
        ]

        print(f"[INFO] Model loaded: {self.metadata['model_name']} v{self.metadata['version']}")
        print(f"[INFO] Performance: R² = {self.metadata['performance']['test_r2']:.4f}, "
              f"RMSE = {self.metadata['performance']['test_rmse']:.2f} MPa")

    def _create_aggregate_features(self, data: Dict[str, float]) -> Dict[str, float]:
        """
        Create aggregate features from input data.

        Args:
            data: Dictionary with original 8 features

        Returns:
            Dictionary with all 16 features (original + aggregate)
        """
        result = data.copy()

        # Total quantities
        result['total_binder'] = data['cement'] + data['slag'] + data['fly_ash']
        result['total_aggregate'] = data['coarse_aggregate'] + data['fine_aggregate']
        result['total_solid'] = result['total_binder'] + result['total_aggregate']

        # Binder composition percentages
        total_binder = result['total_binder'] + 1e-6  # Avoid division by zero
        result['cement_pct'] = data['cement'] / total_binder
        result['slag_pct'] = data['slag'] / total_binder
        result['fly_ash_pct'] = data['fly_ash'] / total_binder

        # Material intensity
        result['paste_volume'] = result['total_binder'] + data['water']
        result['total_volume'] = result['paste_volume'] + result['total_aggregate']

        return result

    def predict(self, input_data: Union[Dict[str, float], pd.DataFrame]) -> Union[float, pd.Series]:
        """
        Predict concrete strength.

        Args:
            input_data: Either a dictionary with 8 original features, or a pandas DataFrame

        Returns:
            Predicted strength in MPa (float if dict input, Series if DataFrame input)

        Example:
            >>> predictor = ConcreteStrengthPredictor()
            >>> strength = predictor.predict({
            ...     'cement': 280, 'slag': 100, 'fly_ash': 0, 'water': 180,
            ...     'superplasticizer': 10, 'coarse_aggregate': 1000,
            ...     'fine_aggregate': 750, 'age': 28
            ... })
            >>> print(f"Predicted strength: {strength:.2f} MPa")
        """
        # Convert dict to DataFrame if needed
        if isinstance(input_data, dict):
            # Validate input
            missing_features = set(self.original_features) - set(input_data.keys())
            if missing_features:
                raise ValueError(f"Missing required features: {missing_features}")

            # Create aggregate features
            full_features = self._create_aggregate_features(input_data)

            # Convert to DataFrame
            df = pd.DataFrame([full_features])

            # Ensure correct feature order
            df = df[self.feature_names]

            # Make prediction
            prediction = self.model.predict(df)[0]
            return prediction

        elif isinstance(input_data, pd.DataFrame):
            # Check if aggregate features already exist
            has_aggregate = all(f in input_data.columns for f in self.feature_names)

            if not has_aggregate:
                # Need to create aggregate features
                result_df = input_data.copy()

                # Create aggregate features for each row
                result_df['total_binder'] = (result_df['cement'] + result_df['slag'] +
                                            result_df['fly_ash'])
                result_df['total_aggregate'] = (result_df['coarse_aggregate'] +
                                               result_df['fine_aggregate'])
                result_df['total_solid'] = result_df['total_binder'] + result_df['total_aggregate']

                total_binder = result_df['total_binder'] + 1e-6
                result_df['cement_pct'] = result_df['cement'] / total_binder
                result_df['slag_pct'] = result_df['slag'] / total_binder
                result_df['fly_ash_pct'] = result_df['fly_ash'] / total_binder

                result_df['paste_volume'] = result_df['total_binder'] + result_df['water']
                result_df['total_volume'] = result_df['paste_volume'] + result_df['total_aggregate']

                input_data = result_df

            # Ensure correct feature order
            input_data = input_data[self.feature_names]

            # Make predictions
            predictions = self.model.predict(input_data)
            return pd.Series(predictions, index=input_data.index)

        else:
            raise TypeError("Input must be either a dictionary or pandas DataFrame")

    def get_model_info(self) -> Dict:
        """Get model metadata and performance information."""
        return self.metadata


def main():
    """Command-line interface for making predictions."""
    parser = argparse.ArgumentParser(
        description='Predict concrete compressive strength using the production model'
    )

    # Original features (required)
    parser.add_argument('--cement', type=float, required=True,
                       help='Cement content (kg/m³)')
    parser.add_argument('--slag', type=float, required=True,
                       help='Blast Furnace Slag content (kg/m³)')
    parser.add_argument('--fly_ash', type=float, required=True,
                       help='Fly Ash content (kg/m³)')
    parser.add_argument('--water', type=float, required=True,
                       help='Water content (kg/m³)')
    parser.add_argument('--superplasticizer', type=float, required=True,
                       help='Superplasticizer content (kg/m³)')
    parser.add_argument('--coarse_aggregate', type=float, required=True,
                       help='Coarse Aggregate content (kg/m³)')
    parser.add_argument('--fine_aggregate', type=float, required=True,
                       help='Fine Aggregate content (kg/m³)')
    parser.add_argument('--age', type=float, required=True,
                       help='Age of concrete (days)')

    args = parser.parse_args()

    # Create input dictionary
    input_data = {
        'cement': args.cement,
        'slag': args.slag,
        'fly_ash': args.fly_ash,
        'water': args.water,
        'superplasticizer': args.superplasticizer,
        'coarse_aggregate': args.coarse_aggregate,
        'fine_aggregate': args.fine_aggregate,
        'age': args.age
    }

    # Load predictor and make prediction
    print("\n" + "="*70)
    print("CONCRETE STRENGTH PREDICTION")
    print("="*70)

    predictor = ConcreteStrengthPredictor()

    print("\n[INPUT MIXTURE]")
    for feature, value in input_data.items():
        unit = "days" if feature == "age" else "kg/m³"
        print(f"  {feature:.<30} {value:.2f} {unit}")

    prediction = predictor.predict(input_data)

    print("\n[PREDICTION]")
    print(f"  Predicted Compressive Strength: {prediction:.2f} MPa")

    print("\n[MODEL PERFORMANCE]")
    print(f"  Test R²:                        {predictor.metadata['performance']['test_r2']:.4f}")
    print(f"  Test RMSE:                      {predictor.metadata['performance']['test_rmse']:.2f} MPa")
    print(f"  Expected Error:                 ±{predictor.metadata['performance']['test_rmse']:.2f} MPa")

    print("\n" + "="*70)


if __name__ == '__main__':
    main()
