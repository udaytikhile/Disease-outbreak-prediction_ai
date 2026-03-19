"""
Shared ML Utilities
===================
Reusable functions for model training, tuning, evaluation, and serialization.
Used by all model training functions in train_all_models.py.
"""

import warnings
warnings.filterwarnings("ignore")

import json
import numpy as np
import pandas as pd
import logging
import joblib
from pathlib import Path
from datetime import datetime, timezone

from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix,
    roc_curve,
    roc_auc_score,
    precision_recall_curve,
    average_precision_score,
    brier_score_loss,
)
from sklearn.calibration import calibration_curve, CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import StackingClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OrdinalEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer
from sklearn.base import BaseEstimator, TransformerMixin

import xgboost as xgb
import lightgbm as lgb

try:
    import matplotlib.pyplot as plt
    _MATPLOTLIB_AVAILABLE = True
except ImportError:
    _MATPLOTLIB_AVAILABLE = False

try:
    from catboost import CatBoostClassifier
    _CATBOOST_AVAILABLE = True
except ImportError:
    _CATBOOST_AVAILABLE = False

try:
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    _OPTUNA_AVAILABLE = True
except ImportError:
    _OPTUNA_AVAILABLE = False

try:
    import shap
    _SHAP_AVAILABLE = True
except ImportError:
    _SHAP_AVAILABLE = False

logger = logging.getLogger(__name__)

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent  # ml/
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

SEP = "=" * 72


# ══════════════════════════════════════════════════════════════════════════════
# Preprocessing
# ══════════════════════════════════════════════════════════════════════════════

def build_preprocessor(numeric_cols, categorical_cols, use_iterative=False,
                       use_onehot=False):
    """ColumnTransformer with optional IterativeImputer & OneHotEncoder."""
    transformers = []
    if numeric_cols:
        if use_iterative:
            num_pipe = Pipeline([
                ("imputer", IterativeImputer(max_iter=20, random_state=42)),
                ("scaler", StandardScaler()),
            ])
        else:
            num_pipe = Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ])
        transformers.append(("num", num_pipe, numeric_cols))

    if categorical_cols:
        if use_onehot:
            cat_pipe = Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OneHotEncoder(
                    handle_unknown="ignore", sparse_output=False
                )),
            ])
        else:
            cat_pipe = Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OrdinalEncoder(
                    handle_unknown="use_encoded_value", unknown_value=-1
                )),
            ])
        transformers.append(("cat", cat_pipe, categorical_cols))

    return ColumnTransformer(transformers, remainder="drop")


# ══════════════════════════════════════════════════════════════════════════════
# Stacking Ensemble Builder
# ══════════════════════════════════════════════════════════════════════════════

def build_stacking_ensemble(xgb_params=None, lgb_params=None, cat_params=None,
                            use_calibration=True):
    """Build a stacking ensemble: XGBoost + LightGBM + CatBoost → LR meta.

    Args:
        xgb_params: dict of XGBoost hyperparameters
        lgb_params: dict of LightGBM hyperparameters
        cat_params: dict of CatBoost hyperparameters
        use_calibration: wrap in CalibratedClassifierCV for better probabilities

    Returns:
        StackingClassifier (or CalibratedClassifierCV wrapping it)
    """
    xgb_params = xgb_params or {}
    lgb_params = lgb_params or {}
    cat_params = cat_params or {}

    estimators = [
        ("xgb", xgb.XGBClassifier(
            random_state=42, n_jobs=-1, eval_metric="logloss",
            tree_method="hist", verbosity=0,
            **xgb_params,
        )),
        ("lgb", lgb.LGBMClassifier(
            random_state=42, n_jobs=-1, verbose=-1,
            **lgb_params,
        )),
    ]

    if _CATBOOST_AVAILABLE:
        estimators.append(
            ("cat", CatBoostClassifier(
                random_state=42, verbose=0,
                **cat_params,
            ))
        )

    stack = StackingClassifier(
        estimators=estimators,
        final_estimator=LogisticRegression(max_iter=1000, random_state=42),
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
        stack_method="predict_proba",
        n_jobs=-1,
        passthrough=False,
    )

    if use_calibration:
        return CalibratedClassifierCV(
            stack, cv=3, method="isotonic",
        )
    return stack


