# Quick Start Guide - MVP Deployment

## Option 1: Run Locally (Testing)

### Step 1: Navigate to MVP directory
```bash
cd webapp/mvp
```

### Step 2: Run the quick start script (Mac/Linux)
```bash
./run.sh
```

### Or run manually:
```bash
# Create venv
python3 -m venv venv

# Activate
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements_mvp.txt

# Run app
streamlit run app.py
```

### Step 3: Open in browser
App will open at: **http://localhost:8501**

---

## Option 2: Deploy to Streamlit Cloud (Production)

### Step 1: Push to GitHub

```bash
cd webapp/mvp
git init
git add .
git commit -m "Initial MVP"

# Create repository on GitHub first, then:
git remote add origin https://github.com/yourusername/material-passport-mvp.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to: https://share.streamlit.io
2. Click: **"New app"**
3. Connect your GitHub repository
4. Select: `material-passport-mvp` repository
5. Select: `app.py` as main file
6. Click: **"Deploy"**

Your app will be live at: 
```
https://yourusername-material-passport-mvp.streamlit.app
```

### Step 3: Verify deployment

Check that:
- [ ] App loads without errors
- [ ] Model loads successfully
- [ ] Input form works
- [ ] Predictions display correctly
- [ ] Feedback system works

---

## Pre-Flight Checklist

Before deploying, verify:

### Model Files
```bash
ls -lh ../models/xgboost.pkl
ls -lh ../models/scaler.pkl
```

Both should exist and be >0 bytes.

### Dependencies
```bash
pip install -r requirements_mvp.txt
python -c "import streamlit, joblib, sklearn, xgboost, matplotlib; print('✅ All OK')"
```

### Test Locally First
```bash
streamlit run app.py
```

- [ ] Enter sample values
- [ ] Click "Generate Passport"
- [ ] Verify prediction appears
- [ ] Check sustainability metrics display

---

## Example Values to Test

### Test Case 1: Standard Concrete
```
Cement: 300 kg/m³
Slag: 0 kg/m³
Fly Ash: 0 kg/m³
Water: 170 kg/m³
Superplasticizer: 0 kg/m³
Coarse Aggregate: 950 kg/m³
Fine Aggregate: 700 kg/m³
Age: 28 days
```
Expected: Strength ~35-40 MPa, Grade B

### Test Case 2: High Strength
```
Cement: 400 kg/m³
Slag: 100 kg/m³
Fly Ash: 0 kg/m³
Water: 160 kg/m³
Superplasticizer: 5 kg/m³
Coarse Aggregate: 950 kg/m³
Fine Aggregate: 700 kg/m³
Age: 28 days
```
Expected: Strength ~45-50 MPa, Grade A

### Test Case 3: Eco-Friendly
```
Cement: 250 kg/m³
Slag: 150 kg/m³
Fly Ash: 100 kg/m³
Water: 170 kg/m³
Superplasticizer: 5 kg/m³
Coarse Aggregate: 950 kg/m³
Fine Aggregate: 700 kg/m³
Age: 90 days
```
Expected: Strength ~35-40 MPa, Grade A+, High circularity

---

## Troubleshooting

### "Error loading models"
**Problem:** Model files not found
**Solution:** Check that `../models/xgboost.pkl` and `../models/scaler.pkl` exist

### "ImportError: No module named 'streamlit'"
**Problem:** Dependencies not installed
**Solution:**
```bash
pip install -r requirements_mvp.txt
```

### "ValueError: X has n features, but scaler is expecting n features"
**Problem:** Input data mismatch
**Solution:** Ensure all 8 features are present and in correct order

### App is slow on Streamlit Cloud
**Problem:** Free tier has cold start
**Solution:** First load takes ~30s, subsequent loads are faster

---

## User Testing Script

### For Internal Testing (Day 1-2)

```bash
# Run locally
streamlit run app.py

# Test these scenarios:
1. Enter sample values → Generate passport
2. Adjust sliders → Re-generate
3. Check sustainability metrics
4. Test feedback system
5. Try all example compositions
```

### For External Testing (Day 3-5)

Share this message:

```
🏗️ Material Passport Generator - Test Needed

I built a tool to generate digital material passports for concrete. 
It uses AI to predict strength and calculate sustainability metrics.

LINK: https://your-app.streamlit.app

WHO SHOULD TEST:
✅ Manufacturers - Check time savings and compliance
✅ Consultants - Check circularity analysis
✅ Architects - Check sustainability metrics

WHAT TO DO:
1. Open the link
2. Enter your concrete composition (or use sliders)
3. Click "Generate Passport"
4. Rate the usefulness (1-5 stars)
5. Add feedback on what's missing

Takes 2 minutes. Your feedback shapes the product!

Please reply with:
- Is this useful?
- What's missing?
- Would you use this regularly?
```

---

## Deployment Verification

### Checklist for Go-Live

- [ ] Tested locally with all test cases
- [ ] Deployed to Streamlit Cloud
- [ ] URL works in Chrome, Firefox, Safari
- [ ] Mobile responsive (check on phone)
- [ ] All sliders work
- [ ] Predictions generate correctly
- [ ] Feedback system functional
- [ ] No console errors
- [ ] Share link with test users

---

## Next Steps

### Day 1-2: Internal Testing
- [ ] Run app locally
- [ ] Test all features
- [ ] Fix any bugs

### Day 3: Deploy
- [ ] Push to GitHub
- [ ] Deploy to Streamlit Cloud
- [ ] Verify all features work

### Day 4-7: User Testing
- [ ] Share with 10-20 users
- [ ] Collect feedback
- [ ] Track metrics

### Day 8-14: Iterate
- [ ] Analyze feedback
- [ ] Prioritize improvements
- [ ] Build next version

---

## Resources

- **Streamlit Docs:** https://docs.streamlit.io
- **Streamlit Cloud:** https://share.streamlit.io
- **Project README:** `../README_MVP.md`
- **Main Project:** `../../README.md`

---

**Ready to launch? Follow the steps above!** 🚀
