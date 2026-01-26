# Material Passport Generator - Backend API

FastAPI backend for the Material Passport Generator project.

## Overview

This backend serves trained ML models and generates digital material passports for building materials, focusing on concrete composition analysis and sustainability metrics.

## Key Features

- **Model Serving:** Load 6 trained ML models from `../models/` directory
- **Production Artifacts:** Use `production_metadata.json` and `production_features.json`
- **MLflow Integration:** Production logging for predictions and model performance
- **Passport Generation:** Create professional, shareable digital passports
- **Sustainability Metrics:** Calculate circularity, CO2 emissions, recycled content
- **QR Code & PDF:** Export capabilities for passport verification

## Architecture

```
FastAPI Application
├── Models Loader (from ../models/)
├── Prediction Service (ML predictions + MLflow logging)
├── Sustainability Service (metrics calculation)
├── Passport Service (orchestration)
└── Utils (QR, PDF, configuration)
```

## Quick Start

### Prerequisites

- Python 3.9+
- Existing trained models in `../models/` directory
- MLflow tracking server (optional, for production logging)

### Installation

```bash
# Navigate to backend directory
cd webapp/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. **Copy Environment Template**
```bash
cp .env.example .env
```

2. **Edit `.env`** (optional, defaults should work)
```bash
# Application
APP_NAME=Material Passport Generator API
APP_VERSION=1.0.0
API_PREFIX=/api/v1

# Model paths
MODELS_DIR=../../models

# Server
HOST=0.0.0.0
PORT=8000

# MLflow (optional)
MLFLOW_TRACKING_URI=../mlruns
```

### Running

```bash
# Development (auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

### API Documentation

Once running, access:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/api/v1/health

### Endpoints

#### Core Passport Endpoints

- `POST /api/v1/passport/generate` - Generate new passport
- `GET /api/v1/passport/{id}` - Retrieve passport by ID
- `GET /api/v1/passport/{id}/pdf` - Download passport as PDF
- `GET /api/v1/passport/{id}/qr` - Get QR code image

#### Supporting Endpoints

- `GET /api/v1/models` - List available models
- `POST /api/v1/predict` - Raw prediction endpoint
- `GET /api/v1/health` - Health check

## Models Available

| Model | Type | R² | RMSE | Description |
|--------|------|-----|-------|-------------|
| Linear Regression | Regression | 0.6276 | 9.80 MPa | Baseline model |
| Random Forest | Regression | 0.8793 | 5.58 MPa | Ensemble model |
| XGBoost | Regression | **0.9353** | **4.08 MPa** | 🏆 **BEST MODEL** |
| Simple NN | Neural Network | 0.8625 | 5.95 MPa | Feedforward network |
| Deep NN | Neural Network | 0.8565 | 6.08 MPa | Deep network |
| Multi-task NN | Neural Network | 0.8667 | 5.86 MPa | Strength + Recyclability |

## MLflow Integration

The backend integrates with MLflow for production monitoring:

- **Prediction Logging:** Every prediction logged with input features and output
- **Model Performance:** Track production metrics over time
- **Error Logging:** Track prediction failures and model issues
- **Experiment Tracking:** Link production runs to development experiments

## Development

### Project Structure

```
webapp/backend/
├── main.py                      # FastAPI application entry point
├── requirements.txt             # Python dependencies
├── .env.example                # Environment variable template
├── models/
│   ├── loader.py               # Model loading with production artifacts
│   └── predictor.py            # Prediction logic
├── api/
│   ├── routes.py               # API route definitions
│   └── schemas.py              # Pydantic models
├── services/
│   ├── prediction_service.py   # ML prediction + MLflow
│   ├── sustainability_service.py  # Sustainability calculations
│   ├── passport_service.py     # Passport generation
│   └── mlflow_service.py     # MLflow logging
├── utils/
│   ├── qr_generator.py         # QR code generation
│   ├── pdf_generator.py        # PDF export
│   ├── config.py               # Configuration
│   └── feature_utils.py       # Feature engineering
└── tests/                      # Unit tests
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run specific test file
pytest tests/test_routes.py

# Run with coverage
pytest --cov=. --cov-report=html
```

## Deployment

### Render (Free Tier)

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect to GitHub repository
4. Set environment variables:
   - `MODELS_DIR`: Path to models directory
   - `CORS_ORIGINS`: Frontend URL
5. Deploy

Environment variables to set:
```bash
MODELS_DIR=/opt/render/project/src/models
CORS_ORIGINS=https://your-frontend.vercel.app
```

### Health Check

Verify deployment:
```bash
curl https://your-app.onrender.com/api/v1/health
```

## Troubleshooting

### Model Loading Issues

**Problem:** Models fail to load

**Solution:**
1. Verify `../models/` directory contains all `.pkl` and `.pth` files
2. Check `production_metadata.json` exists
3. Check Python dependencies match model versions
4. Review logs for specific error messages

### MLflow Connection Issues

**Problem:** MLflow logging fails

**Solution:**
1. Check `MLFLOW_TRACKING_URI` in `.env`
2. Verify MLflow server is accessible
3. Disable MLflow temporarily: Set `MLFLOW_ENABLED=false`

### CORS Issues

**Problem:** Frontend cannot connect to API

**Solution:**
1. Check `CORS_ORIGINS` includes frontend URL
2. Verify CORS middleware configuration in `main.py`
3. Check for CORS errors in browser console

## Contributing

1. Follow existing code style
2. Write tests for new features
3. Update API documentation
4. Log changes in commit messages

## License

This project is for educational and portfolio purposes.

## Author

**Raka Adrianto**
- Sustainability Program Manager @ Siemens
- Passionate about AI/ML for Climate Impact
- Preparing for Portfolio Lead roles in AI for Sustainability
