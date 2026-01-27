"""
Test script to verify MVP can run
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("MVP Pre-Flight Check")
print("=" * 60)

# Check 1: Model files exist
print("\n1. Checking model files...")
# Models are two levels up from mvp directory (webapp/mvp -> webapp/ -> project root)
models_dir = Path(__file__).parent.parent.parent / 'models'

model_files = [
    models_dir / 'xgboost.pkl',
    models_dir / 'scaler.pkl'
]

for file_path in model_files:
    if file_path.exists():
        size = file_path.stat().st_size
        print(f"   ✅ {file_path.name} ({size:,} bytes)")
    else:
        print(f"   ❌ {file_path.name} - NOT FOUND")
        sys.exit(1)

# Check 2: Dependencies
print("\n2. Checking dependencies...")
dependencies = [
    'streamlit',
    'pandas',
    'numpy',
    'sklearn',
    'xgboost',
    'joblib',
    'matplotlib',
    'seaborn'
]

missing_deps = []
for dep in dependencies:
    try:
        __import__(dep)
        print(f"   ✅ {dep}")
    except ImportError:
        print(f"   ❌ {dep} - NOT INSTALLED")
        missing_deps.append(dep)

if missing_deps:
    print(f"\n   ⚠️  Missing dependencies: {', '.join(missing_deps)}")
    print(f"   Run: pip install -r requirements_mvp.txt")
    sys.exit(1)

# Check 3: Load model
print("\n3. Testing model loading...")
try:
    import joblib
    model = joblib.load(models_dir / 'xgboost.pkl')
    scaler = joblib.load(models_dir / 'scaler.pkl')
    
    print(f"   ✅ Model loaded: {type(model).__name__}")
    print(f"   ✅ Scaler loaded: {type(scaler).__name__}")
except Exception as e:
    print(f"   ❌ Error loading model: {e}")
    sys.exit(1)

# Check 4: Test prediction
print("\n4. Testing prediction...")
try:
    import pandas as pd
    
    # Create sample input
    sample_input = pd.DataFrame([{
        'cement': 300,
        'slag': 0,
        'fly_ash': 0,
        'water': 170,
        'superplasticizer': 0,
        'coarse_aggregate': 950,
        'fine_aggregate': 700,
        'age': 28
    }])
    
    # Scale and predict
    sample_scaled = scaler.transform(sample_input)
    prediction = model.predict(sample_scaled)
    
    print(f"   ✅ Prediction successful: {prediction[0]:.2f} MPa")
except Exception as e:
    print(f"   ❌ Prediction error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Summary
print("\n" + "=" * 60)
print("✅ ALL CHECKS PASSED")
print("=" * 60)
print("\nReady to run MVP!")
print("Run: streamlit run app.py")
print("Or: ./run.sh")
print("=" * 60)
