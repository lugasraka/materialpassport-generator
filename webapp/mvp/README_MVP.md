# Material Passport Generator - MVP Documentation

## Overview

The Material Passport Generator MVP is a production-ready web application that uses AI/ML to automatically generate digital material passports for concrete products. Built with Streamlit, it provides an intuitive interface for entering concrete compositions and receiving comprehensive sustainability assessments backed by machine learning predictions.

**Live Application**: Streamlit-based web interface with XGBoost-powered predictions

## Key Features

### Core Functionality
- **AI-Powered Predictions**: XGBoost regression model (R² = 0.91, RMSE = 4.81 MPa) predicts concrete compressive strength from composition inputs
- **Sustainability Metrics**: Automatic calculation of recycled content percentage, circularity score (0-100), and CO₂ emissions estimates
- **Digital Passport Generation**: Professional passport display with sustainability grades (A-E) based on circularity performance
- **PDF Export**: Download complete material passports as formatted PDF documents with all metrics and assessments
- **Multilingual Support**: Interface available in multiple languages for international accessibility

### User Experience
- **Interactive Input Forms**: Clear, validated input fields for 8 concrete composition parameters
- **Real-Time Predictions**: Instant calculation and display of strength predictions and sustainability metrics
- **Industry Benchmarking**: Compare compositions against industry averages
- **Educational Tooltips**: Built-in explanations for all metrics and sustainability concepts
- **Feedback System**: Integrated user rating and feature request collection

### Compliance & Standards
- **EU Digital Product Passport**: Aligned with EU DPP initiative requirements
- **EN 206 Standards**: Compliant with European concrete standards
- **Transparent Methodology**: Clear documentation of calculation methods and model performance

## Technical Architecture

### Technology Stack

**Frontend & Application**
- **Streamlit 1.29.0**: Web application framework
- **Python 3.9+**: Core programming language

**Machine Learning**
- **XGBoost 2.0.3**: Production ML model for strength prediction
- **Scikit-learn 1.3.2**: Feature scaling and preprocessing
- **Joblib**: Model serialization and loading

**Data Processing**
- **Pandas 2.1.4**: Data manipulation and calculations
- **NumPy 1.26.2**: Numerical computations

**PDF Generation**
- **ReportLab 4.0.9**: Professional PDF document creation

### Model Performance

**Production Model: XGBoost Regressor**
- **R² Score**: 0.91 (explains 91% of variance in concrete strength)
- **RMSE**: 4.81 MPa (mean absolute error in strength predictions)
- **Training Data**: 1,030 instances from UCI ML Repository
- **Features**: 8 quantitative inputs (cement, slag, fly ash, water, superplasticizer, coarse aggregate, fine aggregate, age)
- **Inference Time**: <100ms per prediction

**Model Selection Rationale**
- Outperformed Linear Regression (R² = 0.61) and Random Forest (R² = 0.88)
- Better performance than neural network alternatives for this dataset size
- Faster inference and easier interpretability
- Robust to outliers and handles non-linear relationships

### Application Structure

```
webapp/mvp/
├── app.py                      # Main Streamlit application
├── requirements_mvp.txt        # Python dependencies
├── run.sh                      # Launch script (auto-setup)
├── README_MVP.md               # This documentation
├── QUICKSTART.md               # Quick reference guide
└── .streamlit/
    └── config.toml             # Streamlit configuration
```

### Key Components

**1. Input Validation**
- Range validation for all composition parameters
- Physical constraints enforcement (e.g., minimum cement content)
- User-friendly error messages

**2. Prediction Engine**
- Loads pre-trained XGBoost model and scaler
- Standardizes input features using fitted scaler
- Returns strength prediction with model confidence

**3. Sustainability Calculator**
- Recycled content: Percentage of slag and fly ash in mix
- Circularity score: Weighted formula based on recycled content, water efficiency, and age
- CO₂ emissions: Estimated from cement content (industry standard: 0.9 kg CO₂ per kg cement)
- Sustainability grade: A-E scale based on circularity score thresholds

**4. PDF Generator**
- Professional document layout using ReportLab
- Includes all input parameters, predictions, and sustainability metrics
- Formatted tables and clear section headers
- Timestamp and version information

## Installation & Setup

### Quick Start (Recommended)

```bash
cd webapp/mvp
bash run.sh
```

The script automatically:
1. Creates a Python virtual environment
2. Installs all dependencies
3. Launches the application
4. Opens in your default browser at `http://localhost:8501`

### Manual Setup

```bash
cd webapp/mvp

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Mac/Linux
# OR
venv\Scripts\activate     # On Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements_mvp.txt

# Run application
streamlit run app.py
```

### System Requirements