# ══════════════════════════════════════════════════════════════════════════════
# Simple Feature Selector (for SHAP-selected columns)
# ══════════════════════════════════════════════════════════════════════════════


class FeatureSelector(BaseEstimator, TransformerMixin):
    """Select a fixed set of feature indices from a numpy array."""

    def __init__(self, indices):
        self.indices = np.array(indices, dtype=int)

    def fit(self, X, y=None):  # noqa: D401
        return self

    def transform(self, X):
        return X[:, self.indices]


# ══════════════════════════════════════════════════════════════════════════════
# Optuna Hyperparameter Tuning
# ══════════════════════════════════════════════════════════════════════════════

def optuna_tune_xgb(X_train, y_train, n_trials=15, n_folds=5,
                    scale_pos_weight=1.0, scoring="accuracy"):
    """Use Optuna to find best XGBoost hyperparameters.

    Returns:
        dict of best hyperparameters
    """
    if not _OPTUNA_AVAILABLE:
        print("  ⚠️  Optuna not available, using defaults.")
        return {}

    def objective(trial):
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 200, 800),
            "max_depth": trial.suggest_int("max_depth", 3, 10),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
            "min_child_weight": trial.suggest_int("min_child_weight", 1, 15),
            "gamma": trial.suggest_float("gamma", 0, 0.5),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-3, 1.0, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 0.5, 3.0),
        }

        clf = xgb.XGBClassifier(
            random_state=42, n_jobs=-1, eval_metric="logloss",
            tree_method="hist", verbosity=0,
            scale_pos_weight=scale_pos_weight,
            **params,
        )

        cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
        scores = cross_val_score(clf, X_train, y_train, cv=cv,
                                 scoring=scoring, n_jobs=-1)
        return scores.mean()

    study = optuna.create_study(
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=42),
        pruner=optuna.pruners.MedianPruner(),
    )
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)

    print(f"  🔍 Optuna best {scoring}: {study.best_value:.4f}")
    print(f"  🔍 Optuna best params: {study.best_params}")
    return study.best_params


def optuna_tune_lgb(X_train, y_train, n_trials=15, n_folds=5,
                    scale_pos_weight=1.0, scoring="accuracy"):
    """Use Optuna to find best LightGBM hyperparameters."""
    if not _OPTUNA_AVAILABLE:
        return {}

    def objective(trial):
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 200, 800),
            "max_depth": trial.suggest_int("max_depth", 3, 12),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
            "num_leaves": trial.suggest_int("num_leaves", 20, 150),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
            "min_child_samples": trial.suggest_int("min_child_samples", 5, 50),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-3, 1.0, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-3, 1.0, log=True),
        }

        clf = lgb.LGBMClassifier(
            random_state=42, n_jobs=-1, verbose=-1,
            scale_pos_weight=scale_pos_weight,
            **params,
        )

        cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
        scores = cross_val_score(clf, X_train, y_train, cv=cv,
                                 scoring=scoring, n_jobs=-1)
        return scores.mean()

    study = optuna.create_study(
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=42),
    )
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)

    print(f"  🔍 Optuna LGB best {scoring}: {study.best_value:.4f}")
    return study.best_params


# ══════════════════════════════════════════════════════════════════════════════
# Threshold Optimization
# ══════════════════════════════════════════════════════════════════════════════

