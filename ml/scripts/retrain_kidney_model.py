#!/usr/bin/env python3
"""
Retrain Kidney Disease Model
==============================
Standalone script that retrains the chronic kidney disease prediction model
and saves it as a versioned .pkl compatible with the current numpy/sklearn.

Usage:
    cd /home/udaylinux/Desktop/Disease-outbreak-prediction_ai
    python ml/scripts/retrain_kidney_model.py

Output:
    ml/models/kidney_disease_model.pkl  (versioned dict)
"""

import sys
import warnings
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import (
    train_test_split,
    cross_val_score,
    StratifiedKFold,
)
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix,
)
import joblib

# ── Path setup ───────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent          # ml/scripts/
ML_DIR     = SCRIPT_DIR.parent                        # ml/
DATA_DIR   = ML_DIR / "data"
MODEL_DIR  = ML_DIR / "models"

# Add ml/scripts to path so we can import shared utilities
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from utils import build_preprocessor, find_best_threshold, SEP
except ImportError:
    # Minimal fallback if utils.py can't be imported
    SEP = "=" * 72

    def build_preprocessor(numeric_cols, categorical_cols, use_iterative=False,
                           use_onehot=False):
        """Fallback preprocessor builder."""
        from sklearn.impute import SimpleImputer
        from sklearn.compose import ColumnTransformer

        try:
            from sklearn.experimental import enable_iterative_imputer  # noqa
            from sklearn.impute import IterativeImputer
            num_imputer = IterativeImputer(random_state=42, max_iter=20)
        except ImportError:
            num_imputer = SimpleImputer(strategy="median")

        num_pipeline = Pipeline([
            ("imputer", num_imputer),
            ("scaler", StandardScaler()),
        ])

        transformers = [("num", num_pipeline, numeric_cols)]

        if categorical_cols:
            from sklearn.preprocessing import OneHotEncoder
            cat_pipeline = Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
            ])
            transformers.append(("cat", cat_pipeline, categorical_cols))

        return ColumnTransformer(transformers)

    def find_best_threshold(pipe, X_val, y_val, positive_label=1):
        """Sweep thresholds to maximise F1 for positive class."""
        from sklearn.metrics import f1_score as _f1
        try:
            proba = pipe.predict_proba(X_val)[:, 1]
        except Exception:
            return 0.5

        best_t, best_f1 = 0.5, 0.0
        for t in np.arange(0.1, 0.91, 0.01):
            preds = (proba >= t).astype(int)
            if positive_label == 0:
                preds = 1 - preds
            f = _f1(y_val, preds, pos_label=positive_label, zero_division=0)
            if f > best_f1:
                best_f1 = f
                best_t = t
        return round(best_t, 2)


def make_version(filename: str) -> str:
    """Generate a version string like 'kidney_disease_model_20260312T2251'."""
    stem = Path(filename).stem
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M")
    return f"{stem}_{ts}"


