from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from ..services.model_service import model_service
from ..schemas import HeartPredictionSchema, DiabetesPredictionSchema, ParkinsonsPredictionSchema
from ..extensions import limiter

predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/predict/heart', methods=['POST'])
@limiter.limit("10 per minute")
def predict_heart():
    """Predict heart disease"""
    try:
        data = HeartPredictionSchema().load(request.json or {})
    except ValidationError as err:
        return jsonify({'success': False, 'error': err.messages}), 400
        
    response, status_code = model_service.predict('heart', data)
    return jsonify(response), status_code

@predict_bp.route('/predict/diabetes', methods=['POST'])
@limiter.limit("10 per minute")
def predict_diabetes():
    """Predict diabetes"""
    try:
        data = DiabetesPredictionSchema().load(request.json or {})
    except ValidationError as err:
        return jsonify({'success': False, 'error': err.messages}), 400

    response, status_code = model_service.predict('diabetes', data)
    return jsonify(response), status_code

@predict_bp.route('/predict/parkinsons', methods=['POST'])
@limiter.limit("10 per minute")
def predict_parkinsons():
    """Predict Parkinson's disease"""
    try:
        data = ParkinsonsPredictionSchema().load(request.json or {})
    except ValidationError as err:
        return jsonify({'success': False, 'error': err.messages}), 400

    response, status_code = model_service.predict('parkinsons', data)
    return jsonify(response), status_code

@predict_bp.route('/diseases', methods=['GET'])
def get_diseases():
    """Get list of available diseases"""
    return jsonify({
        'diseases': [
            {
                'id': 'heart',
                'name': 'Heart Disease',
                'description': 'Predict cardiovascular disease risk',
                'icon': '❤️'
            },
            {
                'id': 'diabetes',
                'name': 'Diabetes',
                'description': 'Predict diabetes risk',
                'icon': '🩺'
            },
            {
                'id': 'parkinsons',
                'name': "Parkinson's Disease",
                'description': 'Predict Parkinson\'s disease risk',
                'icon': '🧠'
            }
        ]
    })