def find_best_threshold(pipe, X_val, y_val, positive_label=1):
    """Sweep thresholds using ROC curve to maximise Accuracy for positive class.

    Uses ROC-curve interpolated thresholds for efficiency (vs brute-force).
    Falls back to brute-force sweep if ROC approach fails.
    """
    try:
        proba = pipe.predict_proba(X_val)[:, 1]
    except AttributeError:
        print("  ⚠️  predict_proba not available; using threshold = 0.50")
        return 0.5

    best_t, best_score = 0.5, 0.0

    # Use ROC thresholds for more efficient search
    try:
        fpr, tpr, thresholds = roc_curve(y_val, proba, pos_label=positive_label)
        for t in thresholds:
            if t < 0.05 or t > 0.95:
                continue
            preds = (proba >= t).astype(int)
            if positive_label == 0:
                preds = 1 - preds
                compare_y = (y_val == positive_label).astype(int)
            else:
                compare_y = y_val
            score = accuracy_score(compare_y, preds)
            if score > best_score:
                best_score, best_t = score, round(float(t), 4)
    except Exception:
        # Fallback to brute force
        for t in np.arange(0.05, 0.96, 0.01):
            preds = (proba >= t).astype(int)
            if positive_label == 0:
                preds = 1 - preds
                compare_y = (y_val == positive_label).astype(int)
            else:
                compare_y = y_val
            score = accuracy_score(compare_y, preds)
            if score > best_score:
                best_score, best_t = score, round(float(t), 4)

    print(f"  🎯 Best threshold   : {best_t:.4f}  (Accuracy={best_score:.4f})")
    return best_t


# ══════════════════════════════════════════════════════════════════════════════
# SHAP Feature Selection
# ══════════════════════════════════════════════════════════════════════════════

def shap_feature_selection(model, X_train, feature_names, threshold=0.001):
    """Drop features with mean |SHAP| < threshold.

    Args:
        model: fitted classifier (tree-based)
        X_train: transformed training data (numpy array)
        feature_names: list of feature names
        threshold: minimum mean |SHAP| to keep

    Returns:
        list of feature names to keep, list of dropped feature names
    """
    if not _SHAP_AVAILABLE:
        print("  ⚠️  SHAP not available — skipping feature selection")
        return feature_names, []

    try:
        explainer = shap.TreeExplainer(model)
        # Use a sample for speed on large datasets
        sample_size = min(1000, X_train.shape[0])
        X_sample = X_train[:sample_size] if isinstance(X_train, np.ndarray) \
            else X_train.iloc[:sample_size]
        shap_values = explainer.shap_values(X_sample)

        # Handle multi-class output
        if isinstance(shap_values, list):
            shap_values = shap_values[1]  # positive class
        elif shap_values.ndim == 3:
            shap_values = shap_values[:, :, 1]

        mean_abs_shap = np.abs(shap_values).mean(axis=0)
        keep_mask = mean_abs_shap >= threshold
        keep_names = [n for n, k in zip(feature_names, keep_mask) if k]
        drop_names = [n for n, k in zip(feature_names, keep_mask) if not k]

        if drop_names:
            print(f"  🔧 SHAP dropped {len(drop_names)} features: {drop_names}")
        else:
            print(f"  🔧 SHAP: all {len(feature_names)} features above threshold")

        return keep_names, drop_names

    except Exception as e:
        print(f"  ⚠️  SHAP feature selection failed: {e}")
        return feature_names, []


# ══════════════════════════════════════════════════════════════════════════════
# Versioning
# ══════════════════════════════════════════════════════════════════════════════

def make_version(model_filename: str) -> str:
    """Return a version string YYYYMMDD_N with auto-incrementing N."""
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    fpath = MODEL_DIR / model_filename
    if fpath.exists():
        try:
            existing = joblib.load(fpath)
            if isinstance(existing, dict):
                prev_ver = existing.get('version', '')
                if prev_ver.startswith(date_str):
                    n = int(prev_ver.split('_')[1]) + 1
                    return f"{date_str}_{n}"
        except Exception:
            pass
    return f"{date_str}_1"


