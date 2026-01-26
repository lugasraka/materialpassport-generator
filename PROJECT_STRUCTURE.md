# Project Structure

## Overview

This document describes the organization of the Material Passport Generator project, with emphasis on the ML model development and deployment infrastructure.

```
materialpassport-generator/
├── data/                           # Data directory
│   ├── raw/                        # Raw, immutable data
│   └── processed/                  # Processed data ready for ML
│       └── concrete_enriched.csv   # Main dataset with engineered features
│
├── docs/                           # Documentation
│   ├── competitive_analysis_*.md   # Market analysis documents
│   ├── PRD.md                      # Product Requirements Document
│   ├── STRATEGIC_ROADMAP_SUMMARY.md
│   ├── MODEL_DEPLOYMENT_GUIDE.md   # ML model deployment guide
│   └── OPTIMIZATION_SUMMARY.md     # Complete ML optimization journey
│
├── models/                         # Trained ML models
│   ├── production_model.pkl        # Production XGBoost model
│   ├── production_features.json    # Feature configuration
│   ├── production_metadata.json    # Model metadata
│   └── *.pkl                       # Other trained models
│
├── mlruns/                         # MLflow tracking directory
│   ├── 0/                          # Default experiment
│   ├── experiments/                # Individual experiments
│   └── models/                     # MLflow Model Registry
│       └── concrete_strength_xgboost/  # Registered model
│
├── notebooks/                      # Jupyter notebooks for experimentation
│   ├── 01_data_exploration.ipynb   # Initial data analysis
│   ├── 02_baseline_models_mlflow.ipynb     # Baseline models with MLflow
│   ├── 03_deep_learning_mlflow.ipynb       # Deep learning with MLflow
│   ├── 04_hyperparameter_optimization.ipynb # HPO experiments
│   └── archive/                    # Archived notebooks (without MLflow)
│
├── scripts/                        # ML experiment and training scripts
│   ├── run_baseline_models_mlflow.py       # Phase 2: Baseline models
│   ├── run_deep_learning_mlflow.py         # Phase 2: Deep learning models
│   ├── run_hyperparameter_optimization.py  # Phase 3: HPO (200 trials)
│   ├── run_feature_engineering.py          # Phase 4: Feature engineering
│   └── run_hpo_aggregate_features.py       # Phase 4.5: Aggregate features HPO
│
├── src/                            # Source code
│   ├── __init__.py
│   ├── mlflow_config.py           # MLflow configuration constants
│   └── utils/
│       └── mlflow_utils.py        # MLflow utility functions
│
├── venv/                          # Python virtual environment (git ignored)
│
├── deploy_best_model.py          # Production model deployment script
├── predict.py                     # Prediction interface (main API)
│
├── .gitignore                     # Git ignore rules
├── requirements.txt               # Python dependencies
│
├── GETTING_STARTED.md             # Quick start guide
├── PROJECT_STRUCTURE.md           # This file
├── README.md                      # Project overview
├── START_HERE.md                  # Getting started instructions
└── WEB_APP_IMPLEMENTATION_PLAN.md # Web app development plan
```

---

## Directory Descriptions

### 📁 `/data`
Contains all project data, separated into raw and processed datasets.

- **`/data/raw`**: Original, immutable data files
- **`/data/processed`**: Cleaned and preprocessed data ready for modeling
  - `concrete_enriched.csv`: Main dataset with 1030 samples and 17 features

### 📄 `/docs`
Project documentation including business analysis, technical specs, and ML documentation.

**Key Files:**
- **`MODEL_DEPLOYMENT_GUIDE.md`**: Complete guide for using the deployed ML model
  - Performance metrics
  - Usage examples (CLI, Python API, FastAPI, Flask)
  - Integration guides
  - Monitoring recommendations

- **`OPTIMIZATION_SUMMARY.md`**: Comprehensive ML optimization journey
  - All phases (2-4.5) with results
  - 220+ experiments tracked
  - Performance improvements documented
  - Key learnings and insights

### 🤖 `/models`
Trained machine learning models and their metadata.

**Production Files:**
- **`production_model.pkl`**: Production XGBoost model (R² = 0.9353, RMSE = 4.08 MPa)
- **`production_features.json`**: Feature names and configuration
- **`production_metadata.json`**: Model performance, hyperparameters, training date

**Other Models:**
- Various `.pkl` files from training experiments
- Scalers and preprocessing artifacts

### 📊 `/mlruns`
MLflow tracking directory (created automatically).

**Structure:**
- **Experiments:**
  - Concrete-Baseline-Models (6 runs)
  - Concrete-Deep-Learning (7 runs)
  - Concrete-HPO (201+ runs)
  - Concrete-Feature-Engineering (7 runs)

- **Model Registry:**
  - `concrete_strength_xgboost` (3 versions)
  - Version 3 in **Production** stage

### 📓 `/notebooks`
Jupyter notebooks for experimentation and analysis.

**Active Notebooks:**
1. **`01_data_exploration.ipynb`**: Initial EDA and data understanding
2. **`02_baseline_models_mlflow.ipynb`**: Baseline models with MLflow tracking
3. **`03_deep_learning_mlflow.ipynb`**: PyTorch models with MLflow tracking
4. **`04_hyperparameter_optimization.ipynb`**: Optuna HPO experiments

**`/notebooks/archive`**: Old notebooks without MLflow (kept for reference)

### 🔧 `/scripts`
Production-ready scripts for ML experiments and training.

