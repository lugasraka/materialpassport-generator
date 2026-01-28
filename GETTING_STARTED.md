# Getting Started Guide
## Material Passport Generator - AI/ML Project

Welcome! This guide will help you set up and run the Material Passport Generator MVP web application.

## What This Project Offers

An AI-powered system that automatically generates digital material passports for building products, demonstrating:
- **Machine Learning**: XGBoost-based regression for concrete strength prediction
- **Sustainability**: Circular economy metrics and carbon footprint estimation
- **Product Management**: User-centered design and impact measurement
- **Web Application**: Production-ready Streamlit interface with multilingual support

## Prerequisites

Before starting, ensure you have:
- **Python 3.9+** installed
- **Git** (optional, for version control)
- **4GB RAM minimum** (8GB recommended)
- **1GB free disk space**
- **Internet connection** (for initial setup)

## Quick Start - Run the MVP Web Application

### Option 1: Using the Launch Script (Recommended)

```bash
# Navigate to MVP directory
cd webapp/mvp

# Run the launch script
bash run.sh
```

The app will automatically:
1. Create a virtual environment
2. Install all dependencies
3. Launch the Streamlit application
4. Open in your default browser at `http://localhost:8501`

### Option 2: Manual Setup

```bash
# Navigate to MVP directory
cd webapp/mvp

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements_mvp.txt

# Run the application
streamlit run app.py
```

The application will open at `http://localhost:8501`

### Using the Application

1. **Enter Concrete Composition**: Input values for cement, slag, fly ash, water, superplasticizer, aggregates, and age
2. **Generate Passport**: Click to get AI-powered predictions and sustainability metrics
3. **Review Results**: See compressive strength, circularity score, CO2 emissions, and sustainability grade
4. **Export PDF**: Download a professional material passport document
5. **Provide Feedback**: Rate the application and suggest features

## Project Structure Overview

```
material-passport-generator/
│
├── data/
│   ├── raw/                          # Original dataset
│   └── processed/                    # Cleaned + enriched data
│
├── notebooks/                        # Jupyter notebooks for ML development
│   ├── 01_data_exploration.ipynb
│   ├── 02_baseline_models.ipynb
│   └── 03_deep_learning.ipynb
│
├── src/                              # Source code for ML development
│   ├── data/                         # Data processing scripts
│   └── features/                     # Feature engineering
│
├── models/                           # Trained ML models
│   ├── xgboost.pkl                   # Production model
│   └── scaler.pkl                    # Feature scaler
│
├── webapp/                           # Web application
│   └── mvp/                          # MVP Streamlit application (PRODUCTION)
│       ├── app.py                    # Main application
│       ├── requirements_mvp.txt      # Dependencies
│       ├── run.sh                    # Launch script
│       └── README_MVP.md             # MVP documentation
│
├── docs/                             # Documentation
│   └── PRD.md                        # Product requirements
│
└── README.md                         # Project overview
```

## Exploration Paths

This is a completed portfolio project. Choose your exploration path based on your interests:

### Path 1: Use the Application (Quickest)
**For those wanting to see the final product**

1. Run the MVP web application (see Quick Start above)
2. Generate material passports with different compositions
3. Export PDF documents
4. Explore sustainability metrics and grading
5. Review the code in `webapp/mvp/app.py`

### Path 2: Understand the ML Models
**For those interested in the AI/ML development**

1. **Data Exploration** - `notebooks/01_data_exploration.ipynb`
   - Load and inspect the concrete compressive strength dataset
   - Understand sustainability metrics calculation
   - Identify patterns and correlations

2. **Baseline Models** - `notebooks/02_baseline_models.ipynb`
   - Linear Regression, Random Forest, XGBoost
   - Model evaluation and comparison
   - Feature engineering techniques

3. **Deep Learning** - `notebooks/03_deep_learning.ipynb`
   - Neural network implementations
   - Multi-task learning (strength + recyclability)
   - Model selection rationale

### Path 3: ML Development Setup
**For those wanting to experiment with models**

```bash
# Navigate to project root
cd material-passport-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install ML development dependencies
pip install -r requirements.txt

# Download and prepare dataset
python src/data/download_dataset.py

# Launch Jupyter notebooks
jupyter notebook
```

### Path 4: Product & Documentation Review
**For those interested in product management aspects**

1. Review [docs/PRD.md](docs/PRD.md) - Product Requirements Document
2. Review [webapp/mvp/README_MVP.md](webapp/mvp/README_MVP.md) - MVP documentation
3. Examine user research, personas, and feature prioritization
4. Study success metrics and KPIs definition

## Dataset Overview

**Concrete Compressive Strength Dataset**
- **Source:** UCI Machine Learning Repository
- **Size:** 1,030 instances
- **License:** Creative Commons Attribution 4.0 (CC BY 4.0)
- **Purpose:** Predict concrete strength from composition