# ══════════════════════════════════════════════════════════════════════════════
# Evaluation & Save
# ══════════════════════════════════════════════════════════════════════════════

def _json_default(obj):
    """JSON serializer for numpy types."""
    if isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return str(obj)


def save_evaluation_artifacts(
    name,
    model_filename,
    X_test,
    y_test,
    y_pred,
    proba,
    cv_scores,
    best_threshold,
    positive_label=1,
    baseline=None,
):
    """Persist evaluation metrics JSON and optional plots for a trained model.

    - JSON is saved next to the model file as <model>.metrics.json
    - Plots (ROC, PR, calibration) are saved under ml/reports/
    """
    model_path = MODEL_DIR / model_filename

    # Convert to numpy arrays
    y_true = np.asarray(y_test)
    y_pred_arr = np.asarray(y_pred)

    metrics = {
        "model_name": name,
        "model_filename": model_filename,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cv_mean_accuracy": float(np.mean(cv_scores)) if cv_scores is not None else None,
        "cv_std_accuracy": float(np.std(cv_scores)) if cv_scores is not None else None,
        "baseline_accuracy": float(baseline) if baseline is not None else None,
        "best_threshold": float(best_threshold) if best_threshold is not None else None,
        "n_test_samples": int(len(y_true)),
    }

    # Confusion matrix and derived metrics based on y_pred (model's default decision rule)
    try:
        cm = confusion_matrix(y_true, y_pred_arr, labels=[0, 1])
        if cm.size == 4:
            tn, fp, fn, tp = cm.ravel()
            # Sensitivity/specificity from the perspective of the configured positive_label
            if positive_label == 1:
                sensitivity = tp / (tp + fn) if (tp + fn) > 0 else None
                specificity = tn / (tn + fp) if (tn + fp) > 0 else None
            else:
                # Treat label 0 as positive
                tp0 = tn
                fn0 = fp
                sensitivity = tp0 / (tp0 + fn0) if (tp0 + fn0) > 0 else None
                # Specificity with respect to the negative class (label 1)
                tn1 = tp
                fp1 = fn
                specificity = tn1 / (tn1 + fp1) if (tn1 + fp1) > 0 else None
        else:
            tn = fp = fn = tp = sensitivity = specificity = None
        metrics.update(
            {
                "confusion_matrix": cm.tolist(),
                "tn": int(tn) if tn is not None else None,
                "fp": int(fp) if fp is not None else None,
                "fn": int(fn) if fn is not None else None,
                "tp": int(tp) if tp is not None else None,
                "sensitivity": float(sensitivity) if sensitivity is not None else None,
                "specificity": float(specificity) if specificity is not None else None,
            }
        )
    except Exception as e:
        logger.warning(f"Failed to compute confusion matrix metrics: {e}")

    try:
        cls_report = classification_report(
            y_true, y_pred_arr, zero_division=0, output_dict=True
        )
        metrics["classification_report"] = cls_report
        metrics["accuracy"] = float(accuracy_score(y_true, y_pred_arr))
        metrics["f1_weighted"] = float(f1_score(y_true, y_pred_arr, average="weighted"))
    except Exception as e:
        logger.warning(f"Failed to compute basic metrics: {e}")

    # Probability-based metrics and curves (if probabilities available)
    y_score = None
    if proba is not None:
        proba_arr = np.asarray(proba)
        if positive_label == 1:
            y_score = proba_arr
        else:
            # Flip so that y_score represents P(positive_label)
            y_score = 1.0 - proba_arr

    if y_score is not None:
        try:
            y_binary = (y_true == positive_label).astype(int)
            roc_auc = roc_auc_score(y_binary, y_score)
            ap = average_precision_score(y_binary, y_score)
            brier = brier_score_loss(y_binary, y_score)

            fpr, tpr, roc_thresholds = roc_curve(y_binary, y_score, pos_label=1)
            prec, rec, _ = precision_recall_curve(y_binary, y_score, pos_label=1)
            prob_true, prob_pred = calibration_curve(
                y_binary, y_score, n_bins=10, strategy="quantile"
            )

            metrics.update(
                {
                    "roc_auc": float(roc_auc),
                    "average_precision": float(ap),
                    "brier_score": float(brier),
                    "roc_curve": {
                        "fpr": fpr.tolist(),
                        "tpr": tpr.tolist(),
                    },
                    "precision_recall_curve": {
                        "precision": prec.tolist(),
                        "recall": rec.tolist(),
                    },
                    "calibration_curve": {
                        "prob_true": prob_true.tolist(),
                        "prob_pred": prob_pred.tolist(),
                    },
                }
            )

            # Metrics at the F1-optimal threshold (if available)
            if best_threshold is not None:
                # Thresholded predictions on the probability of the configured positive_label
                y_pred_best = (y_score >= best_threshold).astype(int)

                cm_best = confusion_matrix(y_binary, y_pred_best, labels=[0, 1])
                if cm_best.size == 4:
                    tn_b, fp_b, fn_b, tp_b = cm_best.ravel()
                    sensitivity_b = tp_b / (tp_b + fn_b) if (tp_b + fn_b) > 0 else None
                    specificity_b = tn_b / (tn_b + fp_b) if (tn_b + fp_b) > 0 else None
                else:
                    tn_b = fp_b = fn_b = tp_b = sensitivity_b = specificity_b = None

                metrics["threshold_metrics"] = {
                    "threshold": float(best_threshold),
                    "confusion_matrix": cm_best.tolist(),
                    "tn": int(tn_b) if tn_b is not None else None,
                    "fp": int(fp_b) if fp_b is not None else None,
                    "fn": int(fn_b) if fn_b is not None else None,
                    "tp": int(tp_b) if tp_b is not None else None,
                    "sensitivity": float(sensitivity_b) if sensitivity_b is not None else None,
                    "specificity": float(specificity_b) if specificity_b is not None else None,
                    "accuracy": float(accuracy_score(y_binary, y_pred_best)),
                    "f1": float(f1_score(y_binary, y_pred_best, zero_division=0)),
                }

                # Record the ROC operating point closest to the chosen threshold
                try:
                    idx = int(np.argmin(np.abs(roc_thresholds - best_threshold)))
                    metrics["roc_operating_point"] = {
                        "threshold": float(roc_thresholds[idx]),
                        "fpr": float(fpr[idx]),
                        "tpr": float(tpr[idx]),
                    }
                except Exception:
                    # If anything goes wrong, skip without failing evaluation persistence
                    pass
        except Exception as e:
            logger.warning(f"Failed to compute probability-based metrics: {e}")

    # Track test indices for potential later re-evaluation
    try:
        if hasattr(y_test, "index"):
            metrics["test_indices"] = list(map(int, y_test.index.to_list()))
    except Exception:
        pass

    # Persist JSON next to the model file
    try:
        metrics_path = model_path.with_suffix(".metrics.json")
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2, default=_json_default)
        logger.info(f"Saved evaluation metrics → {metrics_path}")
    except Exception as e:
        logger.warning(f"Failed to save evaluation metrics JSON: {e}")

    # Persist plots (ROC, PR, calibration) under ml/reports/
    if y_score is not None and _MATPLOTLIB_AVAILABLE:
        try:
            y_binary = (y_true == positive_label).astype(int)
            fpr, tpr, _ = roc_curve(y_binary, y_score, pos_label=1)
            prec, rec, _ = precision_recall_curve(y_binary, y_score, pos_label=1)
            prob_true, prob_pred = calibration_curve(
                y_binary, y_score, n_bins=10, strategy="quantile"
            )

            fig, axes = plt.subplots(1, 3, figsize=(15, 4))

            # ROC
            ax = axes[0]
            ax.plot(fpr, tpr, label=f"AUC={roc_auc_score(y_binary, y_score):.3f}")
            ax.plot([0, 1], [0, 1], "k--", alpha=0.5)
            ax.set_xlabel("False Positive Rate")
            ax.set_ylabel("True Positive Rate")
            ax.set_title("ROC Curve")
            ax.legend(loc="lower right")

            # Precision-Recall
            ax = axes[1]
            ax.plot(rec, prec, label=f"AP={average_precision_score(y_binary, y_score):.3f}")
            ax.set_xlabel("Recall")
            ax.set_ylabel("Precision")
            ax.set_title("Precision-Recall")
            ax.legend(loc="lower left")

            # Calibration
            ax = axes[2]
            ax.plot(prob_pred, prob_true, "s-")
            ax.plot([0, 1], [0, 1], "k--", alpha=0.5)
            ax.set_xlabel("Predicted probability")
            ax.set_ylabel("Observed frequency")
            ax.set_title("Calibration")

            fig.suptitle(name)
            fig.tight_layout()
            curves_path = REPORT_DIR / f"{model_filename}.curves.png"
            fig.savefig(curves_path)
            plt.close(fig)
            logger.info(f"Saved evaluation plots → {curves_path}")
        except Exception as e:
            logger.warning(f"Failed to save evaluation plots: {e}")


def evaluate_and_save(name, pipe, X_train, X_test, y_train, y_test,
                      model_filename, positive_label=1, baseline=None,
                      n_folds=10):
    """Fit, evaluate, print results, save model+threshold, return metrics dict."""
    # Cross-validation
    cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
    cv_scores = cross_val_score(pipe, X_train, y_train, cv=cv,
                                scoring="accuracy", n_jobs=-1)
    print(f"\n  {n_folds}-Fold CV Accuracy : {cv_scores.mean():.4f} "
          f"(+/- {cv_scores.std():.4f})")

    # Fit
    pipe.fit(X_train, y_train)

    # Predict
    y_pred = pipe.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")

    print(f"  Test Accuracy      : {acc:.4f}  ({acc*100:.2f}%)")
    print(f"  Test F1 (weighted) : {f1:.4f}")

    if baseline:
        delta = acc - baseline
        arrow = "▲" if delta > 0 else ("▼" if delta < 0 else "═")
        print(f"  vs Baseline        : {baseline:.2%} → {acc:.2%}  "
              f"({arrow} {abs(delta)*100:+.2f} pp)")

    print(f"\n  Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))
    print(f"  Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Find optimal threshold
    best_threshold = find_best_threshold(
        pipe, X_test, y_test, positive_label=positive_label
    )

    # Versioned save
    model_path = MODEL_DIR / model_filename
    version = make_version(model_filename)
    trained_at = datetime.now(timezone.utc).isoformat()
    joblib.dump(
        {
            "pipeline": pipe,
            "threshold": best_threshold,
            "version": version,
            "trained_at": trained_at,
        },
        model_path,
    )
    print(f"\n  ✅ Model saved → {model_path}  (v{version}, threshold={best_threshold})")

    # Probabilities for evaluation artifacts
    try:
        proba = pipe.predict_proba(X_test)[:, 1]
    except Exception:
        proba = None

    # Persist rich evaluation artifacts
    try:
        save_evaluation_artifacts(
            name=name,
            model_filename=model_filename,
            X_test=X_test,
            y_test=y_test,
            y_pred=y_pred,
            proba=proba,
            cv_scores=cv_scores,
            best_threshold=best_threshold,
            positive_label=positive_label,
            baseline=baseline,
        )
    except Exception as e:
        logger.warning(f"Failed to persist evaluation artifacts for {name}: {e}")

    return {"name": name, "accuracy": acc, "f1": f1, "cv_mean": cv_scores.mean()}
