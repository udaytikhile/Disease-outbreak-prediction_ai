"""
Model Service — loads .pkl pipeline models and runs predictions.
Each pipeline includes preprocessing (imputation, scaling, encoding)
so we only need to build the raw DataFrame and apply feature engineering.

Features:
  - Bug 5 fix: saved decision threshold applied via predict_proba
  - Bug 3 note: all feature builders use explicit column dicts
  - Bug 2 fix: RuntimeError on load failure
  - Feature 1: SHAP TreeExplainer for top-3 feature contributions
  - Feature 4: version + trained_at metadata loaded from pkl
"""
import joblib
import numpy as np
import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Feature 1: SHAP import with graceful fallback ────────────────────────────
try:
    import shap
    _SHAP_AVAILABLE = True
except ImportError:
    _SHAP_AVAILABLE = False
    logger.warning("⚠️  shap not installed — SHAP explanations disabled. Run: pip install shap")


class ModelService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelService, cls).__new__(cls)
            cls._instance.models = {}
            cls._instance.loaded = False
        return cls._instance

    # ── Model loading ────────────────────────────────────────────────────
    def load_models(self, model_dir):
        """Load all ML pipeline models from .pkl files.

        Each .pkl is a dict {'pipeline', 'threshold', 'version', 'trained_at'}
        produced by the training script. Plain pipeline objects are also accepted
        for backward compatibility (threshold defaults to 0.5, no version info).
        """
        if self.loaded:
            return

        try:
            model_path = Path(model_dir)
            if not model_path.exists():
                # Bug 2 fix: hard failure so Flask refuses to start
                raise RuntimeError(
                    f"Model directory not found: {model_path}. "
                    "Run 'python ml/scripts/train_all_models.py' first."
                )

            model_files = {
                'diabetes':   'diabetes_model.pkl',
                'heart':      'heart_disease_model.pkl',
                'kidney':     'kidney_disease_model.pkl',
                'depression': 'depression_model.pkl',
            }

            for disease, filename in model_files.items():
                fpath = model_path / filename
                if fpath.exists():
                    try:
                        artifact = joblib.load(fpath)
                        # Bug 5 / Feature 4: support versioned dict format
                        if isinstance(artifact, dict) and 'pipeline' in artifact:
                            pipeline   = artifact['pipeline']
                            threshold  = float(artifact.get('threshold', 0.5))
                            version    = artifact.get('version', 'unknown')
                            trained_at = artifact.get('trained_at', None)
                        else:
                            # Backward compat: plain pipeline
                            pipeline   = artifact
                            threshold  = 0.5
                            version    = 'legacy'
                            trained_at = None

                        # Feature 1: build SHAP explainer for this model
                        explainer, feature_names = self._build_shap_explainer(pipeline)

                        self.models[disease] = {
                            'pipeline':      pipeline,
                            'threshold':     threshold,
                            'version':       version,
                            'trained_at':    trained_at,
                            'explainer':     explainer,       # may be None
                            'feature_names': feature_names,  # may be None
                        }
                        logger.info(
                            f"  ✅ Loaded {disease} model from {filename} "
                            f"(v{version}, threshold={threshold}, "
                            f"shap={'yes' if explainer else 'no'})"
                        )
                    except Exception as load_err:
                        logger.error(f"  ❌ Failed to load {filename}: {load_err}")
                else:
                    logger.warning(f"  ⚠️  Model file not found: {fpath}")

            if not self.models:
                # Bug 2 fix: raise so the server startup fails loudly
                raise RuntimeError(
                    "No models were loaded. Run 'python ml/scripts/train_all_models.py' "
                    "to generate the .pkl files before starting the server."
                )

            self.loaded = True
            logger.info(f"✅ All models loaded: {list(self.models.keys())}")
        except RuntimeError:
            # Re-raise RuntimeErrors (Bug 2: startup failures) unchanged
            self.loaded = False
            raise
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self.loaded = False
            raise RuntimeError(f"Model loading failed: {e}") from e

    # ── Feature 4: version info ──────────────────────────────────────────
    def get_model_versions(self) -> dict:
        """Return version metadata for all loaded models (for /health endpoint)."""
        return {
            disease: {
                'version':    info.get('version', 'unknown'),
                'trained_at': info.get('trained_at'),
                'threshold':  info.get('threshold', 0.5),
            }
            for disease, info in self.models.items()
        }

    # ── Feature 1: SHAP helpers ──────────────────────────────────────────
    @staticmethod
    def _build_shap_explainer(pipeline):
        """Build a SHAP TreeExplainer for the classifier step of a sklearn Pipeline.

        Returns (explainer, feature_names_list) or (None, None) on failure.
        Feature names are extracted from the ColumnTransformer 'preprocessor' step.
        """
        if not _SHAP_AVAILABLE:
            return None, None
        try:
            classifier = pipeline.named_steps.get('classifier')
            if classifier is None:
                return None, None

            explainer = shap.TreeExplainer(classifier)

            # Extract feature names from the preprocessor's output
            feature_names = None
            preprocessor = pipeline.named_steps.get('preprocessor')
            if preprocessor is not None:
                try:
                    feature_names = list(preprocessor.get_feature_names_out())
                except Exception:
                    pass

            return explainer, feature_names
        except Exception as e:
            logger.warning(f"SHAP explainer could not be built: {e}")
            return None, None

    def _get_shap_contributions(self, disease_type: str, features_df: pd.DataFrame) -> list:
        """Compute top-3 SHAP feature contributions for a single prediction.

        Returns a list of dicts:
          {'feature': str, 'contribution': float, 'direction': 'risk' | 'protective', 'pct': float}
        or an empty list if SHAP is unavailable or fails.
        """
        model_entry = self.models.get(disease_type, {})
        explainer    = model_entry.get('explainer')
        feature_names = model_entry.get('feature_names')
        pipeline      = model_entry.get('pipeline')

        if explainer is None or pipeline is None:
            return []

        try:
            preprocessor = pipeline.named_steps.get('preprocessor')
            if preprocessor is None:
                return []

            # Transform input to the feature space the classifier sees
            X_transformed = preprocessor.transform(features_df)

            # SHAP values: shape (n_samples, n_features) for binary class 1
            sv = explainer.shap_values(X_transformed)
            # For multi-output (list), index 1 = positive class
            if isinstance(sv, list):
                shap_vals = sv[1][0]
            else:
                # Single array — XGBoost returns shape (n_samples, n_features) directly
                shap_vals = sv[0] if sv.ndim == 2 else sv

            if feature_names is None or len(feature_names) != len(shap_vals):
                # Fall back to generic names
                feature_names = [f"feature_{i}" for i in range(len(shap_vals))]

            # Prettify transformer prefix (e.g. "num__BMI" → "BMI")
            def clean_name(name: str) -> str:
                return name.split('__', 1)[-1] if '__' in name else name

            # Sort by absolute value and take top 3
            indexed = sorted(
                enumerate(shap_vals), key=lambda x: abs(x[1]), reverse=True
            )[:3]

            total_abs = sum(abs(v) for _, v in indexed) or 1.0
            contributions = []
            for idx, sv_val in indexed:
                pct = round(abs(sv_val) / total_abs * 100, 1)
                contributions.append({
                    'feature':      clean_name(feature_names[idx]),
                    'contribution': round(float(sv_val), 4),
                    'direction':    'risk' if sv_val > 0 else 'protective',
                    'pct':          pct,
                })

            return contributions
        except Exception as e:
            logger.warning(f"SHAP computation failed for {disease_type}: {e}")
            return []

    # ── Feature engineering helpers ──────────────────────────────────────
    @staticmethod
    def _safe_float(val):
        if val in (None, ''): return np.nan
        try: return float(val)
        except (ValueError, TypeError): return np.nan

    @staticmethod
    def _safe_str(val):
        if val in (None, ''): return np.nan
        return str(val)

    @staticmethod
    def _build_diabetes_df(data: dict) -> pd.DataFrame:
        """Build DataFrame matching the diabetes training pipeline.

        Bug 3 note: columns are constructed explicitly by name so JSON field
        order never affects the feature vector — do NOT use list(data.values()).
        """
        raw_cols = [
            'HighBP', 'HighChol', 'CholCheck', 'BMI', 'Smoker', 'Stroke',
            'HeartDiseaseorAttack', 'PhysActivity', 'Fruits', 'Veggies',
            'HvyAlcoholConsump', 'AnyHealthcare', 'NoDocbcCost', 'GenHlth',
            'MentHlth', 'PhysHlth', 'DiffWalk', 'Sex', 'Age', 'Education',
            'Income',
        ]
        row = {col: ModelService._safe_float(data.get(col)) for col in raw_cols}
        df = pd.DataFrame([row])

        # Engineered features (must match training script)
        df['BMI_Age'] = df['BMI'] * df['Age']
        df['HighBP_HighChol'] = df['HighBP'] * df['HighChol']
        df['GenHlth_PhysHlth'] = df['GenHlth'] * df['PhysHlth']
        df['GenHlth_MentHlth'] = df['GenHlth'] * df['MentHlth']
        df['BMI_HighBP'] = df['BMI'] * df['HighBP']
        return df

    @staticmethod
    def _build_heart_df(data: dict) -> pd.DataFrame:
        """Build DataFrame matching the heart disease training pipeline.

        Bug 3 note: each column is populated by name — JSON field order is irrelevant.
        """
        row = {
            'age':      ModelService._safe_float(data.get('age')),
            'sex':      ModelService._safe_str(data.get('sex')),
            'dataset':  ModelService._safe_str(data.get('dataset', 'Cleveland')),
            'cp':       ModelService._safe_str(data.get('cp')),
            'trestbps': ModelService._safe_float(data.get('trestbps')),
            'chol':     ModelService._safe_float(data.get('chol')),
            'fbs':      ModelService._safe_str(data.get('fbs')),
            'restecg':  ModelService._safe_str(data.get('restecg')),
            'thalch':   ModelService._safe_float(data.get('thalch')),
            'exang':    ModelService._safe_str(data.get('exang')),
            'oldpeak':  ModelService._safe_float(data.get('oldpeak')),
            'slope':    ModelService._safe_str(data.get('slope')),
            'ca':       ModelService._safe_float(data.get('ca')),
            'thal':     ModelService._safe_str(data.get('thal')),
        }
        df = pd.DataFrame([row])
        # Engineered feature
        df['age_sq'] = df['age'] ** 2
        return df

    @staticmethod
    def _build_kidney_df(data: dict) -> pd.DataFrame:
        """Build DataFrame matching the kidney disease training pipeline.

        Bug 3 note: `cols` list defines an explicit, fixed column order that
        matches training — never derived from the incoming JSON key order.
        """
        cols = [
            'age', 'bp', 'sg', 'al', 'su', 'rbc', 'pc', 'pcc', 'ba',
            'bgr', 'bu', 'sc', 'sod', 'pot', 'hemo', 'pcv', 'wc', 'rc',
            'htn', 'dm', 'cad', 'appet', 'pe', 'ane',
        ]
        row = {col: ModelService._safe_float(data.get(col)) for col in cols}
        return pd.DataFrame([row])

    @staticmethod
    def _build_depression_df(data: dict) -> pd.DataFrame:
        """Build DataFrame matching the depression training pipeline.

        Bug 3 note: all fields are populated by explicit name lookup from `data`
        — JSON field order is irrelevant.
        """
        # Sleep duration mapping
        sleep_map = {
            'Less than 5 hours': 4,
            '5-6 hours': 5.5,
            '7-8 hours': 7.5,
            'More than 8 hours': 9,
            'Others': 6.5,
        }
        diet_map = {'Unhealthy': 0, 'Moderate': 1, 'Healthy': 2, 'Others': 1}

        gender_val = 1 if str(data.get('gender', '')).strip() == 'Male' else 0
        suicidal = 1 if str(data.get('suicidal_thoughts', 'No')).strip() == 'Yes' else 0
        family_hist = 1 if str(data.get('family_history', 'No')).strip() == 'Yes' else 0

        sleep_str = str(data.get('sleep_duration', 'Others')).strip()
        sleep_hours = sleep_map.get(sleep_str, 6.5)

        diet_str = str(data.get('dietary_habits', 'Moderate')).strip()
        dietary_ordinal = diet_map.get(diet_str, 1)

        academic_pressure = ModelService._safe_float(data.get('academic_pressure', 0))
        work_pressure = ModelService._safe_float(data.get('work_pressure', 0))
        cgpa = ModelService._safe_float(data.get('cgpa', 0))
        study_satisfaction = ModelService._safe_float(data.get('study_satisfaction', 0))
        job_satisfaction = ModelService._safe_float(data.get('job_satisfaction', 0))
        work_study_hours = ModelService._safe_float(data.get('work_study_hours', 0))
        financial_stress = ModelService._safe_float(data.get('financial_stress', 0))
        age = ModelService._safe_float(data.get('age', 20))

        row = {
            'Gender': gender_val,
            'Age': age,
            'Profession': str(data.get('profession', 'Student')),
            'Academic Pressure': academic_pressure,
            'Work Pressure': work_pressure,
            'CGPA': cgpa,
            'Study Satisfaction': study_satisfaction,
            'Job Satisfaction': job_satisfaction,
            'Sleep_Hours': sleep_hours,
            'Dietary_Ordinal': dietary_ordinal,
            'Degree': str(data.get('degree', 'BSc')),
            'Have you ever had suicidal thoughts ?': suicidal,
            'Work/Study Hours': work_study_hours,
            'Financial Stress': financial_stress,
            'Family History of Mental Illness': family_hist,
        }
        df = pd.DataFrame([row])
        # Engineered features
        df['Pressure_vs_Satisfaction'] = df['Academic Pressure'] - df['Study Satisfaction']
        df['WorkStudy_Sleep_Ratio'] = df['Work/Study Hours'] / (sleep_hours + 0.1)
        df['Financial_Academic'] = df['Financial Stress'] * df['Academic Pressure']
        return df

    # ── Prediction ───────────────────────────────────────────────────────
    def predict(self, disease_type: str, form_data: dict) -> tuple:
        if not self.loaded:
            return {'success': False, 'error': 'Models not loaded'}, 503

        if disease_type not in self.models:
            return {'success': False, 'error': f'Unknown disease type: {disease_type}'}, 400

        try:
            # Build feature DataFrame
            builder_name = f'_build_{disease_type}_df'
            if not hasattr(self, builder_name):
                return {'success': False, 'error': 'No feature builder for this disease'}, 500
            
            builder = getattr(self, builder_name)
            features_df = builder(form_data)

            # Run pipeline prediction
            # Bug 5 fix: use saved threshold with predict_proba instead of predict()
            pipeline  = self.models[disease_type]['pipeline']
            threshold = self.models[disease_type].get('threshold', 0.5)

            try:
                probability = pipeline.predict_proba(features_df)[0]
                pos_prob    = float(probability[1])  # P(positive class)
                prediction  = 1 if pos_prob >= threshold else 0
                confidence  = round(max(float(probability[0]), float(probability[1])) * 100, 1)
            except AttributeError:
                # Fallback for models without predict_proba
                prediction = int(pipeline.predict(features_df)[0])
                confidence = None

            # Feature 1: SHAP top-3 contributions
            shap_contributions = self._get_shap_contributions(disease_type, features_df)

            # Advice
            advice_map = {
                'heart': {
                    1: "⚠️ Risk Detected: Consult a cardiologist immediately. Maintain a heart-healthy diet, exercise regularly, and monitor your blood pressure.",
                    0: "✅ Low Risk: Maintain a healthy lifestyle with balanced diet and regular exercise to keep your heart healthy."
                },
                'diabetes': {
                    1: "⚠️ Risk Detected: Check blood sugar regularly. Follow a diabetic-friendly diet, exercise routine, and consult an endocrinologist.",
                    0: "✅ Low Risk: Maintain a balanced diet and exercise regularly to prevent diabetes. Monitor your blood sugar periodically."
                },
                'kidney': {
                    0: "⚠️ Risk Detected: Signs indicate chronic kidney disease. Consult a nephrologist for further evaluation, blood tests, and kidney function monitoring.",
                    1: "✅ Low Risk: Kidney function appears normal. Stay hydrated, maintain healthy blood pressure, and get periodic check-ups."
                },
                'depression': {
                    1: "⚠️ Risk Detected: Indicators suggest possible depression. Please consider speaking with a mental health professional for proper evaluation and support.",
                    0: "✅ Low Risk: Mental health indicators look positive. Continue maintaining healthy habits, social connections, and work-life balance."
                },
            }

            disease_names = {
                'heart': 'Heart Disease',
                'diabetes': 'Diabetes',
                'kidney': 'Chronic Kidney Disease',
                'depression': 'Depression',
            }

            risk_level = "High" if prediction == 1 else "Low"
            # Kidney disease: ckd=0 is disease, notckd=1 is healthy
            if disease_type == 'kidney':
                risk_level = "High" if prediction == 0 else "Low"

            advice = advice_map.get(disease_type, {}).get(prediction, "Consult a doctor for advice.")

            return {
                'success':            True,
                'prediction':         prediction,
                'risk_level':         risk_level,
                'confidence':         confidence,
                'advice':             advice,
                'disease':            disease_names.get(disease_type, disease_type),
                'shap_contributions': shap_contributions,   # Feature 1
                'model_version':      self.models[disease_type].get('version', 'unknown'),  # Feature 4
            }, 200

        except Exception as e:
            logger.error(f"Prediction error for {disease_type}: {str(e)}", exc_info=True)
            return {'success': False, 'error': f'Prediction failed: {str(e)}'}, 500


model_service = ModelService()