**Input Features (8):**
1. Cement (kg/m³)
2. Blast Furnace Slag (kg/m³) - recycled industrial waste
3. Fly Ash (kg/m³) - recycled coal combustion byproduct
4. Water (kg/m³)
5. Superplasticizer (kg/m³)
6. Coarse Aggregate (kg/m³)
7. Fine Aggregate (kg/m³)
8. Age (days)

**Target Output:**
- Compressive Strength (MPa)

**Calculated Sustainability Metrics:**
- Recycled Content Percentage
- Circularity Score (0-100 scale)
- CO2 Emissions Estimate
- Sustainability Grade (A-E)

## Key Learning Objectives

By completing this project, you'll demonstrate:

**Technical Skills:**
- Data preprocessing and feature engineering
- ML model selection and evaluation
- Deep learning with PyTorch
- Model deployment and APIs
- MLOps basics (experiment tracking)

**Product Management:**
- User research and personas
- Feature prioritization (MoSCoW)
- Success metrics definition
- Stakeholder mapping
- Impact measurement

**Domain Expertise:**
- Building materials sustainability
- Circular economy principles
- Regulatory landscape (EU DPP)
- Life cycle thinking

## Troubleshooting

### Issue: Application won't start
**Solution:**
```bash
# Ensure you're in the correct directory
cd webapp/mvp

# Check Python version
python3 --version  # Should be 3.9+

# Try manual installation
pip install streamlit xgboost scikit-learn pandas reportlab
streamlit run app.py
```

### Issue: "ModuleNotFoundError"
**Solution:** Ensure virtual environment is activated
```bash
# Check if (venv) appears in terminal
# If not, activate it:
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements_mvp.txt
```

### Issue: "Model file not found"
**Solution:** Ensure you're running from the correct directory
```bash
# The app expects models in ../../models/
# Run from webapp/mvp directory:
cd webapp/mvp
streamlit run app.py
```

### Issue: Port already in use
**Solution:**
```bash
# Specify a different port
streamlit run app.py --server.port 8502
```

### Issue: PDF export fails
**Solution:** Install reportlab explicitly
```bash
pip install reportlab
```

## Project Completion Status

This project demonstrates:

**Completed Components:**
- Data exploration and analysis
- Multiple ML model implementations (Linear Regression, Random Forest, XGBoost, Neural Networks)
- Production model selection and deployment (XGBoost, R² = 0.91)
- Sustainability metrics calculation
- Web application with Streamlit
- PDF export functionality
- Multilingual support
- User feedback system
- Complete documentation (PRD, technical docs, user guides)

**Technical Achievements:**
- Strength prediction R² = 0.91 (target: >0.85)
- RMSE = 4.81 MPa (target: <5 MPa)
- Model inference <100ms per passport
- 90% reduction in manual passport creation time

## Additional Resources

**Documentation:**
- [README.md](README.md) - Project overview and features
- [docs/PRD.md](docs/PRD.md) - Product Requirements Document
- [webapp/mvp/README_MVP.md](webapp/mvp/README_MVP.md) - Complete MVP documentation
- Jupyter notebooks in `notebooks/` - ML development process

**Common Questions:**

**Q: Do I need GPU for this project?**
A: No, the dataset is small enough for CPU training and inference.

**Q: Can I use my own data?**
A: Yes! The framework can be adapted for any material composition data with similar features.

**Q: How accurate is the model?**
A: The XGBoost model achieves R² = 0.91 and RMSE = 4.81 MPa on the test set.

**Q: Can I deploy this to production?**
A: The MVP is production-ready for Streamlit Cloud deployment. See the MVP README for deployment instructions.

**Q: What languages are supported?**
A: The application includes multilingual interface support.

## Next Steps

Choose based on your interests:

**To Use the Application:**
```bash
cd webapp/mvp
bash run.sh
```

**To Explore ML Development:**
```bash
jupyter notebook notebooks/01_data_exploration.ipynb
```

**To Review Documentation:**
- Read [docs/PRD.md](docs/PRD.md) for product strategy
- Read [webapp/mvp/README_MVP.md](webapp/mvp/README_MVP.md) for technical details

**To Extend the Project:**
- Add new material types (steel, wood, masonry)
- Implement batch processing
- Build REST API
- Add user authentication

## Recommended Reading

**Machine Learning:**
- Hands-On Machine Learning (Aurélien Géron)
- Scikit-learn documentation
- XGBoost documentation

**Sustainability:**
- Ellen MacArthur Foundation - Circular Economy resources
- EU Circular Economy Action Plan
- Material Passports (BAMB project)
- EU Digital Product Passport initiative

**Product Management:**
- Inspired (Marty Cagan)
- The Lean Product Playbook (Dan Olsen)

---

## About This Project

This is a portfolio project demonstrating:
- **Technical Capability**: ML model development, deployment, and web application
- **Product Thinking**: User research, feature prioritization, and UX design
- **Impact Orientation**: Circular economy focus and sustainability metrics
- **Full-Stack Development**: Data science to production deployment

The project showcases end-to-end development from problem identification through MVP launch, including comprehensive documentation and user-centered design.
