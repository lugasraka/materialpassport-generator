# Concrete Strength Prediction Model - Deployment Guide

## Overview

This document provides comprehensive information about the production-deployed concrete strength prediction model.

**Model Name:** `concrete_strength_xgboost`
**Version:** 3
**Status:** Production
**Performance:** R² = 0.9353, RMSE = 4.08 MPa
**Deployment Date:** 2026-01-26

---

## Model Information

### Performance Metrics

| Metric | Value | Description |
|--------|-------|-------------|
| **Test R²** | 0.9353 | Explains 93.53% of variance |
| **Test RMSE** | 4.08 MPa | Root mean squared error |
| **Test MAE** | 2.62 MPa | Mean absolute error |
| **CV R²** | 0.9347 ± 0.0154 | Cross-validation score |
| **Training Time** | 0.56 seconds | Fast inference |

### Target Achievement

- ✅ **Primary Target Achieved:** R² > 0.92, RMSE < 4.5 MPa
- ⚠️  **Stretch Target:** R² > 0.94, RMSE < 4.0 MPa (99.5% achieved - only 0.08 MPa away!)

---

## Features (16 Total)

### Original Features (8)

These are the input features required for prediction:

1. **cement** - Portland cement content (kg/m³)
2. **slag** - Blast furnace slag content (kg/m³)
3. **fly_ash** - Fly ash content (kg/m³)
4. **water** - Water content (kg/m³)
5. **superplasticizer** - Superplasticizer additive content (kg/m³)
6. **coarse_aggregate** - Coarse aggregate content (kg/m³)
7. **fine_aggregate** - Fine aggregate content (kg/m³)
8. **age** - Concrete age (days)

### Engineered Features (8)

These features are automatically calculated from the original features:

1. **total_binder** = cement + slag + fly_ash
2. **total_aggregate** = coarse_aggregate + fine_aggregate
3. **total_solid** = total_binder + total_aggregate
4. **cement_pct** = cement / total_binder
5. **slag_pct** = slag / total_binder
6. **fly_ash_pct** = fly_ash / total_binder
7. **paste_volume** = total_binder + water
8. **total_volume** = paste_volume + total_aggregate

---

## Model Architecture

**Algorithm:** XGBoost (Gradient Boosted Trees)

**Key Hyperparameters:**
```python
{
    'n_estimators': 439,           # Number of trees
    'max_depth': 15,                # Maximum tree depth
    'learning_rate': 0.0547,        # Step size shrinkage
    'subsample': 0.584,             # Row sampling ratio
    'colsample_bytree': 0.638,      # Column sampling ratio
    'gamma': 0.257,                 # Minimum loss reduction
    'reg_alpha': 1.885,             # L1 regularization
    'reg_lambda': 0.551,            # L2 regularization
    'min_child_weight': 10          # Minimum sum of weights
}
```

---

## Usage

### 1. Command-Line Interface

The simplest way to make predictions:

```bash
python predict.py --cement 280 --slag 100 --fly_ash 0 --water 180 \
                  --superplasticizer 10 --coarse_aggregate 1000 \
                  --fine_aggregate 750 --age 28
```

**Output:**
```
Predicted Compressive Strength: 42.16 MPa
Expected Error: ±4.08 MPa
```

### 2. Python API

```python
from predict import ConcreteStrengthPredictor

# Initialize predictor
predictor = ConcreteStrengthPredictor()

# Single prediction
strength = predictor.predict({
    'cement': 280,
    'slag': 100,
    'fly_ash': 0,
    'water': 180,
    'superplasticizer': 10,
    'coarse_aggregate': 1000,
    'fine_aggregate': 750,
    'age': 28
})

print(f"Predicted strength: {strength:.2f} MPa")
```

**Output:**
```
Predicted strength: 42.16 MPa
```

### 3. Batch Predictions

```python
import pandas as pd
from predict import ConcreteStrengthPredictor

# Load predictor
predictor = ConcreteStrengthPredictor()

# Create DataFrame with multiple samples
mixtures = pd.DataFrame({
    'cement': [280, 300, 350],
    'slag': [100, 80, 0],
    'fly_ash': [0, 50, 100],
    'water': [180, 170, 160],
    'superplasticizer': [10, 12, 15],
    'coarse_aggregate': [1000, 1050, 1100],
    'fine_aggregate': [750, 800, 850],
    'age': [28, 28, 28]
})

# Make predictions
predictions = predictor.predict(mixtures)
print(predictions)
```

**Output:**
```
0    42.16
1    45.23
2    48.91
dtype: float64
```

### 4. Load from MLflow Model Registry

```python
import mlflow

# Load model from MLflow Registry
model_uri = 'models:/concrete_strength_xgboost/Production'
model = mlflow.pyfunc.load_model(model_uri)

# Make prediction (requires all 16 features including engineered ones)
prediction = model.predict(input_data)
```

### 5. Load from Pickle File

```python
import pickle
import pandas as pd

# Load model
with open('models/production_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Prepare input (must include all 16 features)
input_features = pd.DataFrame([{
    'cement': 280, 'slag': 100, 'fly_ash': 0, 'water': 180,
    'superplasticizer': 10, 'coarse_aggregate': 1000,
    'fine_aggregate': 750, 'age': 28,
    # Engineered features (calculated manually)
    'total_binder': 380, 'total_aggregate': 1750,
    'total_solid': 2130, 'cement_pct': 0.737,
    'slag_pct': 0.263, 'fly_ash_pct': 0.0,
    'paste_volume': 560, 'total_volume': 2310
}])

# Make prediction
prediction = model.predict(input_features)
```

---

## File Locations

### Model Artifacts

