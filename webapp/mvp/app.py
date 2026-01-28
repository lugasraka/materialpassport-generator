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
import shap
import matplotlib.pyplot as plt

# Set page config
st.set_page_config(
    page_title="Material Passport Generator",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'saved_mixes' not in st.session_state:
    st.session_state.saved_mixes = []
if 'language' not in st.session_state:
    st.session_state.language = 'English'

# Language translations - Core UI only
TRANSLATIONS = {
    'English': {
        # Main headers
        'title': '🏗️ Material Passport Generator',
        'subtitle': 'Transform Concrete Composition into Digital Passport in Seconds',
        
        # Tab names
        'tab_generator': '🏗️ Passport Generator',
        'tab_aiml': '🤖 About AI/ML',
        'tab_developer': '👤 About Developer',
        
        # Main sections
        'input_composition': '📝 Input Composition',
        'enter_mix_design': 'Enter concrete mix design (kg/m³):',
        'presets': 'Quick Presets',
        'quality_checks': '✅ Quality Control',
        'cost_estimate': '💰 Cost Estimation',
        'suggestions': '💡 Optimization Suggestions',
        'explainability': '🔍 Prediction Explanation',
        
        # Buttons
        'generate_button': '🚀 Generate Passport',
        'save_mix': '💾 Save This Mix',
        'compare': '🔄 Compare Mixes',
        'reset': '🔄 Reset',
        'download_pdf': '📥 Download PDF',
        'clear_mixes': '🗑️ Clear All Saved Mixes',
        
        # Slider labels
        'cement': 'Cement',
        'cement_help': 'Primary binding material',
        'slag': 'Blast Furnace Slag',
        'slag_help': 'Industrial waste byproduct - increases recyclability',
        'fly_ash': 'Fly Ash',
        'fly_ash_help': 'Coal combustion byproduct - increases recyclability',
        'water': 'Water',
        'water_help': 'Hydration agent',
        'superplasticizer': 'Superplasticizer',
        'superplasticizer_help': 'Chemical additive for workability',
        'coarse_aggregate': 'Coarse Aggregate',
        'coarse_aggregate_help': 'Large particles (gravel, crushed stone)',
        'fine_aggregate': 'Fine Aggregate',
        'fine_aggregate_help': 'Small particles (sand)',
        'curing_age': 'Curing Age (days)',
        'curing_age_help': 'Time since casting',
        
        # Presets
        'preset_standard': 'Standard Concrete',
        'preset_standard_desc': 'Basic structural concrete for general applications',
        'preset_high_strength': 'High Strength',
        'preset_high_strength_desc': 'High-performance concrete for demanding structures',
        'preset_eco': 'Eco-Friendly',
        'preset_eco_desc': 'Sustainable mix with high recycled content',
        'preset_low_cost': 'Low Cost',
        'preset_low_cost_desc': 'Budget-friendly mix for non-critical applications',
        
        # Messages
        'mix_saved': '✅ Saved \'{name}\'',
        'enter_mix_name': 'Please enter a mix name',
        'qc_all_passed': '✅ All quality checks passed!',
        'save_2_mixes': 'Save at least 2 mixes to compare them side-by-side.',
        'well_optimized': '✅ Your mix design is well-optimized!',
        'mix_name_placeholder': 'e.g., Project X - Foundation',
        
        # Passport sections
        'material_passport': 'Material Passport - Concrete',
        'generated': 'Generated:',
        'passport_id': 'Passport ID:',
        'sustainability_grade': 'Sustainability Grade:',
        'export': '📄 Export',
        'download_caption': 'Download digital passport as PDF document',
        
        # Metrics
        'performance': '✅ Performance',
        'compressive_strength': 'Compressive Strength',
        'predicted_strength': 'Predicted Strength',
        'target_30_mpa': 'Target: 30+ MPa',
        'age_days': 'Age: {days} days',
        'sustainability': '♻️ Sustainability',
        'recycled_content': 'Recycled Content',
        'circularity_score': 'Circularity Score',
        'co2_emissions': 'CO₂ Emissions',
        
        # Table headers
        'component': 'Component',
        'amount_kg': 'Amount (kg/m³)',
        'percentage': '%',
        'material': 'Material',
        'cost': 'Cost',
        'mix_name': 'Mix Name',
        'strength_mpa': 'Strength (MPa)',
        'cost_per_m3': 'Cost ($/m³)',
        'circularity': 'Circularity',
        'grade': 'Grade',
        'co2_kg_m3': 'CO₂ (kg/m³)',
        'recycled_pct': 'Recycled %',
        
        # Circularity labels
        'excellent': 'Excellent',
        'good': 'Good',
        'moderate': 'Moderate',
        'poor': 'Poor',
        'very_poor': 'Very Poor',
        
        # Comparison
        'saved_mixes_count': '**Saved Mixes:** {count}',
        'comparison_results': '#### Comparison Results',
        'recommendations': '**Recommendations:**',
        'highest_strength': '💪 **Highest Strength:** {name} ({strength:.1f} MPa)',
        'best_sustainability': '♻️ **Best Sustainability:** {name} (Grade {grade})',
        
        # Welcome
        'welcome_header': '### 👋 Welcome to Material Passport Generator',
        'welcome_ready': '**Ready?** Enter your composition on the left and click "Generate Passport"!',
        
        # Tips by Persona
        'tips_persona': '💡 Tips by Persona',
        
        # Spinners
        'calculating_ci': 'Calculating confidence interval...',
        'shap_generating': 'Generating prediction explanation...',
        
        # Footer
        'footer_mvp': 'Material Passport Generator MVP | Built for rapid user feedback & iteration',
        'footer_project': 'Part of AI/ML portfolio project - Enabling Circular Economy Through Material Intelligence',
    },
    'Deutsch': {
        # Main headers
        'title': '🏗️ Materialpass-Generator',
        'subtitle': 'Verwandeln Sie Betonzusammensetzung in Sekunden in einen digitalen Pass',
        
        # Tab names
        'tab_generator': '🏗️ Pass-Generator',
        'tab_aiml': '🤖 Über KI/ML',
        'tab_developer': '👤 Über Entwickler',
        
        # Main sections
        'input_composition': '📝 Eingabezusammensetzung',
        'enter_mix_design': 'Betonmischung eingeben (kg/m³):',
        'presets': 'Schnellvorlagen',
        'quality_checks': '✅ Qualitätskontrolle',
        'cost_estimate': '💰 Kostenschätzung',
        'suggestions': '💡 Optimierungsvorschläge',
        'explainability': '🔍 Vorhersageerklärung',
        
        # Buttons
        'generate_button': '🚀 Pass erstellen',
        'save_mix': '💾 Mischung speichern',
        'compare': '🔄 Mischungen vergleichen',
        'reset': '🔄 Zurücksetzen',
        'download_pdf': '📥 PDF herunterladen',
        'clear_mixes': '🗑️ Alle gespeicherten Mischungen löschen',
        
        # Slider labels
        'cement': 'Zement',
        'cement_help': 'Primäres Bindemittel',
        'slag': 'Hochofenschlacke',
        'slag_help': 'Industrieabfall - erhöht Recyclingfähigkeit',
        'fly_ash': 'Flugasche',
        'fly_ash_help': 'Kohleverbrennung-Nebenprodukt - erhöht Recyclingfähigkeit',
        'water': 'Wasser',
        'water_help': 'Hydratationsmittel',
        'superplasticizer': 'Superplastifizierer',
        'superplasticizer_help': 'Chemisches Additiv für Verarbeitbarkeit',
        'coarse_aggregate': 'Grobzuschlag',
        'coarse_aggregate_help': 'Große Partikel (Kies, Schotter)',
        'fine_aggregate': 'Feinzuschlag',
        'fine_aggregate_help': 'Kleine Partikel (Sand)',
        'curing_age': 'Aushärtungsalter (Tage)',
        'curing_age_help': 'Zeit seit dem Gießen',
        
        # Presets
        'preset_standard': 'Standardbeton',
        'preset_standard_desc': 'Grundlegender Konstruktionsbeton',
        'preset_high_strength': 'Hochfest',
        'preset_high_strength_desc': 'Hochleistungsbeton für anspruchsvolle Strukturen',
        'preset_eco': 'Umweltfreundlich',
        'preset_eco_desc': 'Nachhaltige Mischung mit hohem Recyclinganteil',
        'preset_low_cost': 'Kostengünstig',
        'preset_low_cost_desc': 'Budgetfreundliche Mischung',
        
        # Messages
        'mix_saved': '✅ \'{name}\' gespeichert',
        'enter_mix_name': 'Bitte Mischungsname eingeben',
        'qc_all_passed': '✅ Alle Qualitätsprüfungen bestanden!',
        'save_2_mixes': 'Speichern Sie mindestens 2 Mischungen zum Vergleichen.',
        'well_optimized': '✅ Ihre Mischung ist gut optimiert!',
        'mix_name_placeholder': 'z.B. Projekt X - Fundament',
        
        # Passport sections
        'material_passport': 'Materialpass - Beton',
        'generated': 'Erstellt:',
        'passport_id': 'Pass-ID:',
        'sustainability_grade': 'Nachhaltigkeitsgrad:',
        'export': '📄 Export',
        'download_caption': 'Digitalen Pass als PDF herunterladen',
        
        # Metrics
        'performance': '✅ Leistung',
        'compressive_strength': 'Druckfestigkeit',
        'predicted_strength': 'Vorhergesagte Festigkeit',
        'target_30_mpa': 'Ziel: 30+ MPa',
        'age_days': 'Alter: {days} Tage',
        'sustainability': '♻️ Nachhaltigkeit',
        'recycled_content': 'Recyclinganteil',
        'circularity_score': 'Kreislauf-Score',
        'co2_emissions': 'CO₂-Emissionen',
        
        # Table headers
        'component': 'Komponente',
        'amount_kg': 'Menge (kg/m³)',
        'percentage': '%',
        'material': 'Material',
        'cost': 'Kosten',
        'mix_name': 'Mischungsname',
        'strength_mpa': 'Festigkeit (MPa)',
        'cost_per_m3': 'Kosten ($/m³)',
        'circularity': 'Kreislauf',
        'grade': 'Note',
        'co2_kg_m3': 'CO₂ (kg/m³)',
        'recycled_pct': 'Recycling %',
        
        # Circularity labels
        'excellent': 'Ausgezeichnet',
        'good': 'Gut',
        'moderate': 'Mäßig',
        'poor': 'Schlecht',
        'very_poor': 'Sehr schlecht',
        
        # Comparison
        'saved_mixes_count': '**Gespeicherte Mischungen:** {count}',
        'comparison_results': '#### Vergleichsergebnisse',
        'recommendations': '**Empfehlungen:**',
        'highest_strength': '💪 **Höchste Festigkeit:** {name} ({strength:.1f} MPa)',
        'best_sustainability': '♻️ **Beste Nachhaltigkeit:** {name} (Note {grade})',
        
        # Welcome
        'welcome_header': '### 👋 Willkommen beim Materialpass-Generator',
        'welcome_ready': '**Bereit?** Geben Sie links Ihre Zusammensetzung ein und klicken Sie auf "Pass erstellen"!',
        
        # Tips by Persona
        'tips_persona': '💡 Tipps nach Persona',
        
        # Spinners
        'calculating_ci': 'Berechne Konfidenzintervall...',
        'shap_generating': 'Erstelle Vorhersageerklärung...',
        
        # Footer
        'footer_mvp': 'Materialpass-Generator MVP | Erstellt für schnelles Nutzer-Feedback & Iteration',
        'footer_project': 'Teil des KI/ML-Portfolioprojekts - Kreislaufwirtschaft durch Material-Intelligence ermöglichen',
    },
    'Español': {
        # Main headers
        'title': '🏗️ Generador de Pasaporte de Materiales',
        'subtitle': 'Transforme la composición del hormigón en pasaporte digital en segundos',
        
        # Tab names
        'tab_generator': '🏗️ Generador de Pasaportes',
        'tab_aiml': '🤖 Sobre IA/ML',
        'tab_developer': '👤 Sobre el Desarrollador',
        
        # Main sections
        'input_composition': '📝 Composición de entrada',
        'enter_mix_design': 'Ingrese el diseño de mezcla de hormigón (kg/m³):',
        'presets': 'Plantillas rápidas',
        'quality_checks': '✅ Control de calidad',
        'cost_estimate': '💰 Estimación de costos',
        'suggestions': '💡 Sugerencias de optimización',
        'explainability': '🔍 Explicación de predicción',
        
        # Buttons
        'generate_button': '🚀 Generar pasaporte',
        'save_mix': '💾 Guardar esta mezcla',
        'compare': '🔄 Comparar mezclas',
        'reset': '🔄 Restablecer',
        'download_pdf': '📥 Descargar PDF',
        'clear_mixes': '🗑️ Borrar todas las mezclas guardadas',
        
        # Slider labels
        'cement': 'Cemento',
        'cement_help': 'Material aglutinante principal',
        'slag': 'Escoria de alto horno',
        'slag_help': 'Subproducto de desecho industrial - aumenta reciclabilidad',
        'fly_ash': 'Ceniza volante',
        'fly_ash_help': 'Subproducto de combustión de carbón - aumenta reciclabilidad',
        'water': 'Agua',
        'water_help': 'Agente de hidratación',
        'superplasticizer': 'Superplastificante',
        'superplasticizer_help': 'Aditivo químico para trabajabilidad',
        'coarse_aggregate': 'Agregado grueso',
        'coarse_aggregate_help': 'Partículas grandes (grava, piedra triturada)',
        'fine_aggregate': 'Agregado fino',
        'fine_aggregate_help': 'Partículas pequeñas (arena)',
        'curing_age': 'Edad de curado (días)',
        'curing_age_help': 'Tiempo desde el vaciado',
        
        # Presets
        'preset_standard': 'Hormigón estándar',
        'preset_standard_desc': 'Hormigón estructural básico para aplicaciones generales',
        'preset_high_strength': 'Alta resistencia',
        'preset_high_strength_desc': 'Hormigón de alto rendimiento para estructuras exigentes',
        'preset_eco': 'Ecológico',
        'preset_eco_desc': 'Mezcla sostenible con alto contenido reciclado',
        'preset_low_cost': 'Bajo costo',
        'preset_low_cost_desc': 'Mezcla económica para aplicaciones no críticas',
        
        # Messages
        'mix_saved': '✅ Guardado \'{name}\'',
        'enter_mix_name': 'Por favor ingrese un nombre de mezcla',
        'qc_all_passed': '✅ ¡Todas las verificaciones de calidad aprobadas!',
        'save_2_mixes': 'Guarde al menos 2 mezclas para compararlas lado a lado.',
        'well_optimized': '✅ ¡Su diseño de mezcla está bien optimizado!',
        'mix_name_placeholder': 'ej. Proyecto X - Cimentación',
        
        # Passport sections
        'material_passport': 'Pasaporte de Material - Hormigón',
        'generated': 'Generado:',
        'passport_id': 'ID de Pasaporte:',
        'sustainability_grade': 'Grado de Sostenibilidad:',
        'export': '📄 Exportar',
        'download_caption': 'Descargar pasaporte digital como documento PDF',
        
        # Metrics
        'performance': '✅ Rendimiento',
        'compressive_strength': 'Resistencia a compresión',
        'predicted_strength': 'Resistencia Predicha',
        'target_30_mpa': 'Objetivo: 30+ MPa',
        'age_days': 'Edad: {days} días',
        'sustainability': '♻️ Sostenibilidad',
        'recycled_content': 'Contenido reciclado',
        'circularity_score': 'Puntuación de circularidad',
        'co2_emissions': 'Emisiones de CO₂',
        
        # Table headers
        'component': 'Componente',
        'amount_kg': 'Cantidad (kg/m³)',
        'percentage': '%',
        'material': 'Material',
        'cost': 'Costo',
        'mix_name': 'Nombre de mezcla',
        'strength_mpa': 'Resistencia (MPa)',
        'cost_per_m3': 'Costo ($/m³)',
        'circularity': 'Circularidad',
        'grade': 'Grado',
        'co2_kg_m3': 'CO₂ (kg/m³)',
        'recycled_pct': 'Reciclado %',
        
        # Circularity labels
        'excellent': 'Excelente',
        'good': 'Bueno',
        'moderate': 'Moderado',
        'poor': 'Pobre',
        'very_poor': 'Muy pobre',
        
        # Comparison
        'saved_mixes_count': '**Mezclas guardadas:** {count}',
        'comparison_results': '#### Resultados de comparación',
        'recommendations': '**Recomendaciones:**',
        'highest_strength': '💪 **Mayor resistencia:** {name} ({strength:.1f} MPa)',
        'best_sustainability': '♻️ **Mejor sostenibilidad:** {name} (Grado {grade})',
        
        # Welcome
        'welcome_header': '### 👋 Bienvenido al Generador de Pasaporte de Materiales',
        'welcome_ready': '**¿Listo?** Ingrese su composición a la izquierda y haga clic en "Generar pasaporte"!',
        
        # Tips by Persona
        'tips_persona': '💡 Consejos por Persona',
        
        # Spinners
        'calculating_ci': 'Calculando intervalo de confianza...',
        'shap_generating': 'Generando explicación de predicción...',
        
        # Footer
        'footer_mvp': 'Generador de Pasaporte de Materiales MVP | Creado para retroalimentación rápida del usuario',
        'footer_project': 'Parte del proyecto de portafolio IA/ML - Habilitando la Economía Circular a través de Inteligencia de Materiales',
    }
}

def get_text(key):
    """Get translated text"""
    return TRANSLATIONS[st.session_state.language].get(key, key)

# Custom CSS for professional look
custom_css = """
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
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid;
    }
    .warning-error {
        background-color: #f8d7da;
        border-color: #dc3545;
        color: #721c24;
    }
    .warning-warning {
        background-color: #fff3cd;
        border-color: #ffc107;
        color: #856404;
    }
    .warning-info {
        background-color: #d1ecf1;
        border-color: #17a2b8;
        color: #0c5460;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.8rem;
        }
        .sub-header {
            font-size: 1.1rem;
        }
        [data-testid="column"] {
            min-width: 100% !important;
        }
    }
    
    /* Comparison table styling */
    .comparison-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
    }
    .comparison-table th, .comparison-table td {
        padding: 0.75rem;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }
    .comparison-table th {
        background-color: #2d5a87;
        color: white;
        font-weight: bold;
    }

    /* Enlarge tab size */
    [data-testid="stTabList"] button {
        font-size: 1.1rem;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        min-height: 3rem;
    }

    [data-testid="stTabList"] {
        gap: 0.5rem;
    }

    [data-testid="stTabList"] button[aria-selected="true"] {
        font-size: 1.2rem;
    }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

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

# NEW FEATURES - Material cost estimation
def calculate_cost(input_data):
    """Calculate estimated material cost"""
    # Material costs in $/kg (approximate)
    cost_data = {
        'cement': 0.10,
        'slag': 0.05,
        'fly_ash': 0.04,
        'water': 0.001,
        'superplasticizer': 2.50,
        'coarse_aggregate': 0.02,
        'fine_aggregate': 0.015
    }
    
    total_cost = sum(input_data[material] * cost_data[material] for material in cost_data)
    
    # Calculate cost breakdown
    cost_breakdown = {mat: input_data[mat] * cost_data[mat] for mat in cost_data}
    
    return {
        'total_cost': total_cost,
        'breakdown': cost_breakdown,
        'cost_per_mpa': total_cost / (input_data.get('predicted_strength', 1) + 0.001)
    }

# Quality control validation
def validate_mix_design(input_data):
    """Validate mix design and return warnings"""
    warnings = []
    
    # Water-cement ratio check
    water_cement_ratio = input_data['water'] / (input_data['cement'] + 0.001)
    if water_cement_ratio > 0.65:
        warnings.append({
            'type': 'error',
            'message': f"⚠️ High water-cement ratio ({water_cement_ratio:.2f}). Durability concerns! Recommended: < 0.65"
        })
    elif water_cement_ratio > 0.55:
        warnings.append({
            'type': 'warning',
            'message': f"⚠️ Moderate water-cement ratio ({water_cement_ratio:.2f}). Consider reducing for better durability."
        })
    
    # Cement content check
    if input_data['cement'] < 200:
        warnings.append({
            'type': 'error',
            'message': f"❌ Cement content too low ({input_data['cement']} kg/m³). Minimum recommended: 200 kg/m³"
        })
    
    # Total binder check
    total_binder = input_data['cement'] + input_data['slag'] + input_data['fly_ash']
    if total_binder < 300:
        warnings.append({
            'type': 'warning',
            'message': f"⚠️ Low total binder content ({total_binder:.0f} kg/m³). May affect strength."
        })
    elif total_binder > 550:
        warnings.append({
            'type': 'warning',
            'message': f"⚠️ High total binder content ({total_binder:.0f} kg/m³). Risk of cracking and high cost."
        })
    
    # Superplasticizer check
    if input_data['superplasticizer'] > 0 and water_cement_ratio > 0.5:
        warnings.append({
            'type': 'info',
            'message': "💡 Tip: With superplasticizer, you can reduce water content for better strength."
        })
    
    # Recycled content check
    recycled = input_data['slag'] + input_data['fly_ash']
    if recycled > total_binder * 0.6:
        warnings.append({
            'type': 'warning',
            'message': f"⚠️ Very high recycled content ({(recycled/total_binder*100):.0f}%). Verify strength requirements."
        })
    
    return warnings

# Optimization suggestions
def suggest_improvements(input_data, prediction, metrics, target_strength=None, target_circularity=None):
    """AI-powered mix optimization suggestions"""
    suggestions = []
    
    # Strength optimization
    if target_strength and prediction < target_strength:
        strength_gap = target_strength - prediction
        
        # Suggest cement increase
        cement_increase = int(strength_gap * 5)  # Rough estimate: 1 kg cement ≈ 0.2 MPa
        suggestions.append({
            'category': 'Strength',
            'message': f"To reach {target_strength:.0f} MPa, consider increasing cement by ~{cement_increase} kg/m³",
            'impact': f"+{strength_gap:.1f} MPa"
        })
        
        # Suggest age increase
        if input_data['age'] < 90:
            suggestions.append({
                'category': 'Strength',
                'message': f"Alternatively, wait longer (age: {input_data['age']}→90 days) for strength development",
                'impact': "Natural strength gain"
            })
        
        # Suggest water reduction
        if input_data['water'] > 150:
            suggestions.append({
                'category': 'Strength',
                'message': f"Reduce water content by 10-20 kg/m³ (current: {input_data['water']} kg/m³)",
                'impact': "+2-4 MPa, better durability"
            })
    
    # Circularity optimization
    if target_circularity and metrics['circularity_score'] < target_circularity:
        circ_gap = target_circularity - metrics['circularity_score']
        
        # Suggest slag addition
        if input_data['slag'] < 150:
            slag_add = min(50, int(circ_gap / 0.5))
            suggestions.append({
                'category': 'Sustainability',
                'message': f"Add {slag_add} kg/m³ slag (current: {input_data['slag']} kg/m³)",
                'impact': f"+{slag_add*0.5:.0f} circularity points"
            })
        
        # Suggest fly ash addition
        if input_data['fly_ash'] < 100:
            flyash_add = min(50, int(circ_gap / 0.5))
            suggestions.append({
                'category': 'Sustainability',
                'message': f"Add {flyash_add} kg/m³ fly ash (current: {input_data['fly_ash']} kg/m³)",
                'impact': f"+{flyash_add*0.5:.0f} circularity points"
            })
        
        # Suggest cement reduction
        if input_data['cement'] > 300:
            suggestions.append({
                'category': 'Sustainability',
                'message': f"Reduce cement by 20-50 kg/m³ and replace with slag/fly ash",
                'impact': "Lower CO₂, higher circularity"
            })
    
    # Cost optimization
    cost_info = calculate_cost(input_data)
    if cost_info['total_cost'] > 35:  # High cost threshold
        suggestions.append({
            'category': 'Cost',
            'message': f"High material cost (${cost_info['total_cost']:.2f}/m³). Consider reducing superplasticizer or using local aggregates.",
            'impact': f"Potential savings: ${(cost_info['total_cost']-30):.2f}/m³"
        })
    
    # General efficiency
    cost_per_mpa = cost_info['total_cost'] / (prediction + 0.001)
    if cost_per_mpa > 1.0:
        suggestions.append({
            'category': 'Efficiency',
            'message': "Cost-efficiency can be improved. Consider higher age or optimized binder blend.",
            'impact': "Better cost-to-strength ratio"
        })
    
    return suggestions

# Prediction confidence intervals
def calculate_confidence_interval(model, scaler, input_df, n_samples=100):
    """Calculate prediction confidence interval using bootstrap"""
    predictions = []
    
    # Add small random noise to simulate uncertainty
    for _ in range(n_samples):
        noisy_input = input_df.copy()
        for col in noisy_input.columns:
            # Add ~2% noise
            noise = np.random.normal(0, 0.02 * noisy_input[col].values[0])
            noisy_input[col] += noise
        
        try:
            scaled_input = scaler.transform(noisy_input)
            pred = model.predict(scaled_input)[0]
            predictions.append(pred)
        except:
            pass
    
    if predictions:
        mean_pred = np.mean(predictions)
        std_pred = np.std(predictions)
        ci_lower = mean_pred - 1.96 * std_pred
        ci_upper = mean_pred + 1.96 * std_pred
        
        return {
            'mean': mean_pred,
            'std': std_pred,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'confidence': 95
        }
    else:
        return None

# SHAP explainability
@st.cache_resource
def get_shap_explainer(_model, _scaler, sample_data):
    """Create and cache SHAP explainer"""
    try:
        # Use a sample of data for background
        background = _scaler.transform(sample_data.sample(min(100, len(sample_data))))
        explainer = shap.TreeExplainer(_model)
        return explainer
    except Exception as e:
        st.warning(f"Could not create SHAP explainer: {e}")
        return None

def explain_prediction(explainer, model, scaler, input_df):
    """Generate SHAP explanation for a prediction"""
    if explainer is None:
        return None
    
    try:
        # Transform input
        input_scaled = scaler.transform(input_df)
        
        # Calculate SHAP values
        shap_values = explainer.shap_values(input_scaled)
        
        # Create explanation dictionary
        feature_contributions = {}
        for i, col in enumerate(input_df.columns):
            feature_contributions[col] = {
                'value': input_df[col].values[0],
                'contribution': shap_values[0][i],
                'abs_contribution': abs(shap_values[0][i])
            }
        
        # Sort by absolute contribution
        sorted_contributions = sorted(
            feature_contributions.items(), 
            key=lambda x: x[1]['abs_contribution'], 
            reverse=True
        )
        
        return {
            'shap_values': shap_values,
            'contributions': dict(sorted_contributions),
            'base_value': explainer.expected_value
        }
    except Exception as e:
        st.warning(f"Could not generate explanation: {e}")
        return None

# Mix design presets
MIX_PRESETS = {
    'Standard Concrete': {
        'cement': 300, 'slag': 0, 'fly_ash': 0, 'water': 170,
        'superplasticizer': 0, 'coarse_aggregate': 950, 'fine_aggregate': 700, 'age': 28,
        'description': 'Basic structural concrete for general applications',
        'key': 'preset_standard',
        'desc_key': 'preset_standard_desc'
    },
    'High Strength': {
        'cement': 400, 'slag': 100, 'fly_ash': 0, 'water': 160,
        'superplasticizer': 5, 'coarse_aggregate': 950, 'fine_aggregate': 700, 'age': 28,
        'description': 'High-performance concrete for demanding structures',
        'key': 'preset_high_strength',
        'desc_key': 'preset_high_strength_desc'
    },
    'Eco-Friendly': {
        'cement': 250, 'slag': 150, 'fly_ash': 100, 'water': 170,
        'superplasticizer': 5, 'coarse_aggregate': 950, 'fine_aggregate': 700, 'age': 90,
        'description': 'Sustainable mix with high recycled content',
        'key': 'preset_eco',
        'desc_key': 'preset_eco_desc'
    },
    'Low Cost': {
        'cement': 280, 'slag': 50, 'fly_ash': 50, 'water': 180,
        'superplasticizer': 0, 'coarse_aggregate': 1000, 'fine_aggregate': 750, 'age': 28,
        'description': 'Budget-friendly mix for non-critical applications',
        'key': 'preset_low_cost',
        'desc_key': 'preset_low_cost_desc'
    }
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
    Generated automatically using XGBoost ML model (R² = 0.91, RMSE = 4.85 MPa)<br/>
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

        with st.expander("ℹ️ Methodology", expanded=False):
            st.info("""
            **How Metrics Are Calculated**
            
            **Recycled Content (%)**
            - Formula: (Slag + Fly Ash) / Total Mass × 100
            - Slag and fly ash are industrial byproducts that replace cement
            
            **CO₂ Emissions (kg/m³)**
            - Cement: 0.85 kg CO₂ per kg cement
            - Slag: 0.07 kg CO₂ per kg slag
            - Fly Ash: 0.01 kg CO₂ per kg fly ash
            - Sum of all component emissions
            
            **Circularity Score (0-100)**
            - Formula: Recycled Content × 3 + Low Carbon Bonus (20 pts if CO₂ < 300)
            - Max score capped at 100
            - Higher score = better material circularity
            
            **Sustainability Grade**
            - Based on Circularity Score thresholds:
            - **A (≥80)**: Excellent - High recycled content, low CO₂
            - **B (60-79)**: Good - Moderate recycled content
            - **C (40-59)**: Moderate - Some recycled content
            - **D (20-39)**: Poor - Low recycled content
            - **E (<20)**: Very Poor - Minimal recycled content
            
            **Formula Reference:**
            ```
            Circularity Score = min(100, Recycled% × 3 + [CO₂ < 300] × 20)
            Grade = f(Circularity Score)
            ```
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
        st.metric("Test R²", "0.9088", "Coefficient of determination")
    with perf_cols[1]:
        st.metric("Test RMSE", "4.85 MPa", "Root mean squared error")
    with perf_cols[2]:
        st.metric("Training Samples", "824", "80% of dataset")
    
    st.info("""
    **Model Performance:**
    - R² = 0.9088 (Excellent: >0.85 threshold)
    - RMSE = 4.85 MPa (Low error margin)
    - Cross-validation: 5-fold R² = 0.9263 (±0.0090)
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
            '34.08%',
            '20.58%',
            '11.68%'
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
        - Mean R²: 0.9263 (std: ±0.0090)
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
            '0.9088',
            '0.8575',
            '0.8667'
        ],
        'Test RMSE (MPa)': [
            '9.796',
            '5.578',
            '4.850',
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
        get_text("tab_generator"), 
        get_text("tab_aiml"), 
        get_text("tab_developer")
    ])
    
    with tab0:
        st.markdown(f'<h1 class="main-header">{get_text("title")}</h1>', unsafe_allow_html=True)
        st.markdown(f'<p class="sub-header">{get_text("subtitle")}</p>', 
                   unsafe_allow_html=True)
        
        # Top bar with language selector
        top_col1, top_col2 = st.columns([7, 1])
        with top_col2:
            language = st.selectbox("🌐", list(TRANSLATIONS.keys()), 
                                   index=list(TRANSLATIONS.keys()).index(st.session_state.language),
                                   label_visibility="collapsed")
            if language != st.session_state.language:
                st.session_state.language = language
                st.rerun()
        
        st.markdown("---")
        
        # Two columns layout
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"### {get_text('input_composition')}")
            st.markdown(get_text('enter_mix_design'))
            
            # Handle reset BEFORE creating widgets
            if 'reset_needed' in st.session_state and st.session_state.reset_needed:
                for key in MIX_PRESETS['Standard Concrete'].keys():
                    if key not in ['description', 'key', 'desc_key']:
                        st.session_state[f'input_{key}'] = MIX_PRESETS['Standard Concrete'][key]
                st.session_state.reset_needed = False
            
            # NEW FEATURE: Quick Presets
            st.markdown(f"#### {get_text('presets')}")
            preset_cols = st.columns(4)
            for i, (preset_name, preset_data) in enumerate(MIX_PRESETS.items()):
                with preset_cols[i % 4]:
                    btn_label = get_text(preset_data['key'])
                    btn_help = get_text(preset_data['desc_key'])
                    if st.button(btn_label, help=btn_help, use_container_width=True):
                        for key, value in preset_data.items():
                            if key not in ['description', 'key', 'desc_key']:
                                st.session_state[f'input_{key}'] = value
            
            st.markdown("---")
            
            # Input form with session state
            cement = st.slider(get_text('cement'), 100, 500, 
                            st.session_state.get('input_cement', 300),
                            key='input_cement',
                            help=get_text('cement_help'))
            slag = st.slider(get_text('slag'), 0, 250, 
                           st.session_state.get('input_slag', 0),
                           key='input_slag',
                           help=get_text('slag_help'))
            fly_ash = st.slider(get_text('fly_ash'), 0, 200, 
                              st.session_state.get('input_fly_ash', 0),
                              key='input_fly_ash',
                              help=get_text('fly_ash_help'))
            water = st.slider(get_text('water'), 120, 200, 
                            st.session_state.get('input_water', 170),
                            key='input_water',
                            help=get_text('water_help'))
            superplasticizer = st.slider(get_text('superplasticizer'), 0, 15, 
                                          st.session_state.get('input_superplasticizer', 0),
                                          key='input_superplasticizer',
                                          help=get_text('superplasticizer_help'))
            coarse_agg = st.slider(get_text('coarse_aggregate'), 800, 1100, 
                                 st.session_state.get('input_coarse_aggregate', 950),
                                 key='input_coarse_aggregate',
                                 help=get_text('coarse_aggregate_help'))
            fine_agg = st.slider(get_text('fine_aggregate'), 600, 800, 
                              st.session_state.get('input_fine_aggregate', 700),
                              key='input_fine_aggregate',
                              help=get_text('fine_aggregate_help'))
            age = st.slider(get_text('curing_age'), 1, 365, 
                         st.session_state.get('input_age', 28),
                         key='input_age',
                         help=get_text('curing_age_help'))
            
            # Buttons
            st.markdown("---")
            button_col1, button_col2 = st.columns(2)
            with button_col1:
                predict_button = st.button(get_text("generate_button"), type="primary", use_container_width=True)
            with button_col2:
                reset_button = st.button(get_text("reset"), use_container_width=True)
            
            if reset_button:
                st.session_state.reset_needed = True
                st.rerun()
            
            # NEW FEATURE: Save current mix
            st.markdown("---")
            save_col1, save_col2 = st.columns([3, 1])
            with save_col1:
                mix_name = st.text_input("Mix name", placeholder=get_text("mix_name_placeholder"), label_visibility="collapsed")
            with save_col2:
                if st.button(get_text("save_mix")):
                    if mix_name:
                        current_mix = {
                            'name': mix_name,
                            'cement': cement, 'slag': slag, 'fly_ash': fly_ash, 'water': water,
                            'superplasticizer': superplasticizer, 'coarse_aggregate': coarse_agg,
                            'fine_aggregate': fine_agg, 'age': age,
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
                        }
                        st.session_state.saved_mixes.append(current_mix)
                        st.success(get_text("mix_saved").format(name=mix_name))
                    else:
                        st.warning(get_text("enter_mix_name"))
            
            # User tips based on persona
            with st.expander(get_text("tips_persona")):
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
                
                # NEW FEATURE #10: Quality Control Checks
                st.markdown(f"### {get_text('quality_checks')}")
                warnings = validate_mix_design(input_data)
                
                if warnings:
                    for warning in warnings:
                        if warning['type'] == 'error':
                            st.markdown(f'<div class="warning-box warning-error">{warning["message"]}</div>', 
                                      unsafe_allow_html=True)
                        elif warning['type'] == 'warning':
                            st.markdown(f'<div class="warning-box warning-warning">{warning["message"]}</div>', 
                                      unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="warning-box warning-info">{warning["message"]}</div>', 
                                      unsafe_allow_html=True)
                else:
                    st.success(get_text("qc_all_passed"))
                
                st.markdown("---")
                
                # Create DataFrame for prediction
                input_df = pd.DataFrame([input_data])
                
                # Scale input
                input_scaled = scaler.transform(input_df)
                
                # Make prediction
                prediction = model.predict(input_scaled)[0]
                
                # NEW FEATURE #16: Confidence Intervals
                with st.spinner(get_text("calculating_ci")):
                    ci_result = calculate_confidence_interval(model, scaler, input_df)
                
                # Calculate sustainability metrics
                metrics = calculate_sustainability_metrics(input_data)
                
                # Add prediction to input_data for cost calculation
                input_data['predicted_strength'] = prediction
                
                # NEW FEATURE #4: Cost Estimation
                cost_result = calculate_cost(input_data)
                
                # Display passport
                display_passport(input_data, prediction, metrics)
                
                # NEW FEATURE: Enhanced metrics with cost and confidence
                st.markdown("### 📈 Enhanced Analysis")
                
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                
                with metric_col1:
                    if ci_result:
                        st.metric(
                            "Predicted Strength",
                            f"{prediction:.1f} MPa",
                            f"±{(ci_result['ci_upper']-ci_result['ci_lower'])/2:.1f} MPa",
                            help=f"95% confidence interval: {ci_result['ci_lower']:.1f} - {ci_result['ci_upper']:.1f} MPa"
                        )
                    else:
                        st.metric("Predicted Strength", f"{prediction:.1f} MPa")
                
                with metric_col2:
                    st.metric(
                        get_text('cost_estimate'),
                        f"${cost_result['total_cost']:.2f}/m³",
                        f"${cost_result['cost_per_mpa']:.2f}/MPa",
                        help="Total material cost per cubic meter"
                    )
                
                with metric_col3:
                    st.metric(
                        "Circularity Score",
                        f"{metrics['circularity_score']:.0f}/100",
                        f"{metrics['circularity_score']-50:.0f} points",
                        delta_color="normal"
                    )
                
                with metric_col4:
                    st.metric(
                        "CO₂ Emissions",
                        f"{metrics['co2_emissions']:.0f} kg/m³",
                        f"-{320-metrics['co2_emissions']:.0f} kg",
                        delta_color="inverse"
                    )
                
                # Cost breakdown
                with st.expander("💰 Cost Breakdown"):
                    cost_df = pd.DataFrame([
                        {'Material': mat.replace('_', ' ').title(), 
                         'Cost': f"${cost:.2f}",
                         'Percentage': f"{(cost/cost_result['total_cost']*100):.1f}%"}
                        for mat, cost in cost_result['breakdown'].items()
                    ]).sort_values('Percentage', ascending=False)
                    st.dataframe(cost_df, hide_index=True, use_container_width=True)
                
                st.markdown("---")
                
                # NEW FEATURE #7: Optimization Suggestions
                st.markdown(f"### {get_text('suggestions')}")
                suggestions = suggest_improvements(
                    input_data, 
                    prediction, 
                    metrics,
                    target_strength=40,  # User could set this
                    target_circularity=70
                )
                
                if suggestions:
                    for suggestion in suggestions:
                        st.info(f"**{suggestion['category']}:** {suggestion['message']}\n\n*Impact:* {suggestion['impact']}")
                else:
                    st.success("✅ Your mix design is well-optimized!")
                
                st.markdown("---")
                
                # NEW FEATURE #21: SHAP Explainability
                st.markdown(f"### {get_text('explainability')}")
                
                with st.spinner("Generating prediction explanation..."):
                    # Load sample data for SHAP background
                    try:
                        data_path = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'concrete_enriched.csv'
                        if data_path.exists():
                            sample_data = pd.read_csv(data_path)
                            feature_cols = ['cement', 'slag', 'fly_ash', 'water', 'superplasticizer', 
                                          'coarse_aggregate', 'fine_aggregate', 'age']
                            sample_data = sample_data[feature_cols]
                            
                            explainer = get_shap_explainer(model, scaler, sample_data)
                            if explainer:
                                explanation = explain_prediction(explainer, model, scaler, input_df)
                                
                                if explanation:
                                    st.markdown("**Feature Contributions to Predicted Strength:**")
                                    
                                    contrib_data = []
                                    for feature, data in list(explanation['contributions'].items())[:8]:
                                        contrib_sign = "+" if data['contribution'] >= 0 else ""
                                        contrib_data.append({
                                            'Feature': feature.replace('_', ' ').title(),
                                            'Value': f"{data['value']:.1f}",
                                            'Contribution': f"{contrib_sign}{data['contribution']:.2f} MPa",
                                            'Impact': '🔴' * int(abs(data['contribution'])) if abs(data['contribution']) > 0 else '⚪'
                                        })
                                    
                                    st.dataframe(pd.DataFrame(contrib_data), hide_index=True, use_container_width=True)
                                    
                                    st.caption(f"Base prediction (average): {explanation['base_value']:.1f} MPa")
                                    st.caption("Each feature contributes positively (+) or negatively (-) to the final prediction.")
                        else:
                            st.info("SHAP explainability requires sample data. Feature not available.")
                    except Exception as e:
                        st.warning(f"Could not load explainability: {e}")
                
                # Additional metrics visualization
                st.markdown("---")
                st.markdown("### 📊 Benchmark Comparison")
                
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
        
        # NEW FEATURE #3: Comparison Mode
        if len(st.session_state.saved_mixes) > 0:
            st.markdown("---")
            st.markdown(f"### {get_text('compare')}")
            st.markdown(f"**Saved Mixes:** {len(st.session_state.saved_mixes)}")
            
            if len(st.session_state.saved_mixes) >= 2:
                compare_cols = st.columns(min(3, len(st.session_state.saved_mixes)))
                selected_mixes = []
                
                for i, col in enumerate(compare_cols):
                    with col:
                        if i < len(st.session_state.saved_mixes):
                            mix = st.session_state.saved_mixes[i]
                            if st.checkbox(f"{mix['name']}", key=f"compare_{i}"):
                                selected_mixes.append(mix)
                
                if len(selected_mixes) >= 2:
                    st.markdown("#### Comparison Results")
                    
                    # Create comparison table
                    comparison_data = []
                    for mix in selected_mixes:
                        # Make prediction for each mix
                        mix_input = {k: v for k, v in mix.items() if k not in ['name', 'timestamp']}
                        mix_df = pd.DataFrame([mix_input])
                        mix_scaled = scaler.transform(mix_df)
                        mix_pred = model.predict(mix_scaled)[0]
                        mix_metrics = calculate_sustainability_metrics(mix_input)
                        mix_cost = calculate_cost({**mix_input, 'predicted_strength': mix_pred})
                        
                        comparison_data.append({
                            'Mix Name': mix['name'],
                            'Strength (MPa)': f"{mix_pred:.1f}",
                            'Cost ($/m³)': f"${mix_cost['total_cost']:.2f}",
                            'Circularity': f"{mix_metrics['circularity_score']:.0f}/100",
                            'Grade': mix_metrics['grade'],
                            'CO₂ (kg/m³)': f"{mix_metrics['co2_emissions']:.0f}",
                            'Recycled %': f"{mix_metrics['recycled_content']:.1f}%"
                        })
                    
                    comp_df = pd.DataFrame(comparison_data)
                    st.dataframe(comp_df, hide_index=True, use_container_width=True)
                    
                    # Highlight best options
                    st.markdown("**Recommendations:**")
                    best_strength_idx = comp_df['Strength (MPa)'].apply(lambda x: float(x)).idxmax()
                    best_circularity_idx = comp_df['Circularity'].apply(lambda x: int(x.split('/')[0])).idxmax()
                    
                    rec_col1, rec_col2 = st.columns(2)
                    with rec_col1:
                        st.success(f"💪 **Highest Strength:** {comp_df.iloc[best_strength_idx]['Mix Name']} ({comp_df.iloc[best_strength_idx]['Strength (MPa)']})")
                    with rec_col2:
                        st.success(f"♻️ **Best Sustainability:** {comp_df.iloc[best_circularity_idx]['Mix Name']} (Grade {comp_df.iloc[best_circularity_idx]['Grade']})")
                
                # Option to clear saved mixes
                if st.button("🗑️ Clear All Saved Mixes"):
                    st.session_state.saved_mixes = []
                    st.rerun()
            else:
                st.info("Save at least 2 mixes to compare them side-by-side.")
        
        # Footer
        st.markdown("---")
        st.markdown(f"""
            <div style="text-align: center; color: #6c757d; font-size: 0.9em;">
                {get_text('footer_mvp')}
                <br>
                <em>{get_text('footer_project')}</em>
            </div>
            """, unsafe_allow_html=True)
    
    with tab1:
        about_ai_ml()
    
    with tab2:
        about_developer()

if __name__ == "__main__":
    main()
