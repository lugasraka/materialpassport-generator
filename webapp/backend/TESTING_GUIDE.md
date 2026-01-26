# Backend API Testing Guide

## Prerequisites

Before running tests, ensure:

1. **Python 3.9+** is installed
2. **Dependencies** are installed:
   ```bash
   cd webapp/backend
   pip install -r requirements.txt
   ```
3. **Models** exist in `../models/` directory:
   ```bash
   ls ../models/*.pkl
   ls ../models/*.pth
   ls ../models/production_*.json
   ```
4. **Environment variables** are configured (optional):
   ```bash
   # Edit .env if needed (uses .env.example defaults)
   # Default configuration should work
   ```

## Quick Start

### 1. Start the API Server

```bash
cd webapp/backend

# Option 1: Run directly with Python
python -m uvicorn main:app --reload

# Option 2: Run main.py directly
python main.py

# Option 3: Use uvicorn command
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Verify Server Started

You should see:
```
===========================================================
Starting Material Passport Generator API...
===========================================================
App: Material Passport Generator API v1.0.0
API Prefix: /api/v1
Host: 0.0.0.0:8000
MLflow: True
===========================================================
✓ MLflow service initialized
✓ Loaded production metadata from 6 models
✓ Loaded production features schema
✓ Loaded Linear Regression
✓ Loaded Random Forest
✓ Loaded XGBoost (Best Model)
✓ Loaded Simple NN
✓ Loaded Deep NN
✓ Loaded Multi-task NN
✓ Loaded scaler_X
✓ Loaded scaler_y_str
✓ Loaded scaler_y_circ
✓ All models loaded: 6 models, 3 scalers
✓ Prediction service initialized
✓ Sustainability service initialized
✓ Passport service initialized
===========================================================
✓ All services initialized successfully
===========================================================

API Documentation: http://0.0.0.0:8000/api/v1/docs
Health Check: http://0.0.0.0:8000/api/v1/health
===========================================================

INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 3. Run Automated Tests

In a new terminal (keep server running):

```bash
cd webapp/backend

# Install test dependencies
pip install requests

# Run test script
python test_api.py
```

## Manual Testing with Swagger UI

### 1. Open Swagger Documentation
Open browser: http://localhost:8000/api/v1/docs

### 2. Test Health Check
```
Endpoint: GET /
or
Endpoint: GET /api/v1/health
```
**Expected Response:**
```json
{
  "app": "Material Passport Generator API",
  "version": "1.0.0",
  "status": "healthy",
  "endpoints": {
    "health": "/api/v1/health",
    "models": "/api/v1/models",
    "docs": "/api/v1/docs"
  },
  "models_loaded": 6,
  "mlflow_enabled": true
}
```

### 3. List Available Models
```
Endpoint: GET /api/v1/models
```
**Expected Response:**
```json
{
  "models": [
    {
      "name": "xgboost",
      "type": "regression",
      "description": "Gradient Boosted Trees (Best Production Model)",
      "performance": {
        "r2": 0.9353,
        "rmse": 4.08,
        "mae": 2.82
      },
      "features": "16 aggregate",
      "best_for_production": true
    },
    ...
  ]
}
```

### 4. Generate Passport
```
Endpoint: POST /api/v1/passport/generate
```

**Request Body:**
```json
{
  "composition": {
    "cement": 350.0,
    "blast_furnace_slag": 150.0,
    "fly_ash": 100.0,
    "water": 180.0,
    "superplasticizer": 7.5,
    "coarse_aggregate": 1000.0,
    "fine_aggregate": 750.0,
    "age": 28
  },
  "model_name": "xgboost"
}
```

