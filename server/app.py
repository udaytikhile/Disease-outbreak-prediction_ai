from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import pandas as pd
import os
import logging
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=['http://localhost:5173', 'http://127.0.0.1:5173'])

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load ML models - Use absolute path
BACKEND_DIR = Path(__file__).parent.absolute()
MODEL_DIR = BACKEND_DIR.parent / 'ml' / 'models'

def _load_pickle(filepath):
    """Load a pickle file with proper file handle management"""
    with open(filepath, 'rb') as f:
        return pickle.load(f)

def load_models() -> dict | None:
    """Load all ML models and scalers"""
    try:
        models = {
            'heart': {
                'model': _load_pickle(f'{MODEL_DIR}/heart_disease_model.sav'),
                'scaler': _load_pickle(f'{MODEL_DIR}/scaler_heart_disease.sav'),
                'fields': ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal'],
                'scaler_columns': ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']
            },
            'diabetes': {
                'model': _load_pickle(f'{MODEL_DIR}/diabetes_model.sav'),
                'scaler': _load_pickle(f'{MODEL_DIR}/scaler_diabetes.sav'),
                'fields': ['pregnancies', 'glucose', 'bloodPressure', 'skinThickness', 'insulin', 'bmi', 'dpf', 'age'],
                'scaler_columns': ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
            },
            'parkinsons': {
                'model': _load_pickle(f'{MODEL_DIR}/parkinsons_model.sav'),
                'scaler': _load_pickle(f'{MODEL_DIR}/scaler_parkinsons.sav'),
                'fields': ['fo', 'fhi', 'flo', 'jitter', 'jitterAbs', 'rap', 'ppq', 'ddp', 'shimmer', 'shimmerDb', 'apq3', 'apq5', 'apq', 'dda', 'nhr', 'hnr', 'rpde', 'dfa', 'spread1', 'spread2', 'd2', 'ppe'],
                'scaler_columns': ['MDVP:Fo(Hz)', 'MDVP:Fhi(Hz)', 'MDVP:Flo(Hz)', 'MDVP:Jitter(%)', 'MDVP:Jitter(Abs)', 'MDVP:RAP', 'MDVP:PPQ', 'Jitter:DDP', 'MDVP:Shimmer', 'MDVP:Shimmer(dB)', 'Shimmer:APQ3', 'Shimmer:APQ5', 'MDVP:APQ', 'Shimmer:DDA', 'NHR', 'HNR', 'RPDE', 'DFA', 'spread1', 'spread2', 'D2', 'PPE']
            }
        }
        logger.info("✅ All models loaded successfully!")
        return models
    except FileNotFoundError as e:
        logger.error(f"Model file not found: {e}")
        return None
    except Exception as e:
        logger.error(f"Error loading models: {e}")
        return None

models = load_models()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'models_loaded': models is not None
    })

def validate_input(data: dict, required_fields: list) -> tuple[bool, str]:
    """Validate input data has all required fields"""
    if not data:
        return False, "No data provided"
    
    missing_fields = [f for f in required_fields if f not in data]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, ""

def safe_float_convert(value, field_name: str) -> tuple[float | None, str]:
    """Safely convert value to float"""
    try:
        return float(value), ""
    except (ValueError, TypeError):
        return None, f"Invalid value for {field_name}: must be a number"

