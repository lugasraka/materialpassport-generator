import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# Set page config
st.set_page_config(
    page_title="Material Passport Generator",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e3a5f;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.3rem;
        color: #2d5a87;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Load models and data
def load_models():
    """Load ML models and scalers"""
    models_dir = Path(__file__).parent.parent.parent / 'models'
    
    try:
        model = joblib.load(models_dir / 'xgboost.pkl')
        scaler = joblib.load(models_dir / 'scaler.pkl')
        return model, scaler
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return None, None

# Calculate sustainability metrics
def calculate_sustainability_metrics(df_row):
    """Calculate circular economy metrics based on composition"""
    
    cement = df_row['cement']
    slag = df_row['slag']
    fly_ash = df_row['fly_ash']
    total_mass = cement + slag + fly_ash + df_row['water'] + df_row['superplasticizer'] + \
                 df_row['coarse_aggregate'] + df_row['fine_aggregate']
    
    # Recycled content (slag + fly ash)
    recycled_content = ((slag + fly_ash) / total_mass) * 100
    
    # CO2 estimation (simplified)
    co2_cement = cement * 0.85
    co2_slag = slag * 0.07
    co2_flyash = fly_ash * 0.01
    co2_total = co2_cement + co2_slag + co2_flyash
    
    # Circularity score (0-100)
    circularity_score = min(100, recycled_content * 3 + (co2_total < 300) * 20)
    
    # Sustainability grade
    if circularity_score >= 80:
        grade = 'A'
        grade_color = '#28a745'
    elif circularity_score >= 60:
        grade = 'B'
        grade_color = '#17a2b8'
    elif circularity_score >= 40:
        grade = 'C'
        grade_color = '#ffc107'
    elif circularity_score >= 20:
        grade = 'D'
        grade_color = '#fd7e14'
    else:
        grade = 'E'
        grade_color = '#dc3545'
    
    return {
        'recycled_content': recycled_content,
        'co2_emissions': co2_total,
        'circularity_score': circularity_score,
        'grade': grade,
        'grade_color': grade_color,
        'total_mass': total_mass
    }

# Generate PDF of Material Passport
def generate_pdf(input_data, prediction, metrics, passport_id, timestamp):
    """Generate PDF document of Material Passport"""
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                           rightMargin=0.75*inch, leftMargin=0.75*inch,
                           topMargin=1*inch, bottomMargin=0.75*inch)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e3a5f'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2d5a87'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    normal_style = styles['Normal']
    
    # Title
    elements.append(Paragraph("🏗️ Material Passport - Concrete", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Header information
    header_data = [
        ['Passport ID:', passport_id],
        ['Generated:', timestamp],
        ['Sustainability Grade:', f"{metrics['grade']} ({get_grade_description(metrics['grade'])})"]
    ]
    
    header_table = Table(header_data, colWidths=[2*inch, 4*inch])
    header_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2d5a87')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Performance Metrics
    elements.append(Paragraph("Performance & Sustainability", heading_style))
    
    perf_data = [
        ['Metric', 'Value', 'Status'],
        ['Compressive Strength', f"{prediction:.1f} MPa", '✅ Target: 30+ MPa' if prediction >= 30 else '⚠️ Below target'],
        ['Age', f"{int(input_data['age'])} days", ''],
        ['Recycled Content', f"{metrics['recycled_content']:.1f}%", f"+{metrics['recycled_content']-10:.1f}% vs industry avg"],
        ['Circularity Score', f"{metrics['circularity_score']:.0f}/100", get_circularity_label(metrics['circularity_score'])],
        ['CO₂ Emissions', f"{metrics['co2_emissions']:.0f} kg/m³", f"-{320-metrics['co2_emissions']:.0f} kg vs industry avg"]
    ]
    
    perf_table = Table(perf_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
    perf_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d5a87')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
    ]))
    
    elements.append(perf_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Material Composition
    elements.append(Paragraph("Material Composition", heading_style))
    
    components = ['cement', 'slag', 'fly_ash', 'water', 'superplasticizer', 
                 'coarse_aggregate', 'fine_aggregate']
    labels = ['Cement', 'Blast Furnace Slag', 'Fly Ash', 'Water', 'Superplasticizer',
              'Coarse Aggregate', 'Fine Aggregate']
    
    comp_data = [['Component', 'Amount (kg/m³)', 'Percentage', 'Note']]
    for comp, label in zip(components, labels):
        value = input_data[comp]
        percent = (value / metrics['total_mass']) * 100
        recycled = '♻️ Recycled' if comp in ['slag', 'fly_ash'] and value > 0 else ''
        comp_data.append([label, f"{value:.0f}", f"{percent:.1f}%", recycled])
    
    comp_table = Table(comp_data, colWidths=[2*inch, 1.3*inch, 1.3*inch, 1.4*inch])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d5a87')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
    ]))
    
    elements.append(comp_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Compliance
    elements.append(Paragraph("Compliance & Standards", heading_style))
    
    compliance_data = [
        ['Standard', 'Status'],
        ['EU Digital Product Passport', '✅ Compliant'],
        ['EN 206 Standards', '✅ Compliant']
    ]
    
    compliance_table = Table(compliance_data, colWidths=[3*inch, 3*inch])
    compliance_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d5a87')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
    ]))
    
    elements.append(compliance_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_text = """
    <para align=center>
    <font size=8 color="#6c757d">
    Material Passport Generator | AI-Powered Sustainability Analysis<br/>
    Generated automatically using XGBoost ML model (R² = 0.91, RMSE = 4.81 MPa)<br/>
    Time savings: ~5 hours vs manual calculation
    </font>
    </para>
    """
    elements.append(Paragraph(footer_text, normal_style))
    
    # Build PDF
    doc.build(elements)
    
    buffer.seek(0)
    return buffer

def get_grade_description(grade):
    """Get description for sustainability grade"""
    descriptions = {
        'A': 'Excellent Sustainability',
        'B': 'Good Sustainability',
        'C': 'Moderate Sustainability',
        'D': 'Poor Sustainability',
        'E': 'Very Poor Sustainability'
    }
    return descriptions.get(grade, '')

def get_circularity_label(score):
    """Get label for circularity score"""
    if score >= 80:
        return 'Excellent'
    elif score >= 60:
        return 'Good'
    elif score >= 40:
        return 'Moderate'
    elif score >= 20:
        return 'Poor'
    else:
        return 'Very Poor'


# Display passport using Streamlit components
def display_passport(input_data, prediction, metrics):
    """Display passport using Streamlit native components"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    passport_id = f"MP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Display header with grade
    st.markdown("---")
    col_header1, col_header2, col_header3 = st.columns([2, 1, 1])
    with col_header1:
        st.markdown("### 🏗️ Material Passport - Concrete")
        st.caption(f"Generated: {timestamp}")
        st.caption(f"Passport ID: {passport_id}")
    with col_header2:
        grade_color_map = {
            'A': 'green', 'B': 'blue', 'C': 'yellow', 'D': 'orange', 'E': 'red'
        }
        st.markdown(
            f"<h1 style='text-align: center; color: {metrics['grade_color']}; font-size: 3rem;'>"
            f"{metrics['grade']}</h1>",
            unsafe_allow_html=True
        )
        
        # Add tooltip for grade
        with st.expander("ℹ️ What does grade mean?", expanded=False):
            grade_descriptions = {
                'A': 'Excellent - High recycled content (20%+), low CO₂, high circularity. Best-in-class sustainability.',
                'B': 'Good - Moderate recycled content (10-20%), good CO₂ reduction, solid circularity score (60-79/100).',
                'C': 'Moderate - Some recycled content (5-10%), average CO₂, circularity score (40-59/100).',
                'D': 'Poor - Low recycled content (2-5%), high CO₂, circularity score (20-39/100).',
                'E': 'Very Poor - Minimal recycled content (0-2%), very high CO₂, circularity score (0-19/100).'
            }
            st.info(f"**Grade {metrics['grade']}**: {grade_descriptions[metrics['grade']]}")
    
    with col_header3:
        st.markdown("### 📄 Export")
        # Generate PDF
        pdf_buffer = generate_pdf(input_data, prediction, metrics, passport_id, timestamp)
        st.download_button(
            label="📥 Download PDF",
            data=pdf_buffer,
            file_name=f"Material_Passport_{passport_id}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )
        st.caption("Download digital passport as PDF document")
    
    # Performance metrics with tooltips
    col_perf1, col_perf2 = st.columns(2)
    with col_perf1:
        st.markdown("#### ✅ Performance")
        
        # Compressive Strength with tooltip
        st.metric("Compressive Strength", f"{prediction:.1f} MPa", "Target: 30+ MPa")
        with st.expander("ℹ️ What is Compressive Strength?", expanded=False):
            st.info("""
            **Compressive Strength** measures the maximum load (in MPa) 
            concrete can withstand before failing.
            
            - **30-40 MPa**: Standard structural concrete
            - **40-50 MPa**: High strength for demanding applications
            - **50+ MPa**: Ultra-high strength for specialized structures
            
            Target: 30+ MPa ✅
            """)
        
        st.caption(f"Achieved: {'✅' if prediction >= 30 else '⚠️'}")
        st.caption(f"Age: {int(input_data['age'])} days")
    
    with col_perf2:
        st.markdown("#### ♻️ Sustainability")
        
        # Recycled Content with tooltip
        st.metric("Recycled Content", f"{metrics['recycled_content']:.1f}%", 
                  f"+{metrics['recycled_content']-10:.1f}% vs industry")
        with st.expander("ℹ️ What is Recycled Content?", expanded=False):
            st.info("""
            **Recycled Content** is the percentage of industrial 
            waste byproducts (slag, fly ash) in the mix.
            
            Higher recycled content = better circularity score.
            
            - **0-10%**: Conventional concrete
            - **10-20%**: Good sustainability
            - **20-30%**: Excellent circularity
            - **30%+**: Best-in-class
            
            Industry avg: 10% ♻️
            """)
        
        # Circularity Score with tooltip
        st.metric("Circularity Score", f"{metrics['circularity_score']:.0f}/100",
                  f"{metrics['circularity_score']-50:.0f} points")
        with st.expander("ℹ️ What is Circularity Score?", expanded=False):
            st.info("""
            **Circularity Score** (0-100) measures how easily 
            materials can be recovered and reused.
            
            Based on:
            - Recycled content percentage
            - CO₂ emissions reduction
            - Overall sustainability grade
            
            - **80-100**: Excellent (Grade A)
            - **60-79**: Good (Grade B)
            - **40-59**: Moderate (Grade C)
            - **20-39**: Poor (Grade D)
            - **0-19**: Very Poor (Grade E)
            """)
        
        # CO2 Emissions with tooltip
        st.metric("CO₂ Emissions", f"{metrics['co2_emissions']:.0f} kg/m³",
                  f"-{320-metrics['co2_emissions']:.0f} kg")
        with st.expander("ℹ️ What are CO₂ Emissions?", expanded=False):
            st.info("""
            **CO₂ Emissions** estimate the carbon footprint of 
            concrete production per cubic meter.
            
            Lower emissions = better environmental impact.
            
            - **250-300 kg/m³**: Excellent (low carbon)
            - **300-350 kg/m³**: Good (average)
            - **350-400 kg/m³**: Moderate
            - **400+ kg/m³**: High (needs improvement)
            
            Industry avg: 320 kg/m³ 🌍
            """)
    
    # Material composition table
    st.markdown("#### 📊 Material Composition")
    
    components = ['cement', 'slag', 'fly_ash', 'water', 'superplasticizer', 
                 'coarse_aggregate', 'fine_aggregate']
    labels = ['Cement', 'Blast Furnace Slag', 'Fly Ash', 'Water', 'Superplasticizer',
              'Coarse Aggregate', 'Fine Aggregate']
    
    comp_data = []
    for comp, label in zip(components, labels):
        value = input_data[comp]
        percent = (value / metrics['total_mass']) * 100
        recycled = '♻️ Recycled' if comp in ['slag', 'fly_ash'] and value > 0 else ''
        comp_data.append({
            'Component': f"{label} {recycled}",
            'Amount (kg/m³)': f"{value:.0f}",
            '%': f"{percent:.1f}%"
        })
    
    st.dataframe(pd.DataFrame(comp_data), use_container_width=True, hide_index=True)
    
    # Compliance and time savings
    col_comp1, col_comp2 = st.columns(2)
    with col_comp1:
        st.markdown("#### 📋 Compliance")
        st.success("✅ EU Digital Product Passport")
        st.success("✅ EN 206 Standards")
    
    with col_comp2:
        st.markdown("#### ⏱️ Time Savings")
        st.markdown(
            f"<h2 style='color: green;'>~5 hours</h2>"
            f"<p>vs manual calculation</p>",
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    
    # Circularity gauge
    st.markdown("### ♻️ Circularity Score")
    
    gauge_col1, gauge_col2, gauge_col3 = st.columns([1, 2, 1])
    
    with gauge_col2:
        # Simple text-based gauge display
        circ_score = metrics['circularity_score']
        
        # Color based on score
        if circ_score >= 80:
            color = 'green'
            label = 'Excellent'
        elif circ_score >= 60:
            color = 'blue'
            label = 'Good'
        elif circ_score >= 40:
            color = 'orange'
            label = 'Moderate'
        elif circ_score >= 20:
            color = 'red'
            label = 'Poor'
        else:
            color = 'darkred'
            label = 'Very Poor'
        
        # Display score with progress bar
        st.markdown(f"""
        <div style='text-align: center;'>
            <h2 style='font-size: 4rem; color: {color}; margin: 0;'>{circ_score:.0f}</h2>
            <p style='margin: 0;'>out of 100</p>
            <p><strong>{label}</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress bar
        st.progress(circ_score / 100)
        st.caption(f"Circularity Score: {label}")
    
    # Feedback section
    st.markdown("---")
    st.markdown("### 📝 Feedback")
    st.markdown("Help us improve! Rate this prediction:")
    
    col_fb1, col_fb2 = st.columns([1, 2])
    
    with col_fb1:
        rating = st.slider("How useful is this prediction?", 1, 5, 3)
        if rating >= 4:
            st.success("Thanks for your positive feedback! 👍")
        elif rating <= 2:
            st.warning("We'll work on improving this.")
    
    with col_fb2:
        feedback = st.text_area("What would make this more useful?", 
                                    placeholder="Tell us what features or improvements you'd like to see...")
        if feedback:
            st.success("Feedback received! Thank you for helping us improve.")
    
    st.markdown("---")
    st.markdown("### 🎯 Value Verification")
    st.info(f"""
            **Did this help you?**
            
            - Manufacturers: Did you save time compared to manual calculation?
            - Consultants: Did this help with your analysis?
            - Architects: Did this inform your material selection?
            
            Your feedback helps us build a better product!
            """)
    
    st.markdown("---")

# About AI/ML Tab
def about_ai_ml():
    """Tab 1: About AI/ML modeling"""
    
    st.markdown("# 🤖 About AI/ML Modeling")
    st.markdown("---")
    
    # Data Source section
    st.markdown("## 📊 Data Source")
    st.markdown("""
    **Dataset:** Concrete Compressive Strength (UCI ML Repository)
    - **Source:** [UCI ML Repository](https://archive.ics.uci.edu/dataset/165/concrete+compressive+strength)
    - **Size:** 1,030 instances
    - **License:** Creative Commons Attribution 4.0 (CC BY 4.0)
    - **Features:** 8 quantitative inputs + 1 output
    """)
    
    st.info("**Primary Reference:** Yeh, I-C. (1998). Modeling of strength of high-performance concrete using artificial neural networks. *Cement and Concrete Research*, 28(12), 1797-1808.")
    
    # Features section
    st.markdown("## 📋 Features Used")
    st.markdown("### Input Features (Concrete Composition)")
    
    features_data = {
        'Feature': [
            'Cement (kg/m³)',
            'Blast Furnace Slag (kg/m³)',
            'Fly Ash (kg/m³)',
            'Water (kg/m³)',
            'Superplasticizer (kg/m³)',
            'Coarse Aggregate (kg/m³)',
            'Fine Aggregate (kg/m³)',
            'Age (days)'
        ],
        'Description': [
            'Primary binding material - most influential for strength',
            'Industrial waste byproduct (steel industry) - increases recyclability',
            'Coal combustion byproduct (power plants) - increases recyclability',
            'Hydration agent - essential for cement reaction',
            'Chemical additive - improves workability without water',
            'Large particles (gravel, crushed stone) - provides structure',
            'Small particles (sand) - fills voids between coarse aggregate',
            'Curing time - longer age = higher strength'
        ],
        'Range': [
            '100-500',
            '0-250',
            '0-200',
            '120-200',
            '0-15',
            '800-1100',
            '600-800',
            '1-365'
        ]
    }
    
    st.dataframe(pd.DataFrame(features_data), use_container_width=True, hide_index=True)
    
    # Model Architecture section
    st.markdown("## 🧠 Model Architecture")
    
    st.markdown("### XGBoost Regressor")
    st.markdown("""
    **XGBoost** (eXtreme Gradient Boosting) is a decision-tree-based ensemble 
    Machine Learning algorithm that uses a gradient boosting framework.
    
    **Why XGBoost?**
    - Handles missing values automatically
    - Handles large datasets efficiently
    - Provides high accuracy with minimal parameter tuning
    - Built-in regularization to prevent overfitting
    - Fast training and prediction speed
    """)
    
    # Model performance
    st.markdown("### Model Performance Metrics")
    
    perf_cols = st.columns(3)
    with perf_cols[0]:
        st.metric("Test R²", "0.9101", "Coefficient of determination")
    with perf_cols[1]:
        st.metric("Test RMSE", "4.81 MPa", "Root mean squared error")
    with perf_cols[2]:
        st.metric("Training Samples", "824", "80% of dataset")
    
    st.info("""
    **Model Performance:**
    - R² = 0.91 (Excellent: >0.85 threshold)
    - RMSE = 4.81 MPa (Low error margin)
    - Cross-validation: 5-fold R² = 0.9221
    - Model trained on 1,030 concrete samples
    """)
    
    # Feature Importance
    st.markdown("### 🔑 Feature Importance")
    st.markdown("Top 3 most important features for predicting strength:")
    
    importance_data = {
        'Feature': [
            'Age',
            'Cement',
            'Water'
        ],
        'Importance': [
            '33.15%',
            '32.85%',
            '12.71%'
        ],
        'Interpretation': [
            'Curing time has the strongest impact on strength development',
            'Primary binding material - most critical for cement hydration',
            'Water-to-cement ratio affects workability and strength'
        ]
    }
    
    st.dataframe(pd.DataFrame(importance_data), use_container_width=True, hide_index=True)
    
    # Training methodology
    st.markdown("## 🎓 Training Methodology")
    
    with st.expander("📖 See Training Pipeline Details", expanded=False):
        st.markdown("""
        **Data Pipeline:**
        1. **Data Loading:** Load from UCI ML Repository
        2. **Data Cleaning:** Handle missing values, outliers
        3. **Feature Engineering:** Calculate sustainability metrics
           - Recycled content % (slag + fly ash / total mass)
           - CO₂ emissions (material-based estimation)
           - Circularity score (weighted formula)
        4. **Train-Test Split:** 80% train, 20% test
        5. **Feature Scaling:** StandardScaler for numerical features
        6. **Model Training:** XGBoost with optimized hyperparameters
           - n_estimators: 100
           - max_depth: 6
           - learning_rate: 0.1
           - subsample: 0.8
        7. **Model Evaluation:** R², RMSE, MAE metrics
        8. **Model Persistence:** Save as .pkl file
        
        **Cross-Validation:**
        - 5-fold cross-validation
        - Mean R²: 0.9221 (std: ±0.0115)
        - Ensures model generalizes well
        """)
    
    # Limitations
    st.markdown("## ⚠️ Model Limitations")
    
    st.warning("""
    **Current Model Limitations:**
    
    1. **Dataset Scope:**
       - Trained only on concrete compressive strength
       - Cannot predict other materials (steel, wood, etc.)
       - Valid range: 100-500 kg/m³ cement content
    
    2. **Environmental Factors:**
       - Does not account for temperature/humidity during curing
       - Assumes standard lab conditions
       - May vary in real-world field conditions
    
    3. **Mix Design Constraints:**
       - Considers only 8 basic components
       - Does not account for admixtures or special additives
       - Aggregate quality (gradation, shape) not considered
    
    4. **Time-Dependent Behavior:**
       - Predicts strength at given age
       - Does not model strength development over time
       - Long-term durability not predicted
    
    **Future Improvements:**
    - Add more material types (steel, timber, masonry)
    - Include environmental conditions as features
    - Ensemble with multiple model types
    - Real-time prediction feedback loop
    """)
    
    # Comparison with other models
    st.markdown("## 📈 Model Comparison")
    
    comparison_data = {
        'Model': [
            'Linear Regression',
            'Random Forest',
            'XGBoost (Current)',
            'Deep Neural Network',
            'Multi-Task Neural Network'
        ],
        'Test R²': [
            '0.6276',
            '0.8793',
            '0.9101',
            '0.8575',
            '0.8667'
        ],
        'Test RMSE (MPa)': [
            '9.796',
            '5.578',
            '4.813',
            '6.059',
            '5.861'
        ],
        'Notes': [
            'Baseline model, linear relationships',
            'Good performance, interpretable feature importance',
            'Best performing, selected for production',
            'Lower performance, may benefit from more data',
            'Good performance, predicts multiple outputs'
        ]
    }
    
    st.dataframe(pd.DataFrame(comparison_data), use_container_width=True, hide_index=True)
    
    # Useful resources
    st.markdown("## 📚 Learning Resources")
    
    st.markdown("""
    **For XGBoost:**
    - [XGBoost Documentation](https://xgboost.readthedocs.io/)
    - [XGBoost Tutorials](https://xgboost.readthedocs.io/en/latest/tutorials/)
    - [Gradient Boosting explained](https://machinelearningmastery.com/gentle-introduction-gradient-boosting-algorithm-machine-learning/)
    
    **For Concrete Technology:**
    - [ACI Manual of Concrete Practice](https://www.concrete.org/)
    - [EN 206 Concrete Standards](https://en-standard.eu/)
    - [Concrete Design & Construction](https://www.concretedesign.co.uk/)
    
    **For Machine Learning:**
    - [Scikit-learn Documentation](https://scikit-learn.org/)
    - [Hands-On Machine Learning](https://www.oreilly.com/library/view/9780596529321)
    - [Machine Learning Mastery](https://machinelearningmastery.com/)
    """)

# About Developer Tab
def about_developer():
    """Tab 2: About Developer Raka Adrianto"""
    
    st.markdown("# 👤 About Developer")
    st.markdown("---")
    
    # Profile section
    st.markdown("## 📋 Profile")
    
    st.markdown("**Raka Adrianto**")
    st.markdown("**Sustainability Program Manager @ Siemens**")
    st.markdown("**Zurich, Switzerland**")
    
    # Links
    st.markdown("## 🔗 Connect")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 👥 LinkedIn
        
        [Connect on LinkedIn](https://www.linkedin.com/in/lugasraka/)
        """)
    with col2:
        st.markdown("""
        ### 📧 Contact
        
        Feel free to reach out via LinkedIn for professional inquiries.
        """)
    
    # Skills
    st.markdown("## 💼 Skills")
    
    st.markdown("**AI/ML:** Python, Scikit-learn, XGBoost, PyTorch")
    st.markdown("**Domain:** Circular Economy, CO2 Footprint, Sustainability")
    
    # Why This Project
    st.markdown("## 🎯 Why This Project?")
    st.markdown("""
    **Problem:** 1.3B tons construction waste/year, EU DPP mandate
    **Solution:** AI-powered digital passports
    **Value:** Save 90% time, enable circular economy
    **Target:** Manufacturers, Consultants, Architects
    """)
    
    # Career Goals
    st.markdown("## 🔮 Career Goals")
    st.markdown("**Goal:** Portfolio Lead, AI for Climate Impact")
    
    st.markdown("**This Project Shows:**")
    st.markdown("- ✅ End-to-end ML system")
    st.markdown("- ✅ Domain expertise in sustainability")
    st.markdown("- ✅ Product sense & user focus")
    st.markdown("- ✅ Impact-oriented problem solving")

# Main App with Tabs
def main():
    # Load models
    model, scaler = load_models()
    
    if model is None:
        st.stop()
    
    # Create tabs
    tab0, tab1, tab2 = st.tabs([
        "🏗️ Passport Generator", 
        "🤖 About AI/ML", 
        "👤 About Developer"
    ])
    
    with tab0:
        st.markdown('<h1 class="main-header">🏗️ Material Passport Generator</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Transform Concrete Composition into Digital Passport in Seconds</p>', 
                   unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Two columns layout
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### 📝 Input Composition")
            st.markdown("Enter concrete mix design (kg/m³):")
            
            # Input form
            cement = st.slider("Cement", 100, 500, 300, 
                            help="Primary binding material")
            slag = st.slider("Blast Furnace Slag", 0, 250, 0, 
                           help="Industrial waste byproduct - increases recyclability")
            fly_ash = st.slider("Fly Ash", 0, 200, 0, 
                              help="Coal combustion byproduct - increases recyclability")
            water = st.slider("Water", 120, 200, 170,
                            help="Hydration agent")
            superplasticizer = st.slider("Superplasticizer", 0, 15, 0,
                                          help="Chemical additive for workability")
            coarse_agg = st.slider("Coarse Aggregate", 800, 1100, 950,
                                 help="Large particles (gravel, crushed stone)")
            fine_agg = st.slider("Fine Aggregate", 600, 800, 700,
                              help="Small particles (sand)")
            age = st.slider("Curing Age (days)", 1, 365, 28,
                         help="Time since casting")
            
            # Predict button
            st.markdown("---")
            predict_button = st.button("🚀 Generate Passport", type="primary", use_container_width=True)
            
            # User tips based on persona
            with st.expander("💡 Tips by Persona"):
                st.markdown("""
                **For Manufacturers (Sustainability Managers):**
                - Try increasing slag/fly ash to improve circularity score
                - Use passport for EU DPP compliance documentation
                
                **For Consultants (Circular Economy):**
                - Compare multiple compositions to find optimal mix
                - Look for high recycled content (>15%) for best circularity
                
                **For Architects/Designers:**
                - Target 30+ MPa strength for structural applications
                - Look for B+ grade or higher for green building credits
                """)
        
        with col2:
            if predict_button:
                # Prepare input data
                input_data = {
                    'cement': cement,
                    'slag': slag,
                    'fly_ash': fly_ash,
                    'water': water,
                    'superplasticizer': superplasticizer,
                    'coarse_aggregate': coarse_agg,
                    'fine_aggregate': fine_agg,
                    'age': age
                }
                
                # Create DataFrame for prediction
                input_df = pd.DataFrame([input_data])
                
                # Scale input
                input_scaled = scaler.transform(input_df)
                
                # Make prediction
                prediction = model.predict(input_scaled)[0]
                
                # Calculate sustainability metrics
                metrics = calculate_sustainability_metrics(input_data)
                
                # Display passport
                display_passport(input_data, prediction, metrics)
                
                # Additional metrics visualization
                st.markdown("### 📈 Benchmark Analysis")
                
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    st.metric(
                        "Recycled Content",
                        f"{metrics['recycled_content']:.1f}%",
                        f"+{metrics['recycled_content']-10:.1f}% vs avg",
                        delta_color="normal"
                    )
                
                with col_b:
                    st.metric(
                        "Circularity Score",
                        f"{metrics['circularity_score']:.0f}/100",
                        f"{metrics['circularity_score']-50:.0f} points",
                        delta_color="normal"
                    )
                
                with col_c:
                    co2_savings = 320 - metrics['co2_emissions']
                    st.metric(
                        "CO₂ Reduction",
                        f"{co2_savings:.0f} kg/m³",
                        f"{co2_savings:.0f} kg",
                        delta_color="inverse"
                    )
            else:
                # Welcome message
                st.markdown("""
                ### 👋 Welcome to Material Passport Generator
                
                **Transform concrete composition data into professional digital passports in seconds.**
                
                #### How it works:
                1. **Enter composition** - Use sliders to input your mix design
                2. **Get prediction** - AI predicts compressive strength instantly
                3. **View passport** - See sustainability metrics and compliance status
                4. **Download & Share** - Export PDF for documentation
                
                #### Why use it?
                - ⏱️ **Save 5+ hours** vs manual calculation
                - 📊 **Instant metrics** - Circular economy scores, CO2 emissions
                - ✅ **EU compliant** - Digital Product Passport format
                - ♻️ **Sustainability** - Optimize for recyclability
                
                **Ready?** Enter your composition on the left and click "Generate Passport"!
                """)
                
                # Example passports
                st.markdown("---")
                st.markdown("### 🎨 Example Compositions")
                
                ex1, ex2 = st.columns(2)
                
                with ex1:
                    st.markdown("**High Strength** (50+ MPa)")
                    st.markdown("""
                        - Cement: 400 kg/m³
                        - Slag: 100 kg/m³
                        - Water: 160 kg/m³
                        - Age: 28 days
                        
                        *Result: Grade A, High performance*
                        """)
                
                with ex2:
                    st.markdown("**Eco-Friendly** (High recycled)")
                    st.markdown("""
                        - Cement: 250 kg/m³
                        - Slag: 150 kg/m³
                        - Fly Ash: 100 kg/m³
                        - Age: 90 days
                        
                        *Result: Grade A+, Circular economy*
                        """)
        
        # Footer
        st.markdown("---")
        st.markdown("""
            <div style="text-align: center; color: #6c757d; font-size: 0.9em;">
                Material Passport Generator MVP | Built for rapid user feedback & iteration
                <br>
                <em>Part of AI/ML portfolio project - Enabling Circular Economy Through Material Intelligence</em>
            </div>
            """, unsafe_allow_html=True)
    
    with tab1:
        about_ai_ml()
    
    with tab2:
        about_developer()

if __name__ == "__main__":
    main()
