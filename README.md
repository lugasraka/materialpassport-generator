# Material Passport Generator - AI/ML Project

Enabling Circular Economy Through AI-Powered Material Intelligence

## Project Status: MVP Launched

A fully functional web application that uses AI/ML to automatically generate digital material passports for concrete products, complete with sustainability metrics and PDF export capabilities.

**Live MVP:** Streamlit web application with XGBoost-powered predictions and multilingual support

## Project Vision

An AI-driven web application that automatically generates digital material passports for building products, enabling transparency in material composition and facilitating circular economy practices in the construction industry.

## Why This Matters

The construction industry generates 1.3 billion tons of waste annually. Digital Material Passports are becoming mandatory in the EU (Digital Product Passport initiative) to enable circular economy. This project demonstrates how AI/ML can automate the creation of these critical documents, reducing manual effort by ~90% (from 5+ hours to minutes).

## Current Features (MVP - V1)

### Core Capabilities
- **AI-Powered Predictions:** XGBoost model (R² = 0.91, RMSE = 4.81 MPa) predicts concrete compressive strength
- **Sustainability Metrics:** Automatic calculation of recycled content, circularity score (0-100), and CO₂ emissions
- **Digital Passport Generation:** Professional passport display with grades A-E based on sustainability
- **PDF Export:** Download complete material passports as formatted PDF documents
- **Interactive Web UI:** Streamlit-based interface with real-time predictions
- **Multilingual Support:** Interface available in multiple languages
- **Compliance Ready:** EU Digital Product Passport and EN 206 standards alignment
- **User Education:** Built-in tooltips and explanations for all metrics
- **Feedback System:** User ratings and feature requests collection

### Performance
- Generate material passports in under 2 minutes (vs 5+ hours manual)
- Support for 8 concrete composition parameters
- Real-time sustainability grade calculation
- Benchmark against industry averages

## Dataset

**Primary Dataset:** Concrete Compressive Strength (UCI ML Repository)
- **Source:** https://archive.ics.uci.edu/dataset/165/concrete+compressive+strength
- **Size:** 1,030 instances
- **Features:** 8 quantitative inputs + 1 output
- **License:** Creative Commons Attribution 4.0 (CC BY 4.0)

### Dataset Features:
1. **Cement** (kg/m³) - Primary binding material
2. **Blast Furnace Slag** (kg/m³) - Industrial waste byproduct (circular economy)
3. **Fly Ash** (kg/m³) - Coal combustion byproduct (waste reuse)
4. **Water** (kg/m³) - Hydration agent
5. **Superplasticizer** (kg/m³) - Chemical additive
6. **Coarse Aggregate** (kg/m³) - Large particles
7. **Fine Aggregate** (kg/m³) - Small particles
8. **Age** (days) - Curing time
9. **Compressive Strength** (MPa) - Target variable

## AI/ML Development Progress

### Phase 1: Foundation (Complete)
- Data acquisition and exploration
- Baseline regression models (Linear, Random Forest, XGBoost)
- Feature engineering for recyclability scoring
- Sustainability metrics calculation
- Model Performance: XGBoost R² = 0.91, RMSE = 4.81 MPa

### Phase 2: Deep Learning (Complete)
- Neural network for strength prediction
- Multi-task learning (strength + recyclability)
- Model comparison and selection
- Production model deployment (XGBoost selected)

### Phase 3: Web Application (MVP Complete)
- Streamlit web application
- Interactive UI with real-time predictions
- Sustainability metrics dashboard
- PDF export functionality
- User feedback collection system
- Multilingual interface support
- Three-tab interface (Generator, About AI/ML, About Developer)

### Phase 4: Future Enhancements (Roadmap)
- Multiple material types (steel, wood, masonry)
- Batch processing for multiple compositions
- Historical data tracking and comparison
- API development for integration
- Advanced visualization and analytics
- Environmental condition factors
- Confidence intervals for predictions

## Learning Objectives

As a sustainability program manager transitioning to AI/ML for impact, this project demonstrates:

