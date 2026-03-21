from flask import Blueprint, request, jsonify
import concurrent.futures
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
_log_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)


def _persist_prediction_log(app, disease_type, input_data, response_data, ip_address):
    """Persist prediction result to database."""
    with app.app_context():
        try:
            log = PredictionLog(
                disease_type=disease_type,
                input_data=input_data,
                prediction=response_data.get('prediction', 0),
                risk_level=response_data.get('risk_level', 'Unknown'),
                confidence=response_data.get('confidence'),
                advice=response_data.get('advice', ''),
                shap_contributions=response_data.get('shap_contributions'),
                ip_address=ip_address,
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            logger.warning(f"Failed to log prediction: {e}")
            db.session.rollback()


def _log_prediction_async(disease_type, input_data, response_data):
    """Queue non-blocking history logging after response generation."""
    try:
        from flask import current_app
        app_obj = current_app._get_current_object()
        ip_address = request.remote_addr
        _log_executor.submit(
            _persist_prediction_log, app_obj, disease_type, input_data, response_data, ip_address
        )
    except Exception as e:
        logger.warning(f"Failed to queue prediction log: {e}")


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

    include_explanations = request.args.get('include_explanations', 'false').lower() == 'true'
    response, status_code = model_service.predict('heart', data, include_explanations=include_explanations)
    if response.get('success'):
        _log_prediction_async('heart', data, response)
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

    include_explanations = request.args.get('include_explanations', 'false').lower() == 'true'
    response, status_code = model_service.predict('diabetes', data, include_explanations=include_explanations)
    if response.get('success'):
        _log_prediction_async('diabetes', data, response)
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

    include_explanations = request.args.get('include_explanations', 'false').lower() == 'true'
    response, status_code = model_service.predict('kidney', data, include_explanations=include_explanations)
    if response.get('success'):
        _log_prediction_async('kidney', data, response)
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

    include_explanations = request.args.get('include_explanations', 'false').lower() == 'true'
    response, status_code = model_service.predict('depression', data, include_explanations=include_explanations)
    if response.get('success'):
        _log_prediction_async('depression', data, response)
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
    from flask import current_app
    if not current_app.config.get('ENABLE_METRICS_ENDPOINT', False):
        return jsonify({'success': False, 'error': 'Not found'}), 404
    try:
        metrics = model_service.get_evaluation_metrics()
        return jsonify({'success': True, 'metrics': metrics}), 200
    except Exception as e:
        logger.warning(f"Failed to load model metrics: {e}")
        return jsonify({'success': False, 'error': 'Could not load model metrics'}), 500

