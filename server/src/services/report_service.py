"""
PDF Report Generation Service.

Generates professional medical-style PDF reports from prediction results
using ReportLab for layout and Matplotlib for charts.
"""
import io
import logging
from datetime import datetime, timezone

logger = logging.getLogger('api')

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    _REPORTLAB_AVAILABLE = True
except ImportError:
    _REPORTLAB_AVAILABLE = False
    logger.warning("⚠️  reportlab not installed — PDF reports disabled.")

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    _MATPLOTLIB_AVAILABLE = True
except ImportError:
    _MATPLOTLIB_AVAILABLE = False
    logger.warning("⚠️  matplotlib not installed — charts in PDF reports disabled.")


DISEASE_NAMES = {
    'heart': 'Heart Disease',
    'diabetes': 'Diabetes',
    'kidney': 'Chronic Kidney Disease',
    'depression': 'Depression',
}

RISK_COLORS = {
    'High': '#ef4444',
    'Low': '#22c55e',
}


def _create_risk_gauge(risk_level, confidence):
    """Create a simple risk gauge chart and return as bytes."""
    if not _MATPLOTLIB_AVAILABLE:
        return None

    fig, ax = plt.subplots(figsize=(3, 1.5))
    color = RISK_COLORS.get(risk_level, '#6366f1')
    conf_pct = confidence * 100 if confidence else 50

    ax.barh(['Risk'], [conf_pct], color=color, height=0.4, alpha=0.85)
    ax.barh(['Risk'], [100 - conf_pct], left=[conf_pct], color='#e5e7eb', height=0.4)
    ax.set_xlim(0, 100)
    ax.set_xlabel('Confidence %')
    ax.set_title(f'{risk_level} Risk', fontsize=12, fontweight='bold', color=color)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf


def _create_shap_chart(contributions):
    """Create a SHAP contribution bar chart and return as bytes."""
    if not _MATPLOTLIB_AVAILABLE or not contributions:
        return None

    features = [c['feature'] for c in contributions]
    values = [c['contribution'] for c in contributions]
    colors = ['#ef4444' if c['direction'] == 'risk' else '#22c55e' for c in contributions]

    fig, ax = plt.subplots(figsize=(4, 2))
    ax.barh(features, values, color=colors, height=0.5)
    ax.set_xlabel('SHAP Value (impact on prediction)')
    ax.set_title('Top Feature Contributions', fontsize=11, fontweight='bold')
    ax.invert_yaxis()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf


def generate_pdf_report(prediction_data):
    """Generate a professional medical-style PDF report.

    Args:
        prediction_data: dict with keys: disease, risk_level, confidence,
                         prediction, advice, shap_contributions (optional)

    Returns:
        BytesIO containing the PDF bytes, or None if reportlab is unavailable.
    """
    if not _REPORTLAB_AVAILABLE:
        return None

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=20 * mm, bottomMargin=20 * mm,
        leftMargin=20 * mm, rightMargin=20 * mm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'ReportTitle', parent=styles['Title'],
        fontSize=22, textColor=HexColor('#1a1a2e'),
        spaceAfter=6 * mm,
    )
    subtitle_style = ParagraphStyle(
        'ReportSubtitle', parent=styles['Normal'],
        fontSize=10, textColor=HexColor('#64748b'),
        alignment=TA_CENTER, spaceAfter=10 * mm,
    )
    heading_style = ParagraphStyle(
        'SectionHeading', parent=styles['Heading2'],
        fontSize=14, textColor=HexColor('#334155'),
        spaceBefore=8 * mm, spaceAfter=4 * mm,
    )
    body_style = ParagraphStyle(
        'ReportBody', parent=styles['Normal'],
        fontSize=11, leading=16, textColor=HexColor('#1e293b'),
    )
    disclaimer_style = ParagraphStyle(
        'Disclaimer', parent=styles['Normal'],
        fontSize=8, textColor=HexColor('#94a3b8'),
        alignment=TA_CENTER, spaceBefore=15 * mm,
    )

    disease = prediction_data.get('disease', 'Unknown')
    disease_name = DISEASE_NAMES.get(disease, disease)
    risk_level = prediction_data.get('risk_level', 'Unknown')
    confidence = prediction_data.get('confidence', 0)
    advice = prediction_data.get('advice', 'No advice available.')
    shap_data = prediction_data.get('shap_contributions', [])

    now = datetime.now(timezone.utc).strftime('%B %d, %Y at %H:%M UTC')
    risk_color = RISK_COLORS.get(risk_level, '#6366f1')

    elements = []

    # ── Header ──────────────────────────────────────────────────────────────
    elements.append(Paragraph('🏥 Health Risk Assessment Report', title_style))
    elements.append(Paragraph(f'Generated on {now}', subtitle_style))
    elements.append(Spacer(1, 4 * mm))

    # ── Summary Table ───────────────────────────────────────────────────────
    elements.append(Paragraph('Assessment Summary', heading_style))

    summary_data = [
        ['Disease Screened', disease_name],
        ['Risk Level', risk_level],
        ['Confidence', f'{confidence * 100:.1f}%' if confidence else 'N/A'],
    ]
    summary_table = Table(summary_data, colWidths=[60 * mm, 100 * mm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#475569')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (1, 1), (1, 1), HexColor(risk_color)),
        ('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e2e8f0')),
    ]))
    elements.append(summary_table)

    # ── Risk Gauge ──────────────────────────────────────────────────────────
    gauge_buf = _create_risk_gauge(risk_level, confidence)
    if gauge_buf:
        elements.append(Spacer(1, 6 * mm))
        elements.append(Image(gauge_buf, width=120 * mm, height=60 * mm))

    # ── SHAP Contributions ─────────────────────────────────────────────────
    if shap_data:
        elements.append(Paragraph('Key Contributing Factors', heading_style))
        shap_buf = _create_shap_chart(shap_data)
        if shap_buf:
            elements.append(Image(shap_buf, width=140 * mm, height=70 * mm))
        else:
            for item in shap_data:
                direction = '↑ Risk' if item.get('direction') == 'risk' else '↓ Protective'
                elements.append(Paragraph(
                    f"• <b>{item['feature']}</b>: {direction} ({item.get('pct', 0):.0f}%)",
                    body_style,
                ))

    # ── Recommendations ─────────────────────────────────────────────────────
    elements.append(Paragraph('Medical Recommendations', heading_style))
    elements.append(Paragraph(advice, body_style))

    # ── Disclaimer ──────────────────────────────────────────────────────────
    elements.append(Paragraph(
        'DISCLAIMER: This report is generated by an AI-based screening tool and '
        'is NOT a medical diagnosis. Always consult a qualified healthcare '
        'professional for medical advice, diagnosis, or treatment.',
        disclaimer_style,
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer
