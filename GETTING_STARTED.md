# Getting Started Guide
## Material Passport Generator - AI/ML Project

Welcome! This guide will help you get started with your Material Passport Generator project.

## 🎯 What You're Building

An AI-powered system that automatically generates digital material passports for building products, demonstrating:
- **Machine Learning**: Regression, classification, and deep learning
- **Sustainability**: Circular economy metrics and carbon footprint estimation
- **Product Management**: User-centered design and impact measurement

## 📋 Prerequisites

Before starting, ensure you have:
- **Python 3.9+** installed
- **Git** (optional, for version control)
- **4GB RAM minimum** (8GB recommended)
- **2GB free disk space**
- **Internet connection** (for dataset download)

## 🚀 Quick Start (5 Minutes)

### Step 1: Setup Environment

```bash
# Navigate to project directory
cd material-passport-generator

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Verify Python version
python --version  # Should be 3.9 or higher
```

### Step 2: Install Dependencies

```bash
# Install all required packages
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
python -c "import pandas; import sklearn; import torch; print('✓ All packages installed!')"
```

### Step 3: Download Dataset

```bash
# Run the dataset download script
python src/data/download_dataset.py
```

**Expected output:**
```
====================================
MATERIAL PASSPORT GENERATOR - Dataset Preparation
====================================

Downloading Concrete Compressive Strength dataset from UCI ML Repository...
✓ Dataset saved to data/raw/concrete_data.csv
✓ Metadata saved to data/raw/metadata.txt
Preparing dataset with sustainability features...
✓ Enriched dataset saved to data/processed/concrete_enriched.csv
✓ Summary statistics saved to data/processed/dataset_summary.txt

✓ Dataset preparation complete!
```

### Step 4: Explore the Data

```bash
# Launch Jupyter Notebook
jupyter notebook notebooks/01_data_exploration.ipynb
```

This will open your browser. Run all cells to explore the dataset!

## 📁 Project Structure Overview

```
material-passport-generator/
│
├── 📊 data/
│   ├── raw/                    # Original dataset
│   └── processed/              # Cleaned + enriched data
│
├── 📓 notebooks/                # Jupyter notebooks for exploration
│   ├── 01_data_exploration.ipynb
│   ├── 02_baseline_models.ipynb    (next step)
│   └── 03_deep_learning.ipynb      (coming soon)
│
├── 🔧 src/                     # Source code
│   ├── data/                   # Data processing scripts
│   ├── models/                 # ML model definitions
│   ├── features/               # Feature engineering
│   └── utils/                  # Helper functions
│
├── 📚 docs/                    # Documentation
│   └── PRD.md                  # Product requirements
│
├── 🌐 webapp/                  # Web application (Phase 2)
│   ├── backend/                # FastAPI
│   └── frontend/               # React
│
└── 📝 README.md                # Project overview
```

## 🧭 Learning Path

### Week 1-2: Foundation
**Goal:** Understand the data and build baseline models

1. ✅ **Data Exploration** (Notebook 01)
   - Load and inspect dataset
   - Understand sustainability metrics
   - Identify patterns and correlations

2. **Baseline Models** (Notebook 02 - next)
   - Linear Regression
   - Random Forest
   - XGBoost
   - Model evaluation and comparison

3. **Feature Engineering**
   - Create interaction features
   - Polynomial features
   - Domain-specific ratios

### Week 3-4: Deep Learning
**Goal:** Build neural networks and improve predictions

4. **Neural Network Models**
   - Feedforward neural network
   - Hyperparameter tuning
   - Multi-task learning (strength + recyclability)

5. **Model Optimization**
   - Cross-validation
   - Regularization
   - Ensemble methods

### Week 5-8: Advanced AI (Optional)
**Goal:** Add sophisticated AI capabilities

6. **Document AI**
   - Simulate technical data sheets
   - NLP for material extraction
   - Named Entity Recognition

7. **Knowledge Graph**
   - Material relationships
   - Property database
   - Recommendation system

### Week 9-12: Web Application
**Goal:** Deploy as a real product

8. **Backend Development**
   - FastAPI REST API
   - Model serving
   - Data validation

9. **Frontend Development**
   - React interface
   - Passport visualization
   - User experience

