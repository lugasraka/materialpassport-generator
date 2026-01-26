"""
PDF generation using ReportLab.
"""
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from io import BytesIO
from typing import Dict

def generate_passport_pdf(passport: Dict) -> bytes:
    """
    Generate PDF document from passport data.
    
    Args:
        passport: Passport dictionary with all passport data
    
    Returns:
        PDF document as bytes
    """
    try:
        # Create PDF with ReportLab
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        doc.pagesize = letter
        width, height = letter
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        heading_style = styles['Heading2']
        normal_style = styles['Normal']
        
        # Add title
        doc.build([
            Paragraph("Digital Material Passport", title_style),
            Spacer(1, 12),
        ])
        
        # Add passport ID and date
        doc.build([
            Paragraph(f"Passport ID: {passport['id']}", normal_style),
            Paragraph(f"Generated: {passport['generated_at']}", normal_style),
            Spacer(1, 12),
        ])
        
        # Add material type
        doc.build([
            Paragraph("Material Type", heading_style),
            Paragraph(passport['material_type'], normal_style),
            Spacer(1, 12),
        ])
        
        # Add material composition table
        doc.build([
            Paragraph("Material Composition", heading_style),
            Spacer(1, 6),
            Table([
                ["Material", "Amount", "Unit"],
                [
                    ["Cement", f"{passport['composition']['cement']:.2f}", "kg/m³"],
                    ["Blast Furnace Slag", f"{passport['composition']['blast_furnace_slag']:.2f}", "kg/m³"],
                    ["Fly Ash", f"{passport['composition']['fly_ash']:.2f}", "kg/m³"],
                    ["Water", f"{passport['composition']['water']:.2f}", "kg/m³"],
                    ["Superplasticizer", f"{passport['composition']['superplasticizer']:.2f}", "kg/m³"],
                    ["Coarse Aggregate", f"{passport['composition']['coarse_aggregate']:.2f}", "kg/m³"],
                    ["Fine Aggregate", f"{passport['composition']['fine_aggregate']:.2f}", "kg/m³"],
                    ["Age", f"{passport['composition']['age']} days"],
                ]
            ],
            Spacer(1, 12),
        ])
        
        # Add predictions
        doc.build([
            Paragraph("Predictions", heading_style),
            Spacer(1, 6),
        ])
        
        # Strength prediction
        strength = passport['predictions']['compressive_strength']
        doc.build([
            Paragraph("Compressive Strength", heading_style),
            Paragraph(f"{strength['value']:.2f} {strength['unit']}", normal_style),
            Paragraph(f"Model: {strength['model']}", normal_style),
            Paragraph(f"Confidence: {strength['confidence']:.0%}", normal_style),
            Spacer(1, 12),
        ])
        
        # Recyclability
        recyclability = passport['predictions']['recyclability']
        doc.build([
            Paragraph("Recyclability Score", heading_style),
            Paragraph(f"{recyclability['score']}/100", normal_style),
            Paragraph(f"Grade: {recyclability['grade']}", normal_style),
            Paragraph(f"Model: {recyclability['model']}", normal_style),
            Spacer(1, 12),
        ])
        
        # Add sustainability metrics
        doc.build([
            Paragraph("Sustainability Metrics", heading_style),
            Spacer(1, 6),
        ])
        
        # Circularity score
        circularity = passport['sustainability_metrics']['circularity_score']
        doc.build([
            Paragraph("Circularity Score", heading_style),
            Paragraph(f"{circularity}/100", normal_style),
            Spacer(1, 12),
        ])
        
        # CO2 emissions
        co2 = passport['sustainability_metrics']['co2_emissions']
        doc.build([
            Paragraph("CO2 Emissions", heading_style),
            Paragraph(f"{co2['value']:.2f} {co2['unit']}", normal_style),
            Spacer(1, 12),
        ])
        
        # Recycled content
        recycled = passport['sustainability_metrics']['recycled_content']
        doc.build([
            Paragraph("Recycled Content", heading_style),
            Paragraph(f"{recycled['percentage']:.1f}%", normal_style),
            Paragraph(f"Materials: {', '.join(recycled['materials'])}", normal_style),
            Spacer(1, 12),
        ])
        
        # Sustainability grade
        grade = passport['sustainability_metrics']['sustainability_grade']
        doc.build([
            Paragraph("Sustainability Grade", heading_style),
            Paragraph(grade, normal_style),
            Spacer(1, 12),
        ])
        
        # Add certification
        doc.build([
            Paragraph("Certification", heading_style),
            Paragraph(passport['certification'], normal_style),
            Spacer(1, 24),
        ])
        
        # Add footer
        doc.build([
            Paragraph("Generated by Material Passport Generator", styles['Normal']),
            Paragraph("https://material-passport.app", styles['Normal']),
        ])
        
        print(f"✓ Generated PDF for passport: {passport['id']}")
        return buffer.getvalue()
        
    except Exception as e:
        print(f"✗ Error generating PDF: {e}")
        raise
