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
from .model_loader import safe_load_model
import json
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
            cls._instance.model_dir = None
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

            self.model_dir = model_path

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
                        artifact = safe_load_model(fpath)
                        if artifact is None:
                            logger.error(f"  ❌ Skipping {filename}: could not load (see above)")
                            continue
                        # Bug 5 / Feature 4: support versioned dict format
                        if isinstance(artifact, dict) and 'pipeline' in artifact:
                            pipeline   = artifact['pipeline']
                            threshold  = float(artifact.get('threshold', 0.5))
                            version    = artifact.get('version', 'unknown')
                            trained_at = artifact.get('trained_at', None)
                            # Optional SHAP feature selection metadata from training
                            feature_names_out = artifact.get('feature_names_out')
                            keep_indices = artifact.get('keep_indices')
                        else:
                            # Backward compat: plain pipeline
                            pipeline   = artifact
                            threshold  = 0.5
                            version    = 'legacy'
                            trained_at = None
                            feature_names_out = None
                            keep_indices = None

                        # Feature 1: build SHAP explainer for this model
                        explainer, feature_names = self._build_shap_explainer(pipeline)

                        self.models[disease] = {
                            'pipeline':          pipeline,
                            'threshold':         threshold,
                            'version':           version,
                            'trained_at':        trained_at,
                            'explainer':         explainer,          # may be None
                            'feature_names':     feature_names,      # SHAP-prepared names (may be None)
                            'feature_names_out': feature_names_out,  # saved from training (may be None)
                            'keep_indices':      keep_indices,       # SHAP-selected indices (may be None)
                        }

                        # Light-weight feature parity check between training and runtime preprocessor
                        if feature_names_out is not None:
                            self._check_feature_parity(disease, pipeline, feature_names_out)
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

    @staticmethod
    def _check_feature_parity(disease: str, pipeline, saved_feature_names):
        """Warn if runtime preprocessor feature names differ from training-time names.

        This helps catch silent mismatches between training and inference
        feature engineering (e.g., adding/removing columns without retraining).
        """
        try:
            preprocessor = pipeline.named_steps.get('preprocessor')
            if preprocessor is None:
                return
            try:
                runtime_names = list(preprocessor.get_feature_names_out())
            except Exception:
                return
            if len(runtime_names) != len(saved_feature_names) or runtime_names != list(saved_feature_names):
                logger.warning(
                    "Feature mismatch for %s model: training feature_names_out length=%d, "
                    "runtime length=%d. Ensure training scripts and ModelService builders are aligned.",
                    disease,
                    len(saved_feature_names),
                    len(runtime_names),
                )
        except Exception as e:
            logger.debug(f"Feature parity check failed for {disease}: {e}")

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

    def get_evaluation_metrics(self) -> dict:
        """Return evaluation metrics loaded from JSON artifacts next to model files.

        Each metrics file is expected to be saved as <model>.metrics.json by the
        training pipeline. Missing or unreadable files are skipped.
        """
        if not self.loaded or self.model_dir is None:
            return {}

        metrics = {}
        model_files = {
            'diabetes':   'diabetes_model.pkl',
            'heart':      'heart_disease_model.pkl',
            'kidney':     'kidney_disease_model.pkl',
            'depression': 'depression_model.pkl',
        }

        for disease, filename in model_files.items():
            metrics_path = self.model_dir / f"{Path(filename).stem}.metrics.json"
            if not metrics_path.exists():
                continue
            try:
                with open(metrics_path, "r", encoding="utf-8") as f:
                    metrics[disease] = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load metrics for {disease} from {metrics_path}: {e}")

        return metrics

    # ── Feature 1: SHAP helpers ──────────────────────────────────────────
    _shap_xgb_patched = False   # class-level flag to avoid double-patching

    @staticmethod
    def _patch_shap_xgboost_compat():
        """Monkey-patch SHAP's decode_ubjson_buffer to fix XGBoost 2.0+ base_score.

        XGBoost 2.0+ stores base_score as a bracketed string like '[5.000088E-1]'
        in its UBJ model dump. SHAP's XGBTreeModelLoader does float(base_score)
        on the decoded dict which fails. We patch the decode function to clean
        the value immediately after decoding.
        """
        if ModelService._shap_xgb_patched:
            return
        try:
            import shap.explainers._tree as _tree_mod
            _orig_decode = _tree_mod.decode_ubjson_buffer

            def _clean_decode(fd):
                result = _orig_decode(fd)
                # Fix base_score if present
                try:
                    lmp = result['learner']['learner_model_param']
                    bs = lmp.get('base_score', '')
                    if isinstance(bs, str) and bs.startswith('[') and bs.endswith(']'):
                        lmp['base_score'] = bs.strip('[]')
                except (KeyError, TypeError):
                    pass
                return result

            _tree_mod.decode_ubjson_buffer = _clean_decode
            ModelService._shap_xgb_patched = True
            logger.debug("Patched SHAP decode_ubjson_buffer for XGBoost compat")
        except Exception as e:
            logger.debug(f"SHAP XGBoost compat patch failed: {e}")

    @staticmethod
    def _unwrap_tree_model(classifier):
        """Unwrap CalibratedClassifierCV / StackingClassifier to find a tree model.

        Returns the first tree-based estimator suitable for SHAP TreeExplainer,
        or None if no tree model can be found.
        """
        # Direct tree model
        if hasattr(classifier, 'get_booster') or hasattr(classifier, 'estimators_'):
            return classifier

        # CalibratedClassifierCV wraps an estimator
        if hasattr(classifier, 'calibrated_classifiers_'):
            inner = classifier.calibrated_classifiers_[0].estimator
            return ModelService._unwrap_tree_model(inner)

        # StackingClassifier — use the first base estimator
        if hasattr(classifier, 'estimators_') and isinstance(classifier.estimators_, list):
            for est in classifier.estimators_:
                result = ModelService._unwrap_tree_model(est)
                if result is not None:
                    return result

        # Named estimators on StackingClassifier (fitted)
        if hasattr(classifier, 'named_estimators_'):
            for name, est in classifier.named_estimators_.items():
                result = ModelService._unwrap_tree_model(est)
                if result is not None:
                    return result

        return None

    @staticmethod
    def _build_shap_explainer(pipeline):
        """Build a SHAP TreeExplainer for the classifier step of a sklearn Pipeline.

        Returns (explainer, feature_names_list) or (None, None) on failure.
        Handles stacking ensembles and CalibratedClassifierCV by unwrapping
        to find the first tree-based estimator.
        """
        if not _SHAP_AVAILABLE:
            return None, None
        try:
            classifier = pipeline.named_steps.get('classifier')
            if classifier is None:
                return None, None

            # Unwrap to find tree model inside stacking/calibration wrappers
            tree_model = ModelService._unwrap_tree_model(classifier)
            if tree_model is None:
                logger.info("No tree model found for SHAP — skipping.")
                return None, None

            # Apply XGBoost/SHAP compatibility patch if needed
            if hasattr(tree_model, 'get_booster'):
                ModelService._patch_shap_xgboost_compat()

            explainer = shap.TreeExplainer(tree_model)

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

            # SHAP values: shape depends on model and SHAP version
            sv = explainer.shap_values(X_transformed)
            
            # For multi-output (list), index 1 = positive class
            if isinstance(sv, list):
                shap_vals = sv[1][0]
            else:
                # Numpy array
                if sv.ndim == 3:
                    # (n_samples, n_features, n_classes)
                    shap_vals = sv[0, :, 1]
                elif sv.ndim == 2:
                    # (n_samples, n_features)
                    shap_vals = sv[0]
                else:
                    shap_vals = sv

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
                
                # Kidney disease target encoding: ckd(disease)=0, notckd(healthy)=1
                # Normal target encoding: disease=1, healthy=0
                if disease_type == 'kidney':
                    direction = 'protective' if sv_val > 0 else 'risk'
                else:
                    direction = 'risk' if sv_val > 0 else 'protective'
                    
                contributions.append({
                    'feature':      clean_name(feature_names[idx]),
                    'contribution': round(float(sv_val), 4),
                    'direction':    direction,
                    'pct':          pct,
                })

            return contributions
        except Exception as e:
            logger.warning(f"SHAP computation failed for {disease_type}: {e}")
            return []

    # ── Feature engineering helpers ──────────────────────────────────────
    @staticmethod
    def _safe_float(val):
        if val in (None, ''):
            return np.nan
        try:
            return float(val)
        except (ValueError, TypeError):
            return np.nan

    @staticmethod
    def _safe_str(val):
        if val in (None, ''):
            return np.nan
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
        # New v2 interaction features
        df['BMI_GenHlth'] = df['BMI'] * df['GenHlth']
        df['Age_HighBP_HighChol'] = df['Age'] * df['HighBP'] * df['HighChol']
        df['PhysHlth_MentHlth'] = df['PhysHlth'] * df['MentHlth']
        df['BMI_PhysActivity'] = df['BMI'] * (1 - df['PhysActivity'])
        df['Income_Education'] = df['Income'] * df['Education']
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
        # Engineered features
        df['age_sq'] = df['age'] ** 2
        # New v2 interaction features
        df['chol_thalch_ratio'] = df['chol'] / (df['thalch'].replace(0, np.nan) + 1)
        df['trestbps_age'] = df['trestbps'] * df['age']
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
        # New v2 features
        df['Pressure_Sum'] = (
            df['Academic Pressure'] + df['Work Pressure'] + df['Financial Stress']
        )
        df['SleepDebt'] = np.maximum(0, 7 - sleep_hours)
        df['Suicidal_Pressure'] = (
            df['Have you ever had suicidal thoughts ?'] * df['Pressure_Sum']
        )
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
                
                # Confidence should be tied to the PREDICTED class probability
                # If prediction is 1 (Positive), confidence is pos_prob
                # If prediction is 0 (Negative), confidence is 1 - pos_prob
                confidence_prob = pos_prob if prediction == 1 else (1.0 - pos_prob)
                confidence  = round(confidence_prob * 100, 1)
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

            from ..constants import DISEASES
            disease_names = {k: v['name'] for k, v in DISEASES.items()}

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