1. **Technical Skills:**
   - Python ML ecosystem (pandas, scikit-learn, PyTorch)
   - Regression, classification, and deep learning
   - Feature engineering and model selection
   - MLOps basics (experiment tracking, model versioning)

2. **Product Management:**
   - User research and persona development
   - Metric definition and success criteria
   - Stakeholder mapping and partnership strategy
   - Go-to-market planning

3. **Domain Expertise:**
   - Building materials sustainability
   - Circular economy principles
   - Regulatory landscape (EU DPP)
   - Life cycle assessment (LCA)

## Project Structure

```
material-passport-generator/
├── data/
│   ├── raw/                          # Original datasets
│   │   ├── concrete_data.csv         # Concrete composition data (UCI dataset)
│   │   └── metadata.txt              # Dataset documentation
│   └── processed/                    # Cleaned and transformed data
│       ├── concrete_enriched.csv     # Enriched dataset with sustainability metrics
│       ├── dataset_summary.txt       # Statistical summary
│       └── exploration_summary.csv   # Exploratory analysis results
├── notebooks/                        # Jupyter notebooks for analysis
│   ├── 01_data_exploration.ipynb     # Data exploration and visualization
│   ├── 02_baseline_models.ipynb      # Baseline ML models (Linear, RF, XGBoost)
│   └── 03_deep_learning.ipynb        # Neural networks and deep learning
├── src/
│   ├── data/                         # Data loading and preprocessing
│   │   ├── __init__.py
│   │   └── download_dataset.py       # Dataset download and enrichment script
│   ├── features/                     # Feature engineering
│   │   ├── __init__.py
│   │   └── feature_engineering.py    # Feature creation and transformation
│   └── __init__.py
├── models/                           # Saved trained models
│   ├── linear_regression.pkl         # Linear regression model
│   ├── random_forest.pkl             # Random forest model
│   ├── xgboost.pkl                   # XGBoost model (PRODUCTION)
│   ├── simple_nn.pth                 # Simple neural network
│   ├── deep_nn.pth                   # Deep neural network
│   ├── multitask_nn.pth              # Multi-task neural network
│   ├── scaler.pkl                    # Feature scaler (PRODUCTION)
│   ├── scaler_X.pkl                  # Input features scaler
│   ├── scaler_y_str.pkl              # Strength target scaler
│   └── scaler_y_circ.pkl             # Circularity target scaler
├── webapp/                           # Web application
│   └── mvp/                          # MVP Streamlit application
│       ├── app.py                    # Main application
│       ├── requirements_mvp.txt      # Dependencies
│       ├── run.sh                    # Launch script
│       ├── README_MVP.md             # MVP documentation
│       └── .streamlit/
│           └── config.toml           # Streamlit configuration
├── docs/
│   └── PRD.md                        # Product Requirements Document
├── requirements.txt                  # Python dependencies (ML development)
├── README.md                         # Project documentation (this file)
├── GETTING_STARTED.md                # Setup and installation guide
└── START_HERE.md                     # Quick start guide
```

## Getting Started

### Quick Start - Run the MVP Web App

**Option 1: Using the launch script (Recommended)**
```bash
cd webapp/mvp
bash run.sh
```

**Option 2: Manual setup**
```bash
cd webapp/mvp

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements_mvp.txt

# Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`

### ML Development Setup

For working with the underlying ML models and notebooks:

```bash
# Clone repository (or download project)
cd material-passport-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download dataset
python src/data/download_dataset.py

# Run initial exploration
jupyter notebook notebooks/01_data_exploration.ipynb
```

### Prerequisites
- Python 3.9+
- pip or conda
- Git

## Key Metrics & Success Criteria

### Technical Metrics (Achieved):
- **Strength Prediction:** R² = 0.91 (Target: > 0.85)
- **RMSE:** 4.81 MPa (Target: < 5 MPa)
- **Model Inference:** < 100ms per passport

### Impact Metrics (Implemented):
- **Material Reuse Potential:** Calculate percentage of recycled content
- **Carbon Footprint:** Estimate CO₂ based on composition
- **Circularity Score:** 0-100 scale based on recyclability
- **Sustainability Grading:** A-E grade system