**Minimum Requirements**
- Python 3.9 or higher
- 2GB RAM
- 500MB free disk space
- Internet connection (initial setup only)

**Recommended**
- Python 3.10+
- 4GB RAM
- Modern web browser (Chrome, Firefox, Safari, Edge)

## Usage Guide

### Generating a Material Passport

1. **Navigate to the Generator Tab**
   - Default landing page of the application

2. **Enter Concrete Composition**
   - **Cement** (kg/m³): Primary binding material (102-540 range)
   - **Blast Furnace Slag** (kg/m³): Industrial waste byproduct (0-359 range)
   - **Fly Ash** (kg/m³): Coal combustion byproduct (0-200 range)
   - **Water** (kg/m³): Hydration agent (121-247 range)
   - **Superplasticizer** (kg/m³): Chemical additive (0-32 range)
   - **Coarse Aggregate** (kg/m³): Large particles (801-1145 range)
   - **Fine Aggregate** (kg/m³): Small particles (594-992 range)
   - **Age** (days): Curing time (1-365 range)

3. **Generate Passport**
   - Click the "Generate Material Passport" button
   - View real-time AI predictions and sustainability metrics

4. **Review Results**
   - **Predicted Compressive Strength**: MPa value with model accuracy (R²)
   - **Recycled Content**: Percentage of recycled materials
   - **Circularity Score**: 0-100 scale assessment
   - **CO₂ Emissions**: Estimated carbon footprint
   - **Sustainability Grade**: A-E rating
   - **Interpretation**: Contextual explanation of results

5. **Export PDF**
   - Click "Download Material Passport (PDF)"
   - Save professional document for records/compliance

### Understanding the Metrics

**Compressive Strength (MPa)**
- Measures concrete's ability to withstand loads
- Predicted using AI/ML model trained on 1,030 real-world samples
- Critical for structural engineering applications

**Recycled Content (%)**
- Percentage of slag and fly ash in total mix
- Higher percentages indicate better circular economy practices
- Industry benchmark: 20-30% is good, >40% is excellent

**Circularity Score (0-100)**
- Composite metric evaluating overall sustainability
- Considers recycled content, water efficiency, and curing time
- Scores: 80-100 (A), 60-79 (B), 40-59 (C), 20-39 (D), 0-19 (E)

**CO₂ Emissions (kg CO₂/m³)**
- Estimated based on cement content
- Uses industry standard: 0.9 kg CO₂ per kg cement
- Lower values indicate reduced carbon footprint

**Sustainability Grade (A-E)**
- Simple letter grade for quick assessment
- Based on circularity score thresholds
- Aligned with EU environmental rating standards

### Example Use Cases

**Case 1: High-Performance Concrete**
```
Cement: 400 kg/m³
Slag: 100 kg/m³
Fly Ash: 0 kg/m³
Water: 180 kg/m³
Superplasticizer: 8 kg/m³
Coarse Aggregate: 1000 kg/m³
Fine Aggregate: 750 kg/m³
Age: 28 days
```
Result: High strength (~40 MPa), moderate recycled content (~20%)

**Case 2: Eco-Friendly Concrete**
```
Cement: 250 kg/m³
Slag: 150 kg/m³
Fly Ash: 100 kg/m³
Water: 160 kg/m³
Superplasticizer: 5 kg/m³
Coarse Aggregate: 950 kg/m³
Fine Aggregate: 700 kg/m³
Age: 56 days
```
Result: Adequate strength (~35 MPa), high recycled content (50%), excellent sustainability grade

## Deployment

### Local Development
Already configured - see Installation & Setup section above.

### Streamlit Cloud Deployment

**Prerequisites**
- GitHub repository with code
- Streamlit Cloud account (free tier available)

**Steps**
1. Push code to GitHub repository
2. Log in to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select repository, branch, and file path (`webapp/mvp/app.py`)
5. Click "Deploy"

**Configuration**
- Streamlit will automatically detect `requirements_mvp.txt`
- Ensure model files are committed to repository (in `models/` directory)
- Set Python version to 3.9+ in advanced settings if needed

### Docker Deployment (Optional)

