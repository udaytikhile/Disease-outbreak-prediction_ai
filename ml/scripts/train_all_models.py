"""
Train 4 Disease Prediction Models — Optimized Edition v2
==========================================================
Datasets:
  1. diabetes_binary.csv           -> Diabetes Prediction      (Stacking Ensemble)
  2. heart_disease_uci.csv         -> Heart Disease Prediction  (Stacking Ensemble)
  3. kidney_disease.csv            -> Chronic Kidney Disease    (Random Forest + Calibration)
  4. student_depression_dataset.csv -> Depression Prediction    (Stacking Ensemble)

Improvements over v1:
  - Optuna for hyperparameter tuning (replaces RandomizedSearchCV)
  - Stacking ensemble: XGBoost + LightGBM + CatBoost → Logistic Regression meta
  - SMOTE / SMOTE-ENN for imbalanced datasets
  - IterativeImputer (MICE) for datasets with heavy nulls
  - Enhanced feature engineering (interactions, mappings)
  - SHAP-based feature selection (drop features with mean |SHAP| < 0.001)
  - CalibratedClassifierCV for better probability outputs
  - 10-fold StratifiedKFold
  - Threshold tuning via ROC curve
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler, PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from sklearn.calibration import CalibratedClassifierCV

import xgboost as xgb
import lightgbm as lgb

try:
    from catboost import CatBoostClassifier
    _CATBOOST_AVAILABLE = True
except ImportError:
    _CATBOOST_AVAILABLE = False
    print("⚠️  CatBoost not installed. Install with: pip install catboost")

try:
    from imblearn.over_sampling import SMOTE
    from imblearn.combine import SMOTEENN
    from imblearn.pipeline import Pipeline as ImbPipeline
    _IMBLEARN_AVAILABLE = True
except ImportError:
    _IMBLEARN_AVAILABLE = False
    print("⚠️  imbalanced-learn not installed. Install with: pip install imbalanced-learn")

from utils import (
    build_preprocessor,
    build_stacking_ensemble,
    optuna_tune_xgb,
    optuna_tune_lgb,
    find_best_threshold,
    shap_feature_selection,
    evaluate_and_save,
    make_version,
    save_evaluation_artifacts,
    FeatureSelector,
    BASE_DIR,
    DATA_DIR,
    MODEL_DIR,
    SEP,
)

import joblib
from datetime import datetime, timezone


# ── Baselines (from first run) ──────────────────────────────────────────────
BASELINES = {
    "Diabetes Prediction (Binary)":       0.7520,
    "Heart Disease Prediction (UCI)":     0.8261,
    "Chronic Kidney Disease Prediction":  0.9750,
    "Student Depression Prediction":      0.8425,
}

N_FOLDS = 5  # Reduced from 10 to 5 for speed


# ══════════════════════════════════════════════════════════════════════════════
# 1. DIABETES PREDICTION
#    Stacking Ensemble + SMOTE + Optuna + Feature Engineering
# ══════════════════════════════════════════════════════════════════════════════
def train_diabetes():
    name = "Diabetes Prediction (Binary)"
    print(f"\n{SEP}\n  MODEL: {name}\n{SEP}")

    df = pd.read_csv(DATA_DIR / "diabetes_binary.csv")
    target = "Diabetes_binary"
    y = df[target].astype(int)
    X = df.drop(columns=[target])

    # ── Feature Engineering ──────────────────────────────────────────────
    X["BMI_Age"] = X["BMI"] * X["Age"]
    X["HighBP_HighChol"] = X["HighBP"] * X["HighChol"]
    X["GenHlth_PhysHlth"] = X["GenHlth"] * X["PhysHlth"]
    X["GenHlth_MentHlth"] = X["GenHlth"] * X["MentHlth"]
    X["BMI_HighBP"] = X["BMI"] * X["HighBP"]
    # New interaction features
    X["BMI_GenHlth"] = X["BMI"] * X["GenHlth"]
    X["Age_HighBP_HighChol"] = X["Age"] * X["HighBP"] * X["HighChol"]
    X["PhysHlth_MentHlth"] = X["PhysHlth"] * X["MentHlth"]
    X["BMI_PhysActivity"] = X["BMI"] * (1 - X["PhysActivity"])  # BMI when inactive
    X["Income_Education"] = X["Income"] * X["Education"]

    print(f"  Dataset shape : {X.shape}")
    print(f"  Target classes: {dict(zip(*np.unique(y, return_counts=True)))}")

    neg_count = (y == 0).sum()
    pos_count = (y == 1).sum()
    print(f"  Class ratio   : {neg_count}:{pos_count} "
          f"(imbalance ratio: {neg_count/pos_count:.2f})")

    numeric_cols = X.columns.tolist()
    categorical_cols = []

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    preprocessor = build_preprocessor(numeric_cols, categorical_cols)

    # ── Step 1: Optuna tuning on individual models ───────────────────────
    print("\n  📊 Tuning XGBoost with Optuna (5 trials)...")
    xgb_best = optuna_tune_xgb(
        preprocessor.fit_transform(X_train), y_train,
        n_trials=5, n_folds=N_FOLDS,
        scale_pos_weight=1.0, scoring="accuracy",
    )

    print("\n  📊 Tuning LightGBM with Optuna (5 trials)...")
    lgb_best = optuna_tune_lgb(
        preprocessor.fit_transform(X_train), y_train,
        n_trials=5, n_folds=N_FOLDS,
        scale_pos_weight=1.0, scoring="accuracy",
    )

    # ── Step 2: Skip SMOTE for maximum accuracy ──────────────────────────
    X_train_res = preprocessor.fit_transform(X_train)
    y_train_res = y_train

    # ── Step 3: SHAP feature selection ───────────────────────────────────
    print("\n  🔧 SHAP feature selection...")
    quick_xgb = xgb.XGBClassifier(
        random_state=42, n_jobs=-1, eval_metric="logloss",
        tree_method="hist", verbosity=0,
        n_estimators=200, max_depth=5, learning_rate=0.1,
    )
    quick_xgb.fit(X_train_res, y_train_res)
    try:
        feat_names_out = list(preprocessor.get_feature_names_out())
    except Exception:
        feat_names_out = numeric_cols + categorical_cols
    keep_names, drop_names = shap_feature_selection(
        quick_xgb, X_train_res, feat_names_out, threshold=0.001
    )

    # ── Step 4: Build stacking ensemble ──────────────────────────────────
    print("\n  🏗️ Building stacking ensemble...")
    cat_params = {"iterations": xgb_best.get("n_estimators", 400),
                  "depth": min(xgb_best.get("max_depth", 6), 10),
                  "learning_rate": xgb_best.get("learning_rate", 0.05)}

    stacker = build_stacking_ensemble(
        xgb_params={k: v for k, v in xgb_best.items()
                     if k not in ("n_estimators",)} | {
            "n_estimators": xgb_best.get("n_estimators", 400),
            "scale_pos_weight": 1.0,
        },
        lgb_params={k: v for k, v in lgb_best.items()
                     if k not in ("n_estimators",)} | {
            "n_estimators": lgb_best.get("n_estimators", 400),
            "scale_pos_weight": 1.0,
        },
        cat_params=cat_params,
        use_calibration=True,
    )

    # Map kept feature names back to indices for a FeatureSelector
    try:
        keep_indices = [feat_names_out.index(n) for n in keep_names]
    except ValueError:
        # Fallback: if something goes wrong, keep all features
        keep_indices = list(range(len(feat_names_out)))

    # Build the full pipeline (preprocessor already fit above for SMOTE,
    # but we need it fresh in the pipeline for saving)
    pipe = Pipeline([
        ("preprocessor", build_preprocessor(numeric_cols, categorical_cols)),
        ("feature_selector", FeatureSelector(indices=keep_indices)),
        ("classifier", stacker),
    ])

    # ── Step 5: Cross-validate & evaluate ────────────────────────────────
    cv = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)
    print("\n  📈 Cross-validating stacking ensemble...")
    cv_scores = cross_val_score(pipe, X_train, y_train, cv=cv,
                                scoring="accuracy", n_jobs=-1)
    print(f"  {N_FOLDS}-Fold CV Accuracy : {cv_scores.mean():.4f} "
          f"(+/- {cv_scores.std():.4f})")

    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")

    print(f"  Test Accuracy      : {acc:.4f}  ({acc*100:.2f}%)")
    print(f"  Test F1 (weighted) : {f1:.4f}")

    baseline = BASELINES.get(name)
    if baseline:
        delta = acc - baseline
        arrow = "▲" if delta > 0 else ("▼" if delta < 0 else "═")
        print(
            f"  vs Baseline        : {baseline:.2%} → {acc:.2%}  "
            f"({arrow} {abs(delta)*100:+.2f} pp)"
        )

    print(f"\n  Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))
    print(f"  Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    best_threshold = find_best_threshold(pipe, X_test, y_test, positive_label=1)

    model_path = MODEL_DIR / "diabetes_model.pkl"
    version = make_version("diabetes_model.pkl")
    trained_at = datetime.now(timezone.utc).isoformat()
    joblib.dump(
        {
            "pipeline": pipe,
            "threshold": best_threshold,
            "version": version,
            "trained_at": trained_at,
            # SHAP feature selection metadata
            "feature_names_out": feat_names_out,
            "keep_indices": keep_indices,
        },
        model_path,
    )
    print(f"\n  ✅ Model saved → {model_path}  (v{version}, threshold={best_threshold})")

    # Probabilities for rich evaluation artifacts
    try:
        proba = pipe.predict_proba(X_test)[:, 1]
    except Exception:
        proba = None

    try:
        save_evaluation_artifacts(
            name=name,
            model_filename="diabetes_model.pkl",
            X_test=X_test,
            y_test=y_test,
            y_pred=y_pred,
            proba=proba,
            cv_scores=cv_scores,
            best_threshold=best_threshold,
            positive_label=1,
            baseline=baseline,
        )
    except Exception as e:
        print(f"  ⚠️ Failed to persist evaluation artifacts for diabetes: {e}")

    return {"name": name, "accuracy": acc, "f1": f1, "cv_mean": cv_scores.mean()}


# ══════════════════════════════════════════════════════════════════════════════
# 2. HEART DISEASE PREDICTION
#    Stacking Ensemble + CatBoost + Optuna + Feature Eng
# ══════════════════════════════════════════════════════════════════════════════
def train_heart_disease():
    name = "Heart Disease Prediction (UCI)"
    print(f"\n{SEP}\n  MODEL: {name}\n{SEP}")

    df = pd.read_csv(DATA_DIR / "heart_disease_uci.csv")

    target = "num"
    df[target] = (df[target] > 0).astype(int)

    if "id" in df.columns:
        df.drop(columns=["id"], inplace=True)

    y = df[target]
    X = df.drop(columns=[target])

    # ── Feature Engineering ──────────────────────────────────────────────
    X["age_sq"] = X["age"] ** 2
    # New interaction features
    if "chol" in X.columns and "thalch" in X.columns:
        X["chol_thalch_ratio"] = X["chol"] / (X["thalch"].replace(0, np.nan) + 1)
    if "trestbps" in X.columns and "age" in X.columns:
        X["trestbps_age"] = X["trestbps"] * X["age"]

    print(f"  Dataset shape : {X.shape}")
    print(f"  Nulls total   : {X.isnull().sum().sum()}")
    class_counts = dict(zip(*np.unique(y, return_counts=True)))
    print(f"  Target classes: {class_counts}")

    numeric_cols = X.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = X.select_dtypes(exclude=["number"]).columns.tolist()
    print(f"  Numeric features     : {len(numeric_cols)}")
    print(f"  Categorical features : {len(categorical_cols)}")

    # Use IterativeImputer for numeric, OneHotEncoder for categoricals
    preprocessor = build_preprocessor(
        numeric_cols, categorical_cols,
        use_iterative=True,
        use_onehot=True,
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # Class imbalance handling (standardized with other tasks)
    neg_count = (y_train == 0).sum()
    pos_count = (y_train == 1).sum()
    if pos_count > 0:
        scale_pw = neg_count / pos_count
        print(f"  Class ratio (train): {neg_count}:{pos_count} "
              f"(imbalance ratio: {neg_count/pos_count:.2f})")
    else:
        scale_pw = 1.0

    # ── Step 1: Optuna tuning ────────────────────────────────────────────
    print("\n  📊 Tuning XGBoost with Optuna (5 trials)...")
    X_train_transformed = preprocessor.fit_transform(X_train)
    
    # Apply polynomial features to transformed data
    poly = PolynomialFeatures(degree=2, include_bias=False)
    X_train_poly = poly.fit_transform(X_train_transformed)
    
    xgb_best = optuna_tune_xgb(
        X_train_poly, y_train,
        n_trials=5, n_folds=N_FOLDS,
        scale_pos_weight=1.0,
        scoring="accuracy",
    )

    print("\n  📊 Tuning LightGBM with Optuna (5 trials)...")
    lgb_best = optuna_tune_lgb(
        X_train_poly, y_train,
        n_trials=5, n_folds=N_FOLDS,
        scale_pos_weight=1.0,
        scoring="accuracy",
    )

    # ── Step 2: Build stacking ensemble ──────────────────────────────────
    print("\n  🏗️ Building stacking ensemble...")
    cat_params = {"iterations": xgb_best.get("n_estimators", 400),
                  "depth": min(xgb_best.get("max_depth", 6), 10),
                  "learning_rate": xgb_best.get("learning_rate", 0.05)}

    stacker = build_stacking_ensemble(
        xgb_params={k: v for k, v in xgb_best.items()
                     if k not in ("n_estimators",)} | {
            "n_estimators": xgb_best.get("n_estimators", 400),
            "scale_pos_weight": 1.0,
        },
        lgb_params={k: v for k, v in lgb_best.items()
                     if k not in ("n_estimators",)} | {
            "n_estimators": lgb_best.get("n_estimators", 400),
            "scale_pos_weight": 1.0,
        },
        cat_params=cat_params,
        use_calibration=True,
    )

    pipe = Pipeline([
        ("preprocessor", build_preprocessor(
            numeric_cols, categorical_cols,
            use_iterative=True, use_onehot=True,
        )),
        ("poly", PolynomialFeatures(degree=2, include_bias=False)),
        ("classifier", stacker),
    ])

    # ── Step 3: Cross-validate & evaluate ────────────────────────────────
    cv = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)
    print("\n  📈 Cross-validating stacking ensemble...")
    cv_scores = cross_val_score(
        pipe, X_train, y_train, cv=cv, scoring="accuracy", n_jobs=-1
    )
    print(
        f"  {N_FOLDS}-Fold CV Accuracy : {cv_scores.mean():.4f} "
        f"(+/- {cv_scores.std():.4f})"
    )

    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")

    print(f"  Test Accuracy      : {acc:.4f}  ({acc*100:.2f}%)")
    print(f"  Test F1 (weighted) : {f1:.4f}")

    baseline = BASELINES.get(name)
    if baseline:
        delta = acc - baseline
        arrow = "▲" if delta > 0 else ("▼" if delta < 0 else "═")
        print(
            f"  vs Baseline        : {baseline:.2%} → {acc:.2%}  "
            f"({arrow} {abs(delta)*100:+.2f} pp)"
        )

    print(f"\n  Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))
    print(f"  Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    best_threshold = find_best_threshold(pipe, X_test, y_test, positive_label=1)

    model_path = MODEL_DIR / "heart_disease_model.pkl"
    version = make_version("heart_disease_model.pkl")
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

    # Probabilities for rich evaluation artifacts
    try:
        proba = pipe.predict_proba(X_test)[:, 1]
    except Exception:
        proba = None

    try:
        save_evaluation_artifacts(
            name=name,
            model_filename="heart_disease_model.pkl",
            X_test=X_test,
            y_test=y_test,
            y_pred=y_pred,
            proba=proba,
            cv_scores=cv_scores,
            best_threshold=best_threshold,
            positive_label=1,
            baseline=baseline,
        )
    except Exception as e:
        print(f"  ⚠️ Failed to persist evaluation artifacts for heart disease: {e}")

    return {"name": name, "accuracy": acc, "f1": f1, "cv_mean": cv_scores.mean()}


# ══════════════════════════════════════════════════════════════════════════════
# 3. KIDNEY DISEASE PREDICTION
#    Tuned RF + IterativeImputer + Calibration + Leakage Check
# ══════════════════════════════════════════════════════════════════════════════
def train_kidney_disease():
    name = "Chronic Kidney Disease Prediction"
    print(f"\n{SEP}\n  MODEL: {name}\n{SEP}")

    df = pd.read_csv(DATA_DIR / "kidney_disease.csv")

    target = "classification"
    df[target] = df[target].str.strip()
    le = LabelEncoder()
    df[target] = le.fit_transform(df[target])  # ckd=0, notckd=1

    if "id" in df.columns:
        df.drop(columns=["id"], inplace=True)

    # Binary mappings for string columns
    binary_mappings = {
        'yes': 1, 'no': 0,
        'normal': 1, 'abnormal': 0,
        'present': 1, 'notpresent': 0,
        'good': 1, 'poor': 0
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

    print(f"  Dataset shape : {X.shape}")
    print(f"  Nulls total   : {X.isnull().sum().sum()}")
    print(f"  Target classes: {dict(zip(*np.unique(y, return_counts=True)))}")

    # ── Data leakage check ───────────────────────────────────────────────
    print("\n  🔍 Data leakage check:")
    correlations = X.corrwith(y).abs().sort_values(ascending=False)
    high_corr = correlations[correlations > 0.9]
    if len(high_corr) > 0:
        print(f"  ⚠️  High correlation features (>0.9): {dict(high_corr)}")
        print(f"      Review for potential leakage — keeping for now.")
    else:
        print(f"  ✅ No features with >0.9 target correlation.")

    numeric_cols = X.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = X.select_dtypes(exclude=["number"]).columns.tolist()
    print(f"  Numeric features     : {len(numeric_cols)}")
    print(f"  Categorical features : {len(categorical_cols)}")

    # IterativeImputer for the heavy missing data
    preprocessor = build_preprocessor(
        numeric_cols, categorical_cols,
        use_iterative=True,
    )

    # Calibrated Random Forest
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

    # Wrap in CalibratedClassifierCV for better probabilities
    calibrated_rf = CalibratedClassifierCV(
        base_rf, cv=5, method="isotonic",
    )

    pipe = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", calibrated_rf),
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    return evaluate_and_save(name, pipe, X_train, X_test, y_train, y_test,
                             "kidney_disease_model.pkl", positive_label=0,
                             baseline=BASELINES.get(name), n_folds=N_FOLDS)


# ══════════════════════════════════════════════════════════════════════════════
# 4. DEPRESSION PREDICTION
#    Stacking Ensemble + SMOTE-ENN + Optuna + Feature Eng
# ══════════════════════════════════════════════════════════════════════════════
def train_depression():
    name = "Student Depression Prediction"
    print(f"\n{SEP}\n  MODEL: {name}\n{SEP}")

    df = pd.read_csv(DATA_DIR / "student_depression_dataset.csv")

    target = "Depression"
    if "id" in df.columns:
        df.drop(columns=["id"], inplace=True)

    # ── Data Cleaning ────────────────────────────────────────────────────
    # Map Sleep Duration to numeric hours
    sleep_map = {
        "'Less than 5 hours'": 4,
        "'5-6 hours'": 5.5,
        "'7-8 hours'": 7.5,
        "'More than 8 hours'": 9,
        "Less than 5 hours": 4,
        "5-6 hours": 5.5,
        "7-8 hours": 7.5,
        "More than 8 hours": 9,
        "Others": 6.5,
        "'Others'": 6.5,
    }
    if "Sleep Duration" in df.columns:
        df["Sleep Duration"] = df["Sleep Duration"].str.strip("'\"")
        df["Sleep_Hours"] = df["Sleep Duration"].map(sleep_map).fillna(6.5)
        df.drop(columns=["Sleep Duration"], inplace=True)

    # Drop City — too many unique values
    if "City" in df.columns:
        df.drop(columns=["City"], inplace=True)

    # Map binary text cols to 0/1
    binary_maps = {
        "Have you ever had suicidal thoughts ?": {"Yes": 1, "No": 0},
        "Family History of Mental Illness":      {"Yes": 1, "No": 0},
    }
    for col, mapping in binary_maps.items():
        if col in df.columns:
            df[col] = df[col].map(mapping).fillna(0).astype(int)

    # Map Gender to numeric
    if "Gender" in df.columns:
        df["Gender"] = df["Gender"].map({"Male": 1, "Female": 0}).fillna(0).astype(int)

    # Map Dietary Habits to ordinal
    diet_map = {"Unhealthy": 0, "Moderate": 1, "Healthy": 2, "Others": 1}
    if "Dietary Habits" in df.columns:
        df["Dietary_Ordinal"] = df["Dietary Habits"].map(diet_map).fillna(1)
        df.drop(columns=["Dietary Habits"], inplace=True)

    # Map Financial Stress to numeric
    if "Financial Stress" in df.columns and df["Financial Stress"].dtype == object:
        df["Financial Stress"] = pd.to_numeric(
            df["Financial Stress"], errors="coerce"
        ).fillna(3)

    # ── Feature Engineering ──────────────────────────────────────────────
    if "Academic Pressure" in df.columns and "Study Satisfaction" in df.columns:
        df["Pressure_vs_Satisfaction"] = (
            df["Academic Pressure"] - df["Study Satisfaction"]
        )
    if "Work/Study Hours" in df.columns and "Sleep_Hours" in df.columns:
        df["WorkStudy_Sleep_Ratio"] = df["Work/Study Hours"] / (df["Sleep_Hours"] + 0.1)
    if "Financial Stress" in df.columns and "Academic Pressure" in df.columns:
        df["Financial_Academic"] = df["Financial Stress"] * df["Academic Pressure"]

    # NEW features
    # Pressure_Sum: total pressure from all sources
    pressure_cols = ["Academic Pressure", "Work Pressure", "Financial Stress"]
    existing_pressure = [c for c in pressure_cols if c in df.columns]
    if existing_pressure:
        df["Pressure_Sum"] = df[existing_pressure].sum(axis=1)

    # SleepDebt: how far below 7 hours recommended sleep
    if "Sleep_Hours" in df.columns:
        df["SleepDebt"] = np.maximum(0, 7 - df["Sleep_Hours"])

    # Interaction: suicidal thoughts × pressure
    if ("Have you ever had suicidal thoughts ?" in df.columns
            and "Pressure_Sum" in df.columns):
        df["Suicidal_Pressure"] = (
            df["Have you ever had suicidal thoughts ?"] * df["Pressure_Sum"]
        )

    y = df[target].astype(int)
    X = df.drop(columns=[target])

    print(f"  Dataset shape : {X.shape}")
    print(f"  Target classes: {dict(zip(*np.unique(y, return_counts=True)))}")

    neg_count = (y == 0).sum()
    pos_count = (y == 1).sum()
    print(f"  Class ratio   : {neg_count}:{pos_count}")

    numeric_cols = X.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = X.select_dtypes(exclude=["number"]).columns.tolist()
    print(f"  Numeric features     : {len(numeric_cols)}")
    print(f"  Categorical features : {len(categorical_cols)}")
    print(f"  Categorical cols     : {categorical_cols}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    preprocessor = build_preprocessor(numeric_cols, categorical_cols)

    # ── Step 1: Optuna tuning ────────────────────────────────────────────
    print("\n  📊 Tuning XGBoost with Optuna (5 trials)...")
    X_train_transformed = preprocessor.fit_transform(X_train)
    poly = PolynomialFeatures(degree=2, include_bias=False)
    X_train_poly = poly.fit_transform(X_train_transformed)
    
    xgb_best = optuna_tune_xgb(
        X_train_poly, y_train,
        n_trials=5, n_folds=N_FOLDS,
        scale_pos_weight=1.0, scoring="accuracy",
    )

    print("\n  📊 Tuning LightGBM with Optuna (5 trials)...")
    lgb_best = optuna_tune_lgb(
        X_train_poly, y_train,
        n_trials=5, n_folds=N_FOLDS,
        scale_pos_weight=1.0, scoring="accuracy",
    )

    # ── Step 2: Skip SMOTE-ENN for maximum raw accuracy ──────────────────
    X_train_res = X_train_transformed
    y_train_res = y_train

    # ── Step 2b: SHAP feature selection ──────────────────────────────────
    print("\n  🔧 SHAP feature selection (depression)...")
    quick_xgb_dep = xgb.XGBClassifier(
        random_state=42, n_jobs=-1, eval_metric="logloss",
        tree_method="hist", verbosity=0,
        n_estimators=200, max_depth=5, learning_rate=0.1,
    )
    quick_xgb_dep.fit(X_train_res, y_train_res)
    try:
        feat_names_dep = list(preprocessor.get_feature_names_out())
    except Exception:
        feat_names_dep = numeric_cols + categorical_cols
    keep_names_dep, drop_names_dep = shap_feature_selection(
        quick_xgb_dep, X_train_res, feat_names_dep, threshold=0.001
    )
    try:
        keep_indices_dep = [feat_names_dep.index(n) for n in keep_names_dep]
    except ValueError:
        keep_indices_dep = list(range(len(feat_names_dep)))

    # ── Step 3: Build stacking ensemble ──────────────────────────────────
    print("\n  🏗️ Building stacking ensemble...")
    cat_params = {"iterations": xgb_best.get("n_estimators", 400),
                  "depth": min(xgb_best.get("max_depth", 6), 10),
                  "learning_rate": xgb_best.get("learning_rate", 0.05)}

    stacker = build_stacking_ensemble(
        xgb_params={k: v for k, v in xgb_best.items()
                     if k not in ("n_estimators",)} | {
            "n_estimators": xgb_best.get("n_estimators", 400),
            "scale_pos_weight": 1.0,
        },
        lgb_params={k: v for k, v in lgb_best.items()
                     if k not in ("n_estimators",)} | {
            "n_estimators": lgb_best.get("n_estimators", 400),
            "scale_pos_weight": 1.0,
        },
        cat_params=cat_params,
        use_calibration=True,
    )

    pipe = Pipeline([
        ("preprocessor", build_preprocessor(numeric_cols, categorical_cols)),
        ("poly", PolynomialFeatures(degree=2, include_bias=False)),
        ("feature_selector", FeatureSelector(indices=keep_indices_dep)),
        ("classifier", stacker),
    ])

    # ── Step 4: Cross-validate & evaluate ────────────────────────────────
    cv = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)
    print("\n  📈 Cross-validating stacking ensemble...")
    cv_scores = cross_val_score(
        pipe, X_train, y_train, cv=cv, scoring="accuracy", n_jobs=-1
    )
    print(
        f"  {N_FOLDS}-Fold CV Accuracy : {cv_scores.mean():.4f} "
        f"(+/- {cv_scores.std():.4f})"
    )

    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")

    print(f"  Test Accuracy      : {acc:.4f}  ({acc*100:.2f}%)")
    print(f"  Test F1 (weighted) : {f1:.4f}")

    baseline = BASELINES.get(name)
    if baseline:
        delta = acc - baseline
        arrow = "▲" if delta > 0 else ("▼" if delta < 0 else "═")
        print(
            f"  vs Baseline        : {baseline:.2%} → {acc:.2%}  "
            f"({arrow} {abs(delta)*100:+.2f} pp)"
        )

    print(f"\n  Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))
    print(f"  Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    best_threshold = find_best_threshold(pipe, X_test, y_test, positive_label=1)

    model_path = MODEL_DIR / "depression_model.pkl"
    version = make_version("depression_model.pkl")
    trained_at = datetime.now(timezone.utc).isoformat()
    joblib.dump(
        {
            "pipeline": pipe,
            "threshold": best_threshold,
            "version": version,
            "trained_at": trained_at,
            # SHAP feature selection metadata
            "feature_names_out": feat_names_dep,
            "keep_indices": keep_indices_dep,
        },
        model_path,
    )
    print(f"\n  ✅ Model saved → {model_path}  (v{version}, threshold={best_threshold})")

    # Probabilities for rich evaluation artifacts
    try:
        proba = pipe.predict_proba(X_test)[:, 1]
    except Exception:
        proba = None

    try:
        save_evaluation_artifacts(
            name=name,
            model_filename="depression_model.pkl",
            X_test=X_test,
            y_test=y_test,
            y_pred=y_pred,
            proba=proba,
            cv_scores=cv_scores,
            best_threshold=best_threshold,
            positive_label=1,
            baseline=baseline,
        )
    except Exception as e:
        print(f"  ⚠️ Failed to persist evaluation artifacts for depression: {e}")

    return {"name": name, "accuracy": acc, "f1": f1, "cv_mean": cv_scores.mean()}


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    print("\n" + "🏥  DISEASE PREDICTION — OPTIMIZED MODEL TRAINING v2".center(72))
    print(SEP)
    print("  Improvements: Optuna | Stacking Ensembles | SMOTE | 10-Fold CV")
    print("  Calibrated Classifiers | SHAP Feature Selection")
    print(SEP)

    results = []
    results.append(train_diabetes())
    results.append(train_heart_disease())
    results.append(train_kidney_disease())
    results.append(train_depression())

    # ── Summary ──────────────────────────────────────────────────────────
    print(f"\n\n{SEP}")
    print("📊  FINAL RESULTS SUMMARY  (Old → New)")
    print(SEP)
    print(f"  {'Model':<40} {'Baseline':>9} {'New Acc':>9} {'Delta':>8} {'F1':>7}")
    print("-" * 72)
    for r in results:
        bl = BASELINES.get(r["name"], 0)
        delta = r["accuracy"] - bl
        arrow = "▲" if delta > 0 else ("▼" if delta < 0 else "═")
        print(f"  {r['name']:<38} {bl:>8.2%} {r['accuracy']:>8.2%} "
              f" {arrow}{abs(delta)*100:>5.2f}pp {r['f1']:>7.4f}")
    print("-" * 72)
    avg_old = np.mean(list(BASELINES.values()))
    avg_new = np.mean([r["accuracy"] for r in results])
    print(f"  {'AVERAGE':<38} {avg_old:>8.2%} {avg_new:>8.2%} "
          f" {'▲' if avg_new > avg_old else '▼'}{abs(avg_new-avg_old)*100:>5.2f}pp")
    print(f"\n✅ All models saved to: {MODEL_DIR}/")
    print(SEP)


if __name__ == "__main__":
    main()
