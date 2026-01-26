# Backend Local Testing - Quick Start

## Setup in 2 Minutes

### Step 1: Install Dependencies

```bash
# Navigate to backend
cd webapp/backend

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Verify Models Exist

```bash
# Check if models directory exists
ls ../models/

# You should see:
# - linear_regression.pkl
# - random_forest.pkl
# - xgboost.pkl
# - simple_nn.pth
# - deep_nn.pth
# - multitask_nn.pth
# - scaler_X.pkl
# - scaler_y_str.pkl
# - scaler_y_circ.pkl
# - production_metadata.json
# - production_features.json
```

### Step 3: Run API Server

```bash
# Option A: Run with uvicorn (recommended)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Option B: Run main.py directly
python main.py
```

### Step 4: Test API

**Option A: Automated Test Script**
```bash
# Install test dependency
pip install requests

# Run automated tests
python test_api.py
```

**Option B: Manual Testing in Browser**
1. Open: http://localhost:8000/api/v1/docs
2. Click "Try it out" on any endpoint
3. Execute request
4. View response

**Test Examples to Try:**

**1. Health Check:**
```
GET http://localhost:8000/api/v1/health
```

**2. List Models:**
```
GET http://localhost:8000/api/v1/models
```

**3. Generate Passport:**
```
POST http://localhost:8000/api/v1/passport/generate
Body:
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

## Expected Output

When you run the server, you should see:

```
============================================================
Starting Material Passport Generator API...
============================================================
App: Material Passport Generator API v1.0.0
API Prefix: /api/v1
Host: 0.0.0.0:8000
MLflow: True
============================================================
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
============================================================
✓ All services initialized successfully
============================================================

API Documentation: http://0.0.0.0:8000/api/v1/docs
Health Check: http://0.0.0.0:8000/api/v1/health
============================================================

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Troubleshooting

### "Models directory not found"
```bash
# Verify models directory exists from backend folder
ls ../models/

# If not, update MODELS_DIR in .env
MODELS_DIR=/absolute/path/to/models
```

### "Port 8000 already in use"
```bash
# Windows - find process using port 8000
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PROCESS_ID> /F

# Then restart server
```

### "Module not found" errors
```bash
# Ensure virtual environment is activated
# Check (venv) in your terminal prompt

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### "MLflow initialization failed"
- This is OK - the API will still work
- Check MLflow logs for more details
- To disable MLflow: Set `MLFLOW_ENABLED=false` in .env

## Success Indicators

✅ Server starts without errors
✅ "All services initialized successfully" message
✅ Can access http://localhost:8000/api/v1/docs
✅ Health check returns `"status": "healthy"`
✅ Models endpoint lists all 6 models
✅ Can generate a passport successfully
✅ Response time < 500ms for passport generation

## Next Steps

After local testing succeeds:

1. ✅ **Review results**: Check MLflow logs in `../mlruns/`
2. 📊 **Performance**: Note response times for each endpoint
3. 🚀 **Deployment**: Follow WEB_APP_IMPLEMENTATION_PLAN.md for Render deployment
4. 🌐 **Frontend**: Start building Next.js frontend (Week 2)
5. 📝 **Documentation**: Document any issues encountered

## Testing Checklist

- [ ] Server starts successfully
- [ ] All 6 models loaded
- [ ] All 3 scalers loaded
- [ ] Health endpoint returns 200 OK
- [ ] Models endpoint returns list of 6 models
- [ ] XGBoost marked as best model
- [ ] Generate passport with XGBoost
- [ ] Generate passport with different model
- [ ] Retrieve passport by ID
- [ ] Download PDF (check file opens)
- [ ] Get QR code (check image displays)
- [ ] Raw prediction works
- [ ] MLflow logs created in `../mlruns/`
- [ ] No errors in console output

**When all checkboxes complete:** ✅ Backend ready for deployment!
