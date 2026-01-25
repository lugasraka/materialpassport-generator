# Material Passport Generator - AI/ML Project

**Tagline:** Enabling Circular Economy Through AI-Powered Material Intelligence

## Project Vision

An AI-driven web application that automatically generates digital material passports for building products, enabling transparency in material composition and facilitating circular economy practices in the construction industry.

## Why This Matters

The construction industry generates 1.3 billion tons of waste annually. Digital Material Passports are becoming mandatory in the EU (Digital Product Passport initiative) to enable circular economy. This project demonstrates how AI/ML can automate the creation of these critical documents.

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

## AI/ML Components

### Phase 1: Foundation (Weeks 1-4)
- [x] Data acquisition and exploration
- [ ] Baseline regression models (Linear, Random Forest, XGBoost)
- [ ] Feature engineering for recyclability scoring
- [ ] Sustainability metrics calculation

### Phase 2: Deep Learning (Weeks 5-8)
- [ ] Neural network for strength prediction
- [ ] Multi-task learning (strength + recyclability)
- [ ] Compositional optimization using RL
- [ ] Transfer learning preparation

### Phase 3: Advanced AI (Weeks 9-12)
- [ ] Document AI simulation (generate synthetic datasheets)
- [ ] NER model for material extraction
- [ ] Knowledge graph construction
- [ ] Recommendation engine for sustainable alternatives

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
│   ├── raw/              # Original datasets
│   ├── processed/        # Cleaned and transformed data
│   └── synthetic/        # Generated training data
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_baseline_models.ipynb
│   ├── 03_deep_learning.ipynb
│   └── 04_sustainability_scoring.ipynb
├── src/
│   ├── data/             # Data loading and preprocessing
│   ├── models/           # ML model definitions
│   ├── features/         # Feature engineering
│   └── utils/            # Helper functions
├── models/               # Saved trained models
├── docs/
│   ├── PRD.md           # Product Requirements Document
│   ├── technical_spec.md
│   └── learning_journal.md
├── webapp/
│   ├── backend/         # FastAPI application
│   └── frontend/        # React application
├── tests/
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.9+
- pip or conda
- Git

### Installation

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

## Key Metrics & Success Criteria

### Technical Metrics:
- **Strength Prediction:** R² > 0.85, RMSE < 5 MPa
- **Recyclability Scoring:** Accuracy > 80%
- **Model Inference:** < 100ms per passport

### Impact Metrics:
- **Material Reuse Potential:** Calculate % recycled content
- **Carbon Footprint:** Estimate CO₂ based on composition
- **Circularity Score:** 0-100 scale based on recyclability

### Product Metrics:
- **Time Saved:** 90% reduction in manual passport creation
- **Adoption:** Target 100 synthetic passports generated
- **Accuracy:** 95% composition extraction accuracy

## Use Cases

1. **Manufacturer:** Auto-generate material passports for product catalog
2. **Architect:** Evaluate material sustainability during design phase
3. **Recycler:** Assess recyclability of demolition materials
4. **Regulator:** Verify compliance with circular economy regulations

## Documentation Strategy

### Product Management Artifacts:
1. **Product Requirements Document (PRD)**
   - Problem statement and market analysis
   - User personas and jobs-to-be-done
   - Feature prioritization (MoSCoW)
   - Success metrics and KPIs

2. **Technical Roadmap**
   - Architecture decisions and rationale
   - Technology stack justification
   - Scalability considerations
   - Technical debt management

3. **Learning Journal**
   - Weekly reflections on AI/ML concepts
   - Challenges and solutions
   - Key insights and breakthroughs
   - Resources and references

4. **Impact Assessment**
   - Environmental impact calculations
   - Stakeholder interview insights
   - Partnership opportunities
   - Business model exploration

## Alignment with Google DeepMind Impact Roles

This project demonstrates key competencies for the Portfolio Lead positions:

- **Real-world AI Application:** Solving circular economy challenges
- **Program Management:** Multi-phase execution with clear milestones
- **Stakeholder Engagement:** Understanding manufacturer, architect, recycler needs
- **Impact Measurement:** Quantifying sustainability outcomes
- **Technical Bridge:** Translating ML capabilities to domain solutions
- **Innovation:** Novel approach to automating material passports

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

**[Your Name]**
- Sustainability Program Manager @ Siemens
- Passionate about AI/ML for Climate Impact
- Preparing for Portfolio Lead roles in AI for Sustainability

---

Built with passion for sustainable construction and circular economy