def make_prediction(disease_type: str, form_data: dict) -> tuple[dict, int]:
    """
    Generic prediction function for all diseases
    Returns: (response_dict, status_code)
    """
    if models is None:
        return {'success': False, 'error': 'Models not loaded'}, 503
    
    if disease_type not in models:
        return {'success': False, 'error': f'Unknown disease type: {disease_type}'}, 400
    
    model_info = models[disease_type]
    required_fields = model_info['fields']
    
    # Validate input
    is_valid, error_msg = validate_input(form_data, required_fields)
    if not is_valid:
        logger.warning(f"Validation failed for {disease_type}: {error_msg}")
        return {'success': False, 'error': error_msg}, 400
    
    # Convert and validate features
    features = []
    for field in required_fields:
        value, error = safe_float_convert(form_data[field], field)
        if error:
            logger.warning(f"Conversion error for {disease_type}.{field}: {error}")
            return {'success': False, 'error': error}, 400
        features.append(value)
    
    try:
        # Scale and predict using DataFrame with original scaler column names
        scaler_columns = model_info.get('scaler_columns', required_fields)
        features_df = pd.DataFrame([features], columns=scaler_columns)
        scaled_features = model_info['scaler'].transform(features_df)
        prediction = int(model_info['model'].predict(scaled_features)[0])
        
        # Get probability
        confidence = None
        try:
            probability = model_info['model'].predict_proba(scaled_features)[0]
            confidence = float(max(probability)) * 100
        except AttributeError:
            pass  # Model doesn't support predict_proba
        
        # Generate advice based on prediction
        advice_map = {
            'heart': {
                1: "⚠️ Risk Detected: Consult a cardiologist immediately. Maintain a heart-healthy diet, exercise regularly, and monitor your blood pressure.",
                0: "✅ Low Risk: Maintain a healthy lifestyle with balanced diet and regular exercise to keep your heart healthy."
            },
            'diabetes': {
                1: "⚠️ Risk Detected: Check blood sugar regularly. Follow a diabetic-friendly diet, exercise routine, and consult an endocrinologist.",
                0: "✅ Low Risk: Maintain a balanced diet and exercise regularly to prevent diabetes. Monitor your blood sugar periodically."
            },
            'parkinsons': {
                1: "⚠️ Risk Detected: Consult a neurologist for comprehensive evaluation and treatment plan. Stay active and follow prescribed therapies.",
                0: "✅ Low Risk: Stay active and healthy. Regular exercise supports neurological health. Monitor any unusual symptoms."
            }
        }
        
        disease_names = {
            'heart': 'Heart Disease',
            'diabetes': 'Diabetes',
            'parkinsons': "Parkinson's Disease"
        }
        
        risk_level = "High" if prediction == 1 else "Low"
        advice = advice_map[disease_type][prediction]
        
        logger.info(f"Prediction successful for {disease_type}: risk={risk_level}, confidence={confidence}")
        
        return {
            'success': True,
            'prediction': prediction,
            'risk_level': risk_level,
            'confidence': confidence,
            'advice': advice,
            'disease': disease_names[disease_type]
        }, 200
    
    except Exception as e:
        logger.error(f"Prediction error for {disease_type}: {str(e)}", exc_info=True)
        return {'success': False, 'error': 'Prediction failed. Please try again.'}, 500

@app.route('/api/predict/heart', methods=['POST'])
def predict_heart():
    """Predict heart disease"""
    response, status_code = make_prediction('heart', request.json or {})
    return jsonify(response), status_code

@app.route('/api/predict/diabetes', methods=['POST'])
def predict_diabetes():
    """Predict diabetes"""
    response, status_code = make_prediction('diabetes', request.json or {})
    return jsonify(response), status_code

@app.route('/api/predict/parkinsons', methods=['POST'])
def predict_parkinsons():
    """Predict Parkinson's disease"""
    response, status_code = make_prediction('parkinsons', request.json or {})
    return jsonify(response), status_code

@app.route('/api/diseases', methods=['GET'])
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

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f"404 error: {request.path}")
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f"500 error: {str(error)}", exc_info=True)
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    if models is None:
        logger.error("❌ ERROR: Models failed to load! Check if ml/models folder exists.")
    else:
        logger.info("✅ All models loaded successfully!")
        logger.info("🚀 Starting Flask server on http://0.0.0.0:5001")
    
    # debug=False for production, set environment variable to change
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('FLASK_PORT', '5001'))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