**Execution Order (for reproducing results):**
1. **`run_baseline_models_mlflow.py`**: Train baseline ML models (Phase 2)
2. **`run_deep_learning_mlflow.py`**: Train neural network models (Phase 2)
3. **`run_hyperparameter_optimization.py`**: Optimize XGBoost hyperparameters (Phase 3)
4. **`run_feature_engineering.py`**: Test 7 feature sets (Phase 4)
5. **`run_hpo_aggregate_features.py`**: Optimize with aggregate features (Phase 4.5)

**Note:** All scripts log to MLflow automatically.

### 💻 `/src`
Source code modules and utilities.

**`mlflow_config.py`**: Central configuration for MLflow
- Experiment names
- Model names
- Performance targets
- Tag taxonomy

**`utils/mlflow_utils.py`**: Reusable MLflow functions
- `setup_mlflow_experiment()`
- `log_model_artifacts()`
- `log_metrics_and_params()`
- `log_feature_importance()`
- And 10+ other utilities

---

## Key Files in Root

### 🚀 Production Files

**`deploy_best_model.py`**
- Official production deployment script
- Trains best model (aggregate features + Phase 3 hyperparameters)
- Registers to MLflow Model Registry
- Promotes to Production stage
- Saves artifacts for deployment

**`predict.py`**
- **Main prediction interface**
- Simple Python API for making predictions
- Handles feature engineering automatically
- CLI and programmatic usage
- Load from pickle or MLflow Registry

### 📚 Documentation

**`README.md`**
- Project overview
- High-level architecture
- Getting started

**`START_HERE.md`** & **`GETTING_STARTED.md`**
- Quick start guides
- Installation instructions
- First steps

**`WEB_APP_IMPLEMENTATION_PLAN.md`**
- Web application development plan
- Frontend and backend architecture
- Deployment strategy

**`PROJECT_STRUCTURE.md`** (this file)
- Complete project organization
- File and directory descriptions

### ⚙️ Configuration

**`requirements.txt`**
- Python package dependencies
- Includes ML libraries (scikit-learn, xgboost, torch)
- MLflow tracking
- Optuna for hyperparameter optimization

**`.gitignore`**
- Ignores venv, mlruns, __pycache__
- Keeps repository clean

---

## Quick Start Commands

### Setup Environment
```bash
# Create virtual environment
python -m venv venv

# Activate venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Make Predictions
```bash
# Using predict.py CLI
python predict.py --cement 280 --slag 100 --fly_ash 0 --water 180 \
                  --superplasticizer 10 --coarse_aggregate 1000 \
                  --fine_aggregate 750 --age 28
```

```python
# Using predict.py in Python
from predict import ConcreteStrengthPredictor

predictor = ConcreteStrengthPredictor()
strength = predictor.predict({
    'cement': 280, 'slag': 100, 'fly_ash': 0, 'water': 180,
    'superplasticizer': 10, 'coarse_aggregate': 1000,
    'fine_aggregate': 750, 'age': 28
})
```

### View MLflow Experiments
```bash
# Launch MLflow UI
mlflow ui --port 5000

# Open browser to http://localhost:5000
```

### Run Experiments
```bash
# Reproduce Phase 2: Baseline models
python scripts/run_baseline_models_mlflow.py

# Reproduce Phase 3: Hyperparameter optimization
python scripts/run_hyperparameter_optimization.py

# Reproduce Phase 4: Feature engineering
python scripts/run_feature_engineering.py

# Deploy production model
python deploy_best_model.py
```

---

## ML Model Information

### Production Model
- **Model:** XGBoost with Aggregate Features
- **Version:** 3 (in Production stage)
- **Performance:** R² = 0.9353, RMSE = 4.08 MPa
- **Features:** 16 (8 original + 8 engineered)
- **Training Data:** 824 samples
- **Test Data:** 206 samples

### Optimization Journey
| Phase | Approach | R² | RMSE |
|-------|----------|-----|------|
| Phase 2 | Baseline XGBoost | 0.9088 | 4.85 MPa |
| Phase 3 | + Hyperparameter Optimization | 0.9314 | 4.20 MPa |
| **Phase 4** | **+ Aggregate Features** | **0.9353** | **4.08 MPa** |

**Total Improvement:** +2.92% R², -15.88% RMSE

---

## Development Workflow

### 1. Experimentation
- Use Jupyter notebooks in `/notebooks`
- All experiments automatically tracked in MLflow
- Iterate and compare results

### 2. Production Scripts
- Convert successful notebooks to scripts in `/scripts`
- Ensure reproducibility
- Add comprehensive logging

### 3. Model Deployment
- Run `deploy_best_model.py`
- Model registered in MLflow Registry
- Artifacts saved to `/models`
- Ready for integration

### 4. Integration
- Use `predict.py` for predictions
- Load model from MLflow or pickle
- Integrate into web application

---

## Git Workflow

```bash
# Standard workflow
git add <files>
git commit -m "Descriptive message"
git push origin main

# For ML experiments
# MLflow tracks everything, so you don't need to commit:
# - model files (*.pkl)
# - mlruns/ directory
# - experiment outputs
```

---

## Additional Resources

- **MLflow Documentation**: https://mlflow.org/docs/latest/
- **XGBoost Documentation**: https://xgboost.readthedocs.io/
- **Optuna Documentation**: https://optuna.readthedocs.io/

---

*Last Updated: 2026-01-26*
*Project Status: Production Model Deployed*
*Next Steps: Web Application Integration*