Create `Dockerfile` in `webapp/mvp/`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements_mvp.txt .
RUN pip install --no-cache-dir -r requirements_mvp.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t material-passport-mvp .
docker run -p 8501:8501 material-passport-mvp
```

## Troubleshooting

### Application Won't Start

**Issue**: Module not found errors
**Solution**:
```bash
pip install --upgrade pip
pip install -r requirements_mvp.txt
```

**Issue**: Port already in use
**Solution**:
```bash
streamlit run app.py --server.port 8502
```

### Model Loading Errors

**Issue**: "Model file not found"
**Solution**: Ensure you're running from `webapp/mvp/` directory. Model paths are relative (`../../models/`)

**Issue**: "Scaler file not found"
**Solution**: Verify both `xgboost.pkl` and `scaler.pkl` exist in `models/` directory

### PDF Export Issues

**Issue**: PDF generation fails
**Solution**:
```bash
pip install reportlab
```

**Issue**: PDF fonts not rendering correctly
**Solution**: ReportLab uses default fonts. This is expected behavior on some systems.

### Performance Issues

**Issue**: Slow predictions
**Solution**: Ensure you have adequate RAM (4GB+). XGBoost models are memory-intensive but should predict in <100ms.

**Issue**: Application lag
**Solution**: Close other browser tabs. Streamlit applications are client-side heavy.

## Known Limitations

### Current Version (V1 MVP)

**Material Types**
- Only supports concrete compositions
- Does not support steel, wood, masonry, or other building materials

**Processing**
- Single composition only (no batch processing)
- No historical data tracking or comparison features

**Model Constraints**
- Predictions valid only within training data ranges
- Extrapolation beyond input ranges may be unreliable
- Model trained on standard concrete mixes (may not generalize to specialty concretes)

**Data Persistence**
- No user authentication or accounts
- No saved passports or history
- All data session-based only

**Sustainability Calculations**
- CO₂ estimates are simplified (based on cement content only)
- Does not include transportation, production energy, or end-of-life impacts
- Circularity score is a proprietary metric, not an industry standard

**Accessibility**
- Limited screen reader support
- No keyboard-only navigation optimization

## Future Enhancements

### Short-Term (V2)
- Batch processing for multiple compositions
- Historical data tracking and comparison charts
- Enhanced PDF export with custom branding
- Data export (CSV, JSON formats)
- Improved mobile responsive design

### Medium-Term (V3)
- Additional material types (steel, wood, masonry)
- User authentication and saved passports
- REST API for third-party integrations
- Advanced visualization and analytics dashboard
- Confidence intervals for predictions

### Long-Term (V4+)
- Integration with BIM software (Revit, ArchiCAD)
- Life cycle assessment (LCA) with full environmental impacts
- Machine learning model improvements using user-contributed data
- Multi-region support with localized standards
- Enterprise features (team collaboration, audit trails)

## Performance Metrics

### Technical Metrics (Achieved)
- **Model R² Score**: 0.91 (target: >0.85)
- **RMSE**: 4.81 MPa (target: <5 MPa)
- **Inference Time**: <100ms per passport (target: <200ms)
- **Application Load Time**: <3 seconds (target: <5 seconds)

### Impact Metrics
- **Time Savings**: 90% reduction in manual passport creation (5+ hours to <2 minutes)
- **Process Efficiency**: Automated calculations eliminate manual errors
- **Accessibility**: Web-based interface requires no specialized software

### Target Product Metrics
- **User Adoption**: 20+ unique users in Week 1 (deployment dependent)
- **Completion Rate**: >60% of users generate full passport
- **User Satisfaction**: >3.5/5 rating
- **Feature Requests**: Collect feedback for V2 roadmap

## Contributing & Feedback

This is a portfolio project demonstrating end-to-end ML product development. Feedback is welcome:

**User Feedback**
- Use the built-in feedback form in the application
- Rate your experience (1-5 stars)
- Suggest features for future versions

**Technical Feedback**
- Report issues or bugs via GitHub Issues
- Propose enhancements via pull requests
- Review code in `app.py` for implementation details

## References & Standards

**Dataset**
- Yeh, I-C. (1998). "Modeling of strength of high-performance concrete using artificial neural networks." *Cement and Concrete Research*, 28(12), 1797-1808.
- UCI Machine Learning Repository: Concrete Compressive Strength Dataset

**Standards & Regulations**
- European Commission. (2022). "Proposal for Ecodesign for Sustainable Products Regulation"
- EN 206: Concrete - Specification, performance, production and conformity
- ISO 14001: Environmental management systems

**Circular Economy**
- Ellen MacArthur Foundation. (2019). "Completing the Picture: How the Circular Economy Tackles Climate Change"
- EU Circular Economy Action Plan (2020)

## License & Usage

This project is for educational and portfolio purposes.

**Dataset License**: Creative Commons Attribution 4.0 (CC BY 4.0)

**Code**: Available for review and learning. Contact for commercial use inquiries.

## Contact

**Raka Adrianto**
- LinkedIn: [linkedin.com/in/lugasraka](https://www.linkedin.com/in/lugasraka/)
- Role: Sustainability Program Manager @ Siemens
- Focus: AI/ML for Climate Impact

---

**Last Updated**: January 2026
**Version**: 1.0 (MVP)
**Status**: Production Ready