### Product Metrics (MVP Goals):
- **Time Saved:** 90% reduction in manual passport creation (5 hours to under 2 minutes)
- **User Adoption:** Target 20+ unique users in Week 1
- **Completion Rate:** Target >60% of users generate full passport
- **User Satisfaction:** Target >3.5/5 rating
- **Feature Requests:** Collect feedback for V2 roadmap

## Use Cases & Target Users

### Primary Users (Fully Supported in MVP)

**1. Manufacturers (Sustainability Managers)**
- Auto-generate EU-compliant Digital Product Passports
- Save 5+ hours per product vs manual calculation
- Ensure EN 206 standards compliance

**2. Consultants (Circular Economy Specialists)**
- Rapid material analysis and circularity scoring
- Benchmark compositions against industry averages
- Generate professional reports for clients

**3. Architects/Designers**
- Evaluate material sustainability during design phase
- Compare different concrete compositions
- Support green building certification (LEED, BREEAM)

### Future Use Cases (Roadmap)
- **Recyclers:** Assess recyclability of demolition materials
- **Regulators:** Verify compliance with circular economy regulations
- **Researchers:** Analyze material composition trends

## Technology Stack

### Frontend
- **Streamlit**: Interactive web application framework
- **Pandas/NumPy**: Data manipulation and display
- **Matplotlib/Seaborn**: Visualizations (future enhancements)

### Backend & ML
- **XGBoost**: Production ML model (R² = 0.91)
- **Scikit-learn**: Feature scaling and preprocessing
- **PyTorch**: Deep learning experiments (archived)

### PDF Generation
- **ReportLab**: Professional PDF document creation

### Deployment (Future)
- **Streamlit Cloud**: Cloud hosting
- **Docker**: Containerization
- **GitHub Actions**: CI/CD pipeline

## Documentation & Learning Resources

For detailed information about the project:
- **[webapp/mvp/README_MVP.md](webapp/mvp/README_MVP.md)** - Complete MVP documentation, features, and deployment guide
- **[docs/PRD.md](docs/PRD.md)** - Product Requirements Document with user research and feature prioritization
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Detailed setup instructions
- **Notebooks**: See `notebooks/` for ML development process and model comparisons

## Documentation Strategy

### Product Management Artifacts

**1. Product Requirements Document (PRD)**
- Problem statement and market analysis
- User personas and jobs-to-be-done
- Feature prioritization (MoSCoW)
- Success metrics and KPIs

**2. MVP Documentation**
- Complete feature documentation
- User guides and tutorials
- Deployment instructions
- Feedback collection plan

**3. Technical Documentation**
- Model performance metrics
- Architecture decisions
- API documentation (future)
- Code documentation in notebooks

## Development Roadmap

### Immediate Priorities
- Deploy MVP to Streamlit Cloud
- Collect user feedback from 20+ testers
- Analyze usage patterns and completion rates
- Document feature requests for V2

### Short-term Enhancements
- Implement most-requested features
- Add batch processing capabilities
- Improve PDF export with custom branding
- Add data export (CSV, JSON)

### Medium-term Goals
- Expand to additional material types (steel, wood)
- Build REST API for integrations
- Add user authentication and saved passports
- Develop mobile-responsive design

### Long-term Vision
- Integration with BIM software
- Machine learning model improvements with user data
- Enterprise features and SaaS model

## References & Citations

**Dataset:**
- Yeh, I-C. (1998). "Modeling of strength of high-performance concrete using artificial neural networks." *Cement and Concrete Research*, 28(12), 1797-1808.

**Circular Economy:**
- Ellen MacArthur Foundation. (2019). "Completing the Picture: How the Circular Economy Tackles Climate Change"

**Digital Product Passports:**
- European Commission. (2022). "Proposal for Ecodesign for Sustainable Products Regulation"

## License

This project is for educational and portfolio purposes. Dataset used under CC BY 4.0 license.

## Author

**Raka Adrianto** [LinkedIn](https://www.linkedin.com/in/lugasraka/)
- Sustainability Program Manager @ Siemens
- Passionate about AI/ML for Climate Impact
- Preparing for Portfolio Lead roles in AI for Sustainability