**Expected Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-4466554400000",
  "material_type": "Concrete",
  "composition": { ... },
  "predictions": {
    "compressive_strength": {
      "value": 45.23,
      "unit": "MPa",
      "confidence": 0.9353,
      "model": "xgboost"
    },
    "recyclability": {
      "score": 78,
      "grade": "B",
      "model": "multitask_nn"
    }
  },
  "sustainability_metrics": {
    "circularity_score": 78,
    "co2_emissions": {
      "value": 320.5,
      "unit": "kg CO2/m³"
    },
    "recycled_content": {
      "percentage": 35.0,
      "materials": ["Blast Furnace Slag", "Fly Ash"]
    },
    "sustainability_grade": "B (Good)"
  },
  "certification": "Circular Economy Compliant",
  "generated_at": "2025-01-26T14:30:00Z",
  "qr_code_url": "/api/v1/passport/550e8400-e29b-41d4-a716-4466554400000/qr"
}
```

### 5. Retrieve Passport
```
Endpoint: GET /api/v1/passport/{passport_id}
```
Use the ID from the previous response.

### 6. Download PDF
```
Endpoint: GET /api/v1/passport/{passport_id}/pdf
```
- Opens PDF download in browser
- Save as `material_passport_{id}.pdf`

### 7. Get QR Code
```
Endpoint: GET /api/v1/passport/{passport_id}/qr
```
- Displays QR code image
- Right-click to save

### 8. Raw Prediction
```
Endpoint: POST /api/v1/predict
```
Same request as passport generation, but returns only predictions without creating a passport.

## Common Issues & Solutions

### Issue: "Models directory not found"
**Solution:**
```bash
# Check if models directory exists at correct location
cd webapp/backend
ls ../models/

# If models are in different location, update .env:
# MODELS_DIR=/path/to/models
```

### Issue: "MLflow initialization failed"
**Solution:**
```bash
# Disable MLflow temporarily in .env:
MLFLOW_ENABLED=false

# Or check MLflow tracking URI:
MLFLOW_TRACKING_URI=../../mlruns
```

### Issue: Import errors (Module not found)
**Solution:**
```bash
# Install dependencies
cd webapp/backend
pip install -r requirements.txt

# Make sure you're using virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Port already in use
**Solution:**
```bash
# Change port in .env:
PORT=8001

# Or kill process using port 8000:
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -i :8000
kill -9 <PID>
```

### Issue: MLflow logging errors
**Solution:**
- MLflow errors are non-fatal - API will continue working
- Check MLflow logs in terminal output
- Verify `mlruns/` directory exists in project root

## Testing Checklist

- [ ] Server starts successfully
- [ ] Health check returns healthy
- [ ] All 6 models loaded
- [ ] Models endpoint lists all models
- [ ] XGBoost marked as best model
- [ ] Passport generation works
- [ ] Predictions look reasonable (strength 10-100 MPa)
- [ ] Sustainability metrics calculated correctly
- [ ] Passport retrieval works
- [ ] PDF download works
- [ ] QR code generation works
- [ ] Raw prediction endpoint works
- [ ] MLflow logs predictions (check mlruns/)
- [ ] No errors in server logs

## Performance Testing

### Generate Multiple Passports
```python
import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

# Generate 10 passports
for i in range(10):
    composition = {
        "cement": 300.0 + i * 10,
        "blast_furnace_slag": 100.0,
        "fly_ash": 50.0,
        "water": 170.0,
        "superplasticizer": 7.0,
        "coarse_aggregate": 1000.0,
        "fine_aggregate": 800.0,
        "age": 28
    }
    
    start = time.time()
    response = requests.post(f"{BASE_URL}/passport/generate", json={"composition": composition})
    end = time.time()
    
    print(f"Passport {i+1}: {end-start*1000:.0f}ms (HTTP {response.status_code})")
```

**Expected:** < 200ms per passport (ML model prediction + calculations)

## Next Steps After Testing

1. ✅ If all tests pass: Ready for deployment
2. 🚀 Deploy to Render: See WEB_APP_IMPLEMENTATION_PLAN.md
3. 🌐 Build Frontend: Next.js application
4. 📝 Document: API endpoints and examples
5. 📊 Monitor: MLflow logs for production tracking