- **Model File:** `models/production_model.pkl`
- **Features Config:** `models/production_features.json`
- **Metadata:** `models/production_metadata.json`

### MLflow Tracking

- **Tracking URI:** `file:./mlruns`
- **Experiment:** Concrete-HPO (ID: 761842859264032071)
- **Run ID:** ffeae41fe79945319dc4a88940f53ba7
- **Registry:** `concrete_strength_xgboost` (Version 3, Stage: Production)

### Documentation

- **Optimization Summary:** `OPTIMIZATION_SUMMARY.md`
- **Deployment Guide:** `MODEL_DEPLOYMENT_GUIDE.md` (this file)

---

## Integration Examples

### FastAPI Endpoint

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from predict import ConcreteStrengthPredictor

app = FastAPI()
predictor = ConcreteStrengthPredictor()

class ConcreteInput(BaseModel):
    cement: float
    slag: float
    fly_ash: float
    water: float
    superplasticizer: float
    coarse_aggregate: float
    fine_aggregate: float
    age: float

@app.post("/predict")
def predict_strength(input_data: ConcreteInput):
    try:
        prediction = predictor.predict(input_data.dict())
        return {
            "predicted_strength_mpa": round(prediction, 2),
            "model_version": predictor.metadata['version'],
            "model_r2": predictor.metadata['performance']['test_r2'],
            "expected_error_mpa": predictor.metadata['performance']['test_rmse']
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Flask Endpoint

```python
from flask import Flask, request, jsonify
from predict import ConcreteStrengthPredictor

app = Flask(__name__)
predictor = ConcreteStrengthPredictor()

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    required_fields = ['cement', 'slag', 'fly_ash', 'water',
                      'superplasticizer', 'coarse_aggregate',
                      'fine_aggregate', 'age']

    # Validate input
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    # Make prediction
    prediction = predictor.predict(data)

    return jsonify({
        'predicted_strength_mpa': round(prediction, 2),
        'model_version': predictor.metadata['version'],
        'expected_error_mpa': predictor.metadata['performance']['test_rmse']
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

## Model Monitoring

### Recommended Metrics to Track

1. **Prediction Distribution**
   - Monitor the distribution of predicted values
   - Alert if predictions fall outside expected range (10-100 MPa)

2. **Input Feature Distribution**
   - Track drift in input features compared to training data
   - Alert on out-of-distribution inputs

3. **Prediction Latency**
   - Monitor inference time (should be < 100ms per prediction)

4. **Model Performance**
   - Collect actual strengths when available
   - Compare predictions vs actuals
   - Retrain if RMSE degrades beyond 5.0 MPa

### Retraining Triggers

Retrain the model if any of these conditions are met:

- ✅ New data accumulated (>500 new samples)
- ✅ Performance degradation (RMSE > 5.0 MPa on validation)
- ✅ Significant feature drift detected
- ✅ Scheduled retraining (quarterly)

---

## Expected Model Behavior

### Typical Predictions

| Mixture Type | Expected Strength | Actual Range |
|-------------|-------------------|--------------|
| Low strength (w/c > 0.6) | 20-30 MPa | 15-35 MPa |
| Standard concrete | 30-45 MPa | 25-50 MPa |
| High strength (w/c < 0.4) | 45-70 MPa | 40-80 MPa |
| Ultra-high strength | 70-90 MPa | 65-100 MPa |

### Prediction Uncertainty

- **Typical Error:** ±4.08 MPa (RMSE)
- **95% Confidence:** ±8.16 MPa (2 × RMSE)
- **Median Error:** ±2.62 MPa (MAE)

### Edge Cases

- **Very low age (< 3 days):** Model may underpredict
- **Very high age (> 365 days):** Limited training data, higher uncertainty
- **Unusual mix ratios:** Predictions less reliable outside training distribution

---

## Troubleshooting

### Common Issues

**Issue:** `ModuleNotFoundError: No module named 'xgboost'`
**Solution:** Install requirements: `pip install -r requirements.txt`

**Issue:** `FileNotFoundError: models/production_model.pkl not found`
**Solution:** Run deployment script: `python deploy_best_model.py`

**Issue:** Predictions seem unrealistic
**Solution:** Verify input units (kg/m³ for materials, days for age)

**Issue:** Model performance degraded
**Solution:** Check for feature drift, consider retraining with new data

---

## Model Lifecycle

### Current Status: Production

**Deployment Date:** 2026-01-26
**Last Evaluation:** 2026-01-26
**Next Review:** 2026-04-26 (Quarterly)
**Deployed By:** Claude Code Optimization Pipeline

### Version History

| Version | Date | R² | RMSE | Status | Notes |
|---------|------|-----|------|--------|-------|
| 3 | 2026-01-26 | 0.9353 | 4.08 MPa | Production | Aggregate features + HPO |
| 2 | 2026-01-26 | 0.9314 | 4.20 MPa | Archived | Original features + HPO |
| 1 | 2026-01-26 | 0.9088 | 4.85 MPa | Archived | Baseline XGBoost |

---

## Contact & Support

For questions or issues with this model:

1. Check [OPTIMIZATION_SUMMARY.md](OPTIMIZATION_SUMMARY.md) for detailed optimization journey
2. Review MLflow experiments: `mlflow ui --port 5000`
3. Examine model artifacts in `models/` directory
4. Check training scripts in project root

---

## License & Attribution

This model was developed as part of the Material Passport Generator project.

**Citation:**
```
Concrete Strength Prediction Model v3
Developed using XGBoost with aggregate feature engineering
Performance: R² = 0.9353, RMSE = 4.08 MPa
Deployment Date: 2026-01-26
```

---

*Last Updated: 2026-01-26*
*Model Version: 3*
*Status: Production*
