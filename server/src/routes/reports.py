"""
PDF Report generation endpoint.
"""
import re
from flask import Blueprint, request, jsonify, send_file
from ..extensions import limiter

reports_bp = Blueprint('reports', __name__)

_MAX_ADVICE_CHARS = 800
_MAX_SHAP_ITEMS = 10


def _strip_tags(text: str) -> str:
    if not text:
        return ""
    # ReportLab Paragraph supports a markup subset; strip tags to avoid injection.
    return re.sub(r"<[^>]*?>", "", str(text))


def _validate_shap_contributions(value):
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("shap_contributions must be an array")
    cleaned = []
    for item in value[:_MAX_SHAP_ITEMS]:
        if not isinstance(item, dict):
            continue
        feature = item.get("feature")
        direction = item.get("direction")
        pct = item.get("pct")
        contribution = item.get("contribution")
        if not isinstance(feature, str) or not feature.strip():
            continue
        if direction not in ("risk", "protective"):
            continue
        try:
            pct_f = float(pct)
            contrib_f = float(contribution)
        except (TypeError, ValueError):
            continue
        cleaned.append(
            {
                "feature": feature.strip()[:64],
                "direction": direction,
                "pct": max(0.0, min(100.0, round(pct_f, 1))),
                "contribution": round(contrib_f, 6),
            }
        )
    return cleaned


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

    # Validate/sanitize fields (server-authoritative)
    from ..constants import DISEASES
    allowed_disease_keys = set(DISEASES.keys())
    allowed_disease_names = {v.get("name") for v in DISEASES.values() if isinstance(v, dict)}
    allowed_disease_names = {n for n in allowed_disease_names if isinstance(n, str) and n.strip()}

    disease = str(data.get("disease", "")).strip()
    if disease not in allowed_disease_keys and disease not in allowed_disease_names:
        return jsonify({'success': False, 'error': 'Invalid disease'}), 400

    risk_level = str(data.get("risk_level", "")).strip()
    if risk_level not in ("Low", "High"):
        return jsonify({'success': False, 'error': 'Invalid risk_level (expected Low/High)'}), 400

    confidence = data.get("confidence", None)
    if confidence is not None:
        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            return jsonify({'success': False, 'error': 'Invalid confidence'}), 400
        confidence = max(0.0, min(100.0, confidence))

    advice = _strip_tags(data.get("advice", ""))
    advice = re.sub(r"\s+", " ", advice).strip()
    if not advice:
        return jsonify({'success': False, 'error': 'Advice is required'}), 400
    advice = advice[:_MAX_ADVICE_CHARS]

    try:
        shap_contributions = _validate_shap_contributions(data.get("shap_contributions"))
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400

    sanitized_payload = {
        "disease": disease,
        "risk_level": risk_level,
        "confidence": confidence,
        "prediction": data.get("prediction"),
        "advice": advice,
        "shap_contributions": shap_contributions,
    }

    from ..services.report_service import generate_pdf_report

    pdf_buffer = generate_pdf_report(sanitized_payload)
    if pdf_buffer is None:
        return jsonify({
            'success': False,
            'error': 'PDF generation is not available. Install reportlab: pip install reportlab'
        }), 503

    safe_name = re.sub(r"[^a-zA-Z0-9_-]+", "_", disease)[:64] or "assessment"
    filename = f'health_report_{safe_name}.pdf'

    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename,
    )
