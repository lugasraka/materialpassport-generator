# Material Passport Generator - MVP

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Existing trained models in `../models/` directory

### Installation

1. **Create virtual environment:**
```bash
cd webapp/mvp
python -m venv venv

# Activate
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

2. **Install dependencies:**
```bash
pip install -r requirements_mvp.txt
```

### Run Locally

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 📋 Features

### For Manufacturers (Sustainability Managers)
- ✅ Generate EU-compliant Digital Product Passports
- ✅ Auto-calculate sustainability metrics
- ✅ Time savings: ~5 hours vs manual calculation
- ✅ Compliance checklist (DPP, EN 206)

### For Consultants (Circular Economy)
- ✅ Instant circularity score (0-100)
- ✅ Benchmark against industry averages
- ✅ Material composition analysis
- ✅ CO2 emission estimation

### For Architects/Designers
- ✅ Visual sustainability dashboard
- ✅ Material grade (A-E)
- ✅ Green building metrics alignment
- ✅ Performance benchmarking

---

## 🎯 MVP Success Metrics

### Week 1 KPIs
| Metric | Target | How to Track |
|--------|--------|-------------|
| Unique users | 20+ | Streamlit analytics |
| Completion rate | >60% | Form submissions / visits |
| Satisfaction | >3.5/5 | Built-in rating |
| "Would use again" | >50% | Post-use survey |
| Time to value | <2 min | Prediction speed |

---

## 📊 Technical Architecture

```
Streamlit App (app.py)
├── Model Loading (joblib)
│   ├── XGBoost model (xgboost.pkl)
│   └── Scaler (scaler.pkl)
├── Input Form (8 sliders)
├── Prediction Pipeline
│   ├── Input scaling
│   ├── XGBoost prediction
│   └── Sustainability metrics
├── Passport Display (HTML/CSS)
├── Visualization (matplotlib/seaborn)
└── Feedback Collection
```

---

## 🔄 User Feedback Loop

### What We're Testing
1. **Value Proposition**: Is this useful enough to replace manual calculation?
2. **User Experience**: Is the interface intuitive for all personas?
3. **Feature Prioritization**: What features do users want most?

### Feedback Channels
- Built-in rating system (1-5 stars)
- Open text feedback box
- Persona-specific feedback prompts
- Usage analytics (input patterns, completion rates)

---

## 🚀 Deployment (Streamlit Cloud)

### Step 1: Prepare for Deployment

1. **Create GitHub repository**
```bash
cd webapp/mvp
git init
git add app.py requirements_mvp.txt README_MVP.md
git commit -m "Initial MVP"
git remote add origin <your-repo-url>
git push origin main
```

2. **Verify model files are accessible**
   - The app expects models in `../models/` relative to app.py
   - Ensure XGBoost model and scaler exist

### Step 2: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub repository
4. Point to `webapp/mvp/app.py`
5. Click "Deploy"

**URL format:** `https://your-username-material-passport-generator-mvp.streamlit.app`

### Step 3: Share with Users

Create shareable links:
```
🏗️ Material Passport Generator MVP
Test it here: https://your-app.streamlit.app

For Manufacturers:
- Generate EU-compliant passports
- Save 5+ hours per product

For Consultants:
- Instant circularity analysis
- Benchmark against industry

For Architects:
- Compare material sustainability
- Green building metrics
```

---

## 📈 Week 2: Iteration Plan

### If Feedback is Positive (≥4/5 stars)
**Add:**
- [ ] PDF export functionality
- [ ] Multiple composition comparison
- [ ] Save/load presets
- [ ] Email/passcode for saved passports

**Improve:**
- [ ] Add more materials (steel, wood)
- [ ] A/B test model versions
- [ ] Confidence intervals

### If Feedback is Mixed (2.5-3.9 stars)
**Investigate:**
- [ ] Which features are least useful?
- [ ] What's causing friction?
- [ ] Are personas confused by UI?

**Improve:**
- [ ] Simplify input form
- [ ] Add tooltips/help text
- [ ] Better explanations of metrics

### If Feedback is Negative (<2.5 stars)
**Pivot:**
- [ ] Revisit user interviews
- [ ] Test different value proposition
- [ ] Consider narrower scope

---

## 🐛 Troubleshooting

### Issue: Model not found
```
Error: Error loading models
```
**Solution:** Verify `../models/xgboost.pkl` and `../models/scaler.pkl` exist

### Issue: Import errors
```
ModuleNotFoundError: No module named 'streamlit'
```
**Solution:** Ensure virtual environment is activated and dependencies installed

### Issue: Scaler transform error
```
ValueError: X has n features, but scaler is expecting n features
```
**Solution:** Ensure input has all 8 features and they're in correct order

---

## 📝 Development Notes

### File Structure
```
webapp/mvp/
├── app.py                    # Main Streamlit application
├── requirements_mvp.txt       # Python dependencies
├── README_MVP.md             # This file
└── venv/                     # Virtual environment (created locally)
```

### Key Components

1. **Model Loading**: Cached resource to prevent reloading
2. **Input Form**: 8 sliders for concrete composition
3. **Prediction**: XGBoost model with scaling
4. **Sustainability Metrics**: Recycled content, circularity, CO2
5. **Passport Display**: HTML/CSS with responsive layout
6. **Feedback**: Built-in rating and text feedback
7. **Visualization**: Circular gauge, benchmark metrics

### Model Performance
- **Model**: XGBoost Regressor
- **Test R²**: 0.9101
- **Test RMSE**: 4.81 MPa
- **Training samples**: 1,030

---

## 🎓 Learning Goals

This MVP tests:
1. **Problem-Solution Fit**: Do users actually need this?
2. **User Experience**: Is the interface intuitive?
3. **Value Delivery**: Does it save time/money?
4. **Feature Prioritization**: What should we build next?

### Questions to Answer Week 1
- What composition values do users test most?
- Which persona engages most?
- What features are requested most?
- Where do users drop off?

---

## 🤝 Getting Help

### Streamlit Resources
- [Streamlit Documentation](https://docs.streamlit.io)
- [Streamlit Community](https://discuss.streamlit.io)
- [Streamlit Cloud Guide](https://docs.streamlit.io/streamlit-cloud)

### Project Resources
- Main README: `../../README.md`
- PRD: `../../docs/PRD.md`
- Web App Plan: `../../WEB_APP_IMPLEMENTATION_PLAN.md`

---

## 📅 Timeline

### Week 1 (Days 1-7)
- [x] Build MVP app (Day 1-2)
- [ ] Deploy to Streamlit Cloud (Day 3)
- [ ] Test with 5-10 real users (Day 3-4)
- [ ] Collect and analyze feedback (Day 5-7)

### Week 2 (Days 8-14)
- [ ] Iterate based on feedback
- [ ] Add requested features
- [ ] Test with 20+ users
- [ ] Prepare for production roadmap

---

## 🌟 Success Criteria

### MVP Success (Continue to Production)
- 20+ unique users
- >60% completion rate
- >3.5/5 satisfaction
- Clear feature requests for next version

### MVP Needs Pivot (<60% completion)
- Users confused by interface
- Low engagement
- Negative feedback

### MVP Fail (<10 users, <2/5 rating)
- Value proposition not validated
- Revisit problem statement
- Consider different approach

---

**Built for rapid iteration and user feedback.**

*Last updated: January 2025*
