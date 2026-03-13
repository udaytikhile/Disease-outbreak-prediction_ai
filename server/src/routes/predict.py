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

    # region agent log
    try:
        import json, time
        with open('/home/udaylinux/Desktop/Disease-outbreak-prediction_ai/.cursor/debug-941ec4.log', 'a') as f:
            f.write(json.dumps({
                "sessionId": "941ec4",
                "runId": "pre-fix",
                "hypothesisId": "B",
                "location": "server/src/routes/predict.py:76",
                "message": "predict_heart_request",
                "data": {"disease": "heart"},
                "timestamp": int(time.time() * 1000)
            }) + "\n")
    except Exception:
        pass
    # endregion

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
    from ..constants import DISEASES
    return jsonify({
        'diseases': list(DISEASES.values())
    })


@predict_bp.route('/predict/metrics', methods=['GET'])
def get_model_metrics():
    """Get evaluation metrics for each disease model (internal/debug use).
    ---
    tags:
      - Predictions
    responses:
      200:
        description: Evaluation metrics for all loaded disease models
    """
    try:
        metrics = model_service.get_evaluation_metrics()
        return jsonify({'success': True, 'metrics': metrics}), 200
    except Exception as e:
        logger.warning(f"Failed to load model metrics: {e}")
        return jsonify({'success': False, 'error': 'Could not load model metrics'}), 500