10. **Deployment & Documentation**
    - Cloud deployment
    - Portfolio presentation
    - Learning journal

## 📊 Dataset Overview

**Concrete Compressive Strength Dataset**
- **Source:** UCI Machine Learning Repository
- **Size:** 1,030 instances
- **Purpose:** Predict concrete strength from composition

**Features (Inputs):**
1. Cement (kg/m³)
2. Blast Furnace Slag (kg/m³) - *recycled material*
3. Fly Ash (kg/m³) - *recycled material*
4. Water (kg/m³)
5. Superplasticizer (kg/m³)
6. Coarse Aggregate (kg/m³)
7. Fine Aggregate (kg/m³)
8. Age (days)

**Target (Output):**
- Compressive Strength (MPa)

**Sustainability Metrics (Calculated):**
- Recycled Content %
- Circularity Score (0-100)
- CO2 Emissions Estimate
- Sustainability Grade

## 🎓 Key Learning Objectives

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

## 🛠️ Troubleshooting

### Issue: "ucimlrepo not found"
```bash
pip install ucimlrepo
```

### Issue: "Jupyter not found"
```bash
pip install jupyter
jupyter --version
```

### Issue: "ModuleNotFoundError"
Make sure virtual environment is activated:
```bash
# Check if (venv) appears in terminal
# If not, activate it:
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### Issue: "Permission denied"
On Mac/Linux, you might need:
```bash
chmod +x src/data/download_dataset.py
```

### Issue: Dataset download fails
If `ucimlrepo` doesn't work, download manually:
1. Go to: https://archive.ics.uci.edu/dataset/165/concrete+compressive+strength
2. Download the XLS file
3. Save to `data/raw/concrete_data.csv`
4. Run: `python src/data/download_dataset.py` (it will process the existing file)

## 📈 Success Metrics

Track your progress:

**Week 1-2:**
- [ ] Dataset downloaded and explored
- [ ] Baseline models trained (R² > 0.80)
- [ ] Sustainability metrics calculated
- [ ] First notebook completed

**Week 3-4:**
- [ ] Neural network implemented
- [ ] Model performance > baseline
- [ ] Feature engineering applied
- [ ] Second notebook completed

**Week 5-8:**
- [ ] Advanced AI features added
- [ ] Web prototype created
- [ ] API endpoints working

**Week 9-12:**
- [ ] Full application deployed
- [ ] Documentation complete
- [ ] Portfolio presentation ready

## 🤝 Getting Help

**Resources:**
- **Documentation:** Check `docs/` folder
- **Examples:** Look at completed notebook cells
- **Python Help:** Use `help(function_name)` in Python
- **Stack Overflow:** Search for specific errors

**Common Questions:**

**Q: How long should each phase take?**
A: 2-4 weeks per phase, but adjust based on your schedule.

**Q: Do I need GPU for this project?**
A: No, the dataset is small enough for CPU training.

**Q: Can I use my own data instead?**
A: Yes! The framework works with any material composition data.

**Q: What if I get stuck on ML concepts?**
A: Focus on understanding the workflow first, then dive deeper into theory.

## ✅ Next Steps

You're all set! Here's what to do next:

1. **Start Jupyter**
   ```bash
   jupyter notebook notebooks/01_data_exploration.ipynb
   ```

2. **Run all cells** in the exploration notebook

3. **Read the insights** and understand the data

4. **Move to Notebook 02** for baseline ML models

5. **Document your learning** in `docs/learning_journal.md`

## 📚 Recommended Reading

**Machine Learning:**
- Hands-On Machine Learning (Aurélien Géron)
- Scikit-learn documentation

**Sustainability:**
- Ellen MacArthur Foundation resources
- EU Circular Economy Action Plan
- Material Passports (BAMB project)

**Product Management:**
- Inspired (Marty Cagan)
- The Lean Product Playbook (Dan Olsen)

---

**Happy Learning! 🎉**

Remember: This is a portfolio project. Focus on demonstrating:
- Technical capability
- Product thinking
- Impact orientation

Take notes, document challenges, and showcase your problem-solving process!

---

**Questions or issues?** Create documentation of your solutions - they make great interview stories!
