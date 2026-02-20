import pickle
import pandas as pd
import logging
from pathlib import Path
from flask import current_app

logger = logging.getLogger(__name__)

class ModelService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelService, cls).__new__(cls)
            cls._instance.models = {}
            cls._instance.loaded = False
        return cls._instance

    def load_models(self, model_dir):
        """Load all ML models and scalers"""
        if self.loaded:
            return

        try:
            model_path = Path(model_dir)
            if not model_path.exists():
                logger.error(f"Model directory not found: {model_path}")
                return

            self.models = {
                'heart': {
                    'model': self._load_pickle(model_path / 'heart_disease_model.sav'),
                    'scaler': self._load_pickle(model_path / 'scaler_heart_disease.sav'),
                    'fields': ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal'],
                    'scaler_columns': ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']
                },
                'diabetes': {
                    'model': self._load_pickle(model_path / 'diabetes_model.sav'),
                    'scaler': self._load_pickle(model_path / 'scaler_diabetes.sav'),
                    'fields': ['pregnancies', 'glucose', 'bloodPressure', 'skinThickness', 'insulin', 'bmi', 'dpf', 'age'],
                    'scaler_columns': ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
                },
                'parkinsons': {
                    'model': self._load_pickle(model_path / 'parkinsons_model.sav'),
                    'scaler': self._load_pickle(model_path / 'scaler_parkinsons.sav'),
                    'fields': ['fo', 'fhi', 'flo', 'jitter', 'jitterAbs', 'rap', 'ppq', 'ddp', 'shimmer', 'shimmerDb', 'apq3', 'apq5', 'apq', 'dda', 'nhr', 'hnr', 'rpde', 'dfa', 'spread1', 'spread2', 'd2', 'ppe'],
                    'scaler_columns': ['MDVP:Fo(Hz)', 'MDVP:Fhi(Hz)', 'MDVP:Flo(Hz)', 'MDVP:Jitter(%)', 'MDVP:Jitter(Abs)', 'MDVP:RAP', 'MDVP:PPQ', 'Jitter:DDP', 'MDVP:Shimmer', 'MDVP:Shimmer(dB)', 'Shimmer:APQ3', 'Shimmer:APQ5', 'MDVP:APQ', 'Shimmer:DDA', 'NHR', 'HNR', 'RPDE', 'DFA', 'spread1', 'spread2', 'D2', 'PPE']
                }
            }
            # Verify all models and scalers loaded successfully (BUG-8 fix)
            for disease, info in self.models.items():
                if info['model'] is None or info['scaler'] is None:
                    raise ValueError(f"Model or scaler for '{disease}' failed to load (got None)")
            self.loaded = True
            logger.info("✅ All models loaded successfully!")
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self.loaded = False

    def _load_pickle(self, filepath):
        with open(filepath, 'rb') as f:
            return pickle.load(f)

    def validate_input(self, data: dict, required_fields: list) -> tuple[bool, str]:
        if not data:
            return False, "No data provided"
        
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        return True, ""

    def safe_float_convert(self, value, field_name: str) -> tuple[float | None, str]:
        try:
            return float(value), ""
        except (ValueError, TypeError):
            return None, f"Invalid value for {field_name}: must be a number"

    def predict(self, disease_type: str, form_data: dict) -> tuple[dict, int]:
        if not self.loaded:
            return {'success': False, 'error': 'Models not loaded'}, 503
        
        if disease_type not in self.models:
            return {'success': False, 'error': f'Unknown disease type: {disease_type}'}, 400
        
        model_info = self.models[disease_type]
        required_fields = model_info['fields']
        
        is_valid, error_msg = self.validate_input(form_data, required_fields)
        if not is_valid:
            logger.warning(f"Validation failed for {disease_type}: {error_msg}")
            return {'success': False, 'error': error_msg}, 400
        
        features = []
        for field in required_fields:
            value, error = self.safe_float_convert(form_data[field], field)
            if error:
                logger.warning(f"Conversion error for {disease_type}.{field}: {error}")
                return {'success': False, 'error': error}, 400
            features.append(value)
        
        try:
            scaler_columns = model_info.get('scaler_columns', required_fields)
            features_df = pd.DataFrame([features], columns=scaler_columns)
            scaled_features = model_info['scaler'].transform(features_df)
            prediction = int(model_info['model'].predict(scaled_features)[0])
            
            confidence = None
            try:
                probability = model_info['model'].predict_proba(scaled_features)[0]
                confidence = float(max(probability)) * 100
            except AttributeError:
                pass
            
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
            advice = advice_map.get(disease_type, {}).get(prediction, "Consult a doctor for advice.")
            
            return {
                'success': True,
                'prediction': prediction,
                'risk_level': risk_level,
                'confidence': confidence,
                'advice': advice,
                'disease': disease_names.get(disease_type, disease_type)
            }, 200
        
        except Exception as e:
            logger.error(f"Prediction error for {disease_type}: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'Prediction failed. Please try again.'}, 500

model_service = ModelService()
