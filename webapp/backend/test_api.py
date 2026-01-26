"""
Test script for Material Passport Generator API

Run this script to test all API endpoints locally.
"""
import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000"

print("=" * 60)
print("Material Passport Generator API - Test Script")
print("=" * 60)
print(f"\nAPI URL: {BASE_URL}")
print("=" * 60)

# Test 1: Health Check
print("\n[Test 1] Health Check")
print("-" * 60)
try:
    response = requests.get(f"{BASE_URL}/")
    data = response.json()
    print(f"✓ Status: {data.get('status')}")
    print(f"✓ App: {data.get('app')}")
    print(f"✓ Version: {data.get('version')}")
    print(f"✓ Models Loaded: {data.get('models_loaded', 0)}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 2: Get Available Models
print("\n[Test 2] Get Available Models")
print("-" * 60)
try:
    response = requests.get(f"{BASE_URL}/api/v1/models")
    data = response.json()
    models = data.get('models', [])
    print(f"✓ Found {len(models)} models:")
    for model in models:
        print(f"  - {model['name']} ({model['type']})")
        print(f"    R²: {model['performance']['r2']:.4f}")
        print(f"    RMSE: {model['performance']['rmse']:.2f}")
        if model.get('best_for_production'):
            print(f"    ★ BEST MODEL FOR PRODUCTION")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 3: Generate Passport
print("\n[Test 3] Generate Material Passport")
print("-" * 60)
try:
    # Example composition
    composition = {
        "cement": 350.0,
        "blast_furnace_slag": 150.0,
        "fly_ash": 100.0,
        "water": 180.0,
        "superplasticizer": 7.5,
        "coarse_aggregate": 1000.0,
        "fine_aggregate": 750.0,
        "age": 28
    }
    
    payload = {
        "composition": composition,
        "model_name": "xgboost"  # Use best model
    }
    
    print("Sending composition:")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(
        f"{BASE_URL}/api/v1/passport/generate",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 201:
        passport = response.json()
        print(f"\n✓ Passport Generated: {passport['id']}")
        print(f"\nPredictions:")
        strength = passport['predictions']['compressive_strength']
        print(f"  Compressive Strength: {strength['value']:.2f} {strength['unit']}")
        print(f"    Confidence: {strength['confidence']:.0%}")
        
        recyclability = passport['predictions']['recyclability']
        print(f"  Recyclability: {recyclability['score']}/100 (Grade {recyclability['grade']})")
        
        print(f"\nSustainability Metrics:")
        metrics = passport['sustainability_metrics']
        print(f"  Circularity Score: {metrics['circularity_score']}/100")
        print(f"  CO2 Emissions: {metrics['co2_emissions']['value']:.2f} {metrics['co2_emissions']['unit']}")
        print(f"  Recycled Content: {metrics['recycled_content']['percentage']:.1f}%")
        print(f"    Materials: {', '.join(metrics['recycled_content']['materials'])}")
        print(f"  Grade: {metrics['sustainability_grade']}")
        print(f"  Certification: {passport['certification']}")
        
        passport_id = passport['id']
        print(f"\nPassport URL: {BASE_URL}/api/v1/passport/{passport_id}")
    else:
        print(f"✗ Failed: HTTP {response.status_code}")
        print(f"  Response: {response.text}")
        passport_id = None

except Exception as e:
    print(f"✗ Failed: {e}")
    passport_id = None

# Test 4: Retrieve Passport (if passport was generated)
print("\n[Test 4] Retrieve Passport by ID")
print("-" * 60)
try:
    if 'passport_id' in locals():
        response = requests.get(f"{BASE_URL}/api/v1/passport/{passport_id}")
        if response.status_code == 200:
            passport = response.json()
            print(f"✓ Retrieved passport: {passport['id']}")
            print(f"  Material: {passport['material_type']}")
        else:
            print(f"✗ Passport not found")
    else:
        print("⊘ Skipped - no passport ID from previous test")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 5: Raw Prediction
print("\n[Test 5] Raw Prediction (no passport generation)")
print("-" * 60)
try:
    composition = {
        "cement": 400.0,
        "blast_furnace_slag": 100.0,
        "fly_ash": 50.0,
        "water": 170.0,
        "superplasticizer": 8.0,
        "coarse_aggregate": 950.0,
        "fine_aggregate": 800.0,
        "age": 28
    }
    
    payload = {
        "composition": composition,
        "model_name": "xgboost"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/predict",
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Predictions:")
        strength = data['strength']
        print(f"  Strength: {strength['value']:.2f} {strength['unit']} (confidence: {strength['confidence']:.0%})")
        recyclability = data['recyclability']
        print(f"  Recyclability: {recyclability['score']}/100 (Grade {recyclability['grade']})")
    else:
        print(f"✗ Failed: HTTP {response.status_code}")
        
except Exception as e:
    print(f"✗ Failed: {e}")

print("\n" + "=" * 60)
print("Testing Complete!")
print("=" * 60)
print("\nNext Steps:")
print("1. Open browser: http://localhost:8000/docs")
print("2. Explore Swagger UI documentation")
print("3. Try generating passports with different compositions")
print("4. Download PDF for generated passports")
print("5. Scan QR codes to verify")
print("=" * 60)
