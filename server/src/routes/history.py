"""
Prediction history endpoints — persists and retrieves prediction logs from DB.
"""
from flask import Blueprint, request, jsonify
from ..extensions import db, limiter
from ..models import PredictionLog

history_bp = Blueprint('history', __name__)


@history_bp.route('/history', methods=['GET'])
def get_history():
    """Get prediction history (paginated).
    ---
    tags:
      - History
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
      - name: per_page
        in: query
        type: integer
        default: 20
      - name: disease
        in: query
        type: string
        description: Filter by disease type (heart, diabetes, kidney, depression)
    responses:
      200:
        description: Paginated prediction history
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    disease = request.args.get('disease', None, type=str)

    query = PredictionLog.query.order_by(PredictionLog.created_at.desc())

    if disease:
        query = query.filter_by(disease_type=disease)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'success': True,
        'predictions': [
            p.to_dict(include_input_data=False, include_shap_contributions=False)
            for p in pagination.items
        ],
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
    })


@history_bp.route('/history/<int:prediction_id>', methods=['DELETE'])
@limiter.limit("5 per minute")
def delete_prediction(prediction_id):
    """Delete a specific prediction record.
    ---
    tags:
      - History
    parameters:
      - name: prediction_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Prediction deleted successfully
      403:
        description: Unauthorized — IP mismatch
      404:
        description: Prediction not found
    """
    prediction = db.session.get(PredictionLog, prediction_id)
    if not prediction:
        return jsonify({'success': False, 'error': 'Prediction not found'}), 404

    # Basic ownership check: only the IP that created it can delete it
    if prediction.ip_address and prediction.ip_address != request.remote_addr:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    db.session.delete(prediction)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Prediction deleted'})


@history_bp.route('/history/stats', methods=['GET'])
def get_stats():
    """Get aggregate stats on prediction history.
    ---
    tags:
      - History
    responses:
      200:
        description: Prediction statistics
    """
    from sqlalchemy import func

    total = PredictionLog.query.count()

    # Single GROUP BY query instead of 8 separate COUNT queries
    rows = db.session.query(
        PredictionLog.disease_type,
        PredictionLog.risk_level,
        func.count(PredictionLog.id)
    ).group_by(PredictionLog.disease_type, PredictionLog.risk_level).all()

    stats_by_disease = {}
    for disease in ['heart', 'diabetes', 'kidney', 'depression']:
        stats_by_disease[disease] = {'total': 0, 'high_risk': 0, 'low_risk': 0}

    for disease_type, risk_level, count in rows:
        if disease_type in stats_by_disease:
            stats_by_disease[disease_type]['total'] += count
            if risk_level == 'High':
                stats_by_disease[disease_type]['high_risk'] = count
            elif risk_level == 'Low':
                stats_by_disease[disease_type]['low_risk'] = count

    return jsonify({
        'success': True,
        'total_predictions': total,
        'by_disease': stats_by_disease,
    })

