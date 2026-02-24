"""
Prediction history endpoints — persists and retrieves prediction logs from DB.
"""
from flask import Blueprint, request, jsonify
from ..extensions import db
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
        'predictions': [p.to_dict() for p in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
    })


@history_bp.route('/history/<int:prediction_id>', methods=['DELETE'])
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
      404:
        description: Prediction not found
    """
    prediction = db.session.get(PredictionLog, prediction_id)
    if not prediction:
        return jsonify({'success': False, 'error': 'Prediction not found'}), 404

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
    total = PredictionLog.query.count()

    stats_by_disease = {}
    for disease in ['heart', 'diabetes', 'kidney', 'depression']:
        disease_count = PredictionLog.query.filter_by(disease_type=disease).count()
        high_risk = PredictionLog.query.filter_by(
            disease_type=disease, risk_level='High'
        ).count()
        stats_by_disease[disease] = {
            'total': disease_count,
            'high_risk': high_risk,
            'low_risk': disease_count - high_risk,
        }

    return jsonify({
        'success': True,
        'total_predictions': total,
        'by_disease': stats_by_disease,
    })
