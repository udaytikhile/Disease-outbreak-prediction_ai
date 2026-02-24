from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from ..services.model_service import model_service
from ..schemas import (
    HeartPredictionSchema,
    DiabetesPredictionSchema,
    KidneyPredictionSchema,
    DepressionPredictionSchema,
)
from ..extensions import limiter, db, logger
from ..models import PredictionLog

predict_bp = Blueprint('predict', __name__)


def _log_prediction(disease_type, input_data, response_data):
    """Persist prediction result to database."""
    try:
        log = PredictionLog(
            disease_type=disease_type,
            input_data=input_data,
            prediction=response_data.get('prediction', 0),
            risk_level=response_data.get('risk_level', 'Unknown'),
            confidence=response_data.get('confidence'),
            advice=response_data.get('advice', ''),
            shap_contributions=response_data.get('shap_contributions'),
            ip_address=request.remote_addr,
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        logger.warning(f"Failed to log prediction: {e}")
        db.session.rollback()


@predict_bp.route('/predict/heart', methods=['POST'])
@limiter.limit("10 per minute")
def predict_heart():
    """Predict heart disease risk.
    ---
    tags:
      - Predictions
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            age: { type: number, example: 45 }
            sex: { type: string, example: "Male" }
            cp: { type: string, example: "asymptomatic" }
            trestbps: { type: number, example: 120 }
            chol: { type: number, example: 200 }
            fbs: { type: string, example: "FALSE" }
            restecg: { type: string, example: "normal" }
            thalch: { type: number, example: 150 }
            exang: { type: string, example: "FALSE" }
            oldpeak: { type: number, example: 1.0 }
            slope: { type: string, example: "flat" }
            ca: { type: number, example: 0 }
            thal: { type: string, example: "normal" }
    responses:
      200:
        description: Prediction result
      400:
        description: Validation error
    """
    try:
        data = HeartPredictionSchema().load(request.json or {})
    except ValidationError as err:
        return jsonify({'success': False, 'error': err.messages}), 400

    response, status_code = model_service.predict('heart', data)
    if response.get('success'):
        _log_prediction('heart', data, response)
    return jsonify(response), status_code


@predict_bp.route('/predict/diabetes', methods=['POST'])
@limiter.limit("10 per minute")
def predict_diabetes():
    """Predict diabetes risk.
    ---
    tags:
      - Predictions
    consumes:
      - application/json
    responses:
      200:
        description: Prediction result
      400:
        description: Validation error
    """
    try:
        data = DiabetesPredictionSchema().load(request.json or {})
    except ValidationError as err:
        return jsonify({'success': False, 'error': err.messages}), 400

    response, status_code = model_service.predict('diabetes', data)
    if response.get('success'):
        _log_prediction('diabetes', data, response)
    return jsonify(response), status_code


@predict_bp.route('/predict/kidney', methods=['POST'])
@limiter.limit("10 per minute")
def predict_kidney():
    """Predict chronic kidney disease risk.
    ---
    tags:
      - Predictions
    consumes:
      - application/json
    responses:
      200:
        description: Prediction result
      400:
        description: Validation error
    """
    try:
        data = KidneyPredictionSchema().load(request.json or {})
    except ValidationError as err:
        return jsonify({'success': False, 'error': err.messages}), 400

    response, status_code = model_service.predict('kidney', data)
    if response.get('success'):
        _log_prediction('kidney', data, response)
    return jsonify(response), status_code


@predict_bp.route('/predict/depression', methods=['POST'])
@limiter.limit("10 per minute")
def predict_depression():
    """Predict depression risk.
    ---
    tags:
      - Predictions
    consumes:
      - application/json
    responses:
      200:
        description: Prediction result
      400:
        description: Validation error
    """
    try:
        data = DepressionPredictionSchema().load(request.json or {})
    except ValidationError as err:
        return jsonify({'success': False, 'error': err.messages}), 400

    response, status_code = model_service.predict('depression', data)
    if response.get('success'):
        _log_prediction('depression', data, response)
    return jsonify(response), status_code


@predict_bp.route('/diseases', methods=['GET'])
def get_diseases():
    """Get list of available diseases.
    ---
    tags:
      - Predictions
    responses:
      200:
        description: List of supported disease models
    """
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
                'id': 'kidney',
                'name': 'Chronic Kidney Disease',
                'description': 'Predict chronic kidney disease risk',
                'icon': '🫘'
            },
            {
                'id': 'depression',
                'name': 'Depression',
                'description': 'Predict depression risk',
                'icon': '🧠'
            },
        ]
    })
