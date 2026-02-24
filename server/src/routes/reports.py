"""
PDF Report generation endpoint.
"""
from flask import Blueprint, request, jsonify, send_file
from ..extensions import limiter

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/reports/generate', methods=['POST'])
@limiter.limit("5 per minute")
def generate_report():
    """Generate a PDF report from prediction data.
    ---
    tags:
      - Reports
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - disease
            - risk_level
            - confidence
            - advice
          properties:
            disease:
              type: string
              example: heart
            risk_level:
              type: string
              example: High
            confidence:
              type: number
              example: 0.87
            prediction:
              type: integer
              example: 1
            advice:
              type: string
              example: "Consult a cardiologist."
            shap_contributions:
              type: array
              items:
                type: object
    responses:
      200:
        description: PDF file
        content:
          application/pdf:
            schema:
              type: string
              format: binary
      400:
        description: Missing required fields
      503:
        description: PDF generation not available
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Missing request body'}), 400

    required = ['disease', 'risk_level', 'advice']
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({
            'success': False,
            'error': f'Missing required fields: {", ".join(missing)}'
        }), 400

    from ..services.report_service import generate_pdf_report

    pdf_buffer = generate_pdf_report(data)
    if pdf_buffer is None:
        return jsonify({
            'success': False,
            'error': 'PDF generation is not available. Install reportlab: pip install reportlab'
        }), 503

    disease = data.get('disease', 'assessment')
    filename = f'health_report_{disease}.pdf'

    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename,
    )