def retrain():
    """Train and save the kidney disease model."""
    print(f"\n{SEP}")
    print("  🩺 Retraining: Chronic Kidney Disease Prediction Model")
    print(SEP)
    print(f"  Runtime: numpy={np.__version__}  sklearn={sklearn.__version__}")
    print(f"  Data   : {DATA_DIR / 'kidney_disease.csv'}")
    print(f"  Output : {MODEL_DIR / 'kidney_disease_model.pkl'}")
    print(SEP)

    # ── Load data ────────────────────────────────────────────────────────
    csv_path = DATA_DIR / "kidney_disease.csv"
    if not csv_path.exists():
        print(f"  ❌ Dataset not found: {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path)
    target = "classification"
    df[target] = df[target].str.strip()
    le = LabelEncoder()
    df[target] = le.fit_transform(df[target])  # ckd=0, notckd=1

    if "id" in df.columns:
        df.drop(columns=["id"], inplace=True)

    # ── Binary mappings for string columns ───────────────────────────────
    binary_mappings = {
        "yes": 1, "no": 0,
        "normal": 1, "abnormal": 0,
        "present": 1, "notpresent": 0,
        "good": 1, "poor": 0,
    }

    for col in df.columns:
        if col == target:
            continue
        if df[col].dtype == object:
            unique_vals = set(df[col].dropna().str.lower().str.strip().unique())
            mapping_keys = set(binary_mappings.keys())
            if unique_vals.intersection(mapping_keys):
                df[col] = df[col].str.strip().str.lower().map(binary_mappings)
            else:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    y = df[target]
    X = df.drop(columns=[target])

    print(f"  Dataset shape  : {X.shape}")
    print(f"  Nulls total    : {X.isnull().sum().sum()}")
    print(f"  Target classes : {dict(zip(*np.unique(y, return_counts=True)))}")

    # ── Data leakage check ───────────────────────────────────────────────
    print("\n  🔍 Data leakage check:")
    correlations = X.corrwith(y).abs().sort_values(ascending=False)
    high_corr = correlations[correlations > 0.9]
    if len(high_corr) > 0:
        print(f"  ⚠️  High correlation features (>0.9): {dict(high_corr)}")
        print("      Review for potential leakage — keeping for now.")
    else:
        print("  ✅ No features with >0.9 target correlation.")

    numeric_cols = X.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = X.select_dtypes(exclude=["number"]).columns.tolist()
    print(f"  Numeric features     : {len(numeric_cols)}")
    print(f"  Categorical features : {len(categorical_cols)}")

    # ── Preprocessing ────────────────────────────────────────────────────
    preprocessor = build_preprocessor(
        numeric_cols, categorical_cols,
        use_iterative=True,
    )

    # ── Model: Calibrated Random Forest ──────────────────────────────────
    base_rf = RandomForestClassifier(
        n_estimators=500,
        max_depth=None,
        min_samples_split=3,
        min_samples_leaf=1,
        max_features="sqrt",
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )

    calibrated_rf = CalibratedClassifierCV(
        base_rf, cv=5, method="isotonic",
    )

    pipe = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", calibrated_rf),
    ])

    # ── Train / test split ───────────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y,
    )

    # ── Cross-validation ─────────────────────────────────────────────────
    N_FOLDS = 10
    cv = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)
    print(f"\n  📈 {N_FOLDS}-Fold cross-validation...")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        cv_scores = cross_val_score(
            pipe, X_train, y_train, cv=cv, scoring="accuracy", n_jobs=-1,
        )
    print(f"  CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

    # ── Fit and evaluate ─────────────────────────────────────────────────
    print("\n  🏋️  Training final model...")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")

    print(f"  Test Accuracy      : {acc:.4f}  ({acc * 100:.2f}%)")
    print(f"  Test F1 (weighted) : {f1:.4f}")
    print(f"\n  Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))
    print(f"  Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # ── Optimal threshold ────────────────────────────────────────────────
    best_threshold = find_best_threshold(
        pipe, X_test, y_test, positive_label=0,  # ckd=0 is positive class
    )
    print(f"\n  Optimal threshold (for ckd=0): {best_threshold}")

    # ── Save model ───────────────────────────────────────────────────────
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODEL_DIR / "kidney_disease_model.pkl"
    version = make_version("kidney_disease_model.pkl")
    trained_at = datetime.now(timezone.utc).isoformat()

    artifact = {
        "pipeline": pipe,
        "threshold": best_threshold,
        "version": version,
        "trained_at": trained_at,
    }
    joblib.dump(artifact, model_path)

    print(f"\n  ✅ Model saved → {model_path}")
    print(f"     version    : {version}")
    print(f"     threshold  : {best_threshold}")
    print(f"     trained_at : {trained_at}")
    print(f"     numpy      : {np.__version__}")
    print(f"     sklearn    : {sklearn.__version__}")
    print(SEP)

    return {"accuracy": acc, "f1": f1, "cv_mean": cv_scores.mean()}


if __name__ == "__main__":
    retrain()
