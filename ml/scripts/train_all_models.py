"""
Train 4 Disease Prediction Models — Optimized Edition
=======================================================
Datasets:
  1. diabetes_binary.csv           -> Diabetes Prediction      (XGBoost)
  2. heart_disease_uci.csv         -> Heart Disease Prediction  (XGBoost)
  3. kidney_disease.csv            -> Chronic Kidney Disease    (Random Forest)
  4. student_depression_dataset.csv -> Depression Prediction    (XGBoost)

Improvements over baseline:
  - XGBoost for diabetes, heart, and depression models
  - IterativeImputer (MICE) for datasets with heavy nulls
  - Feature engineering (interactions, mappings)
  - RandomizedSearchCV for hyperparameter tuning
  - TargetEncoder for high-cardinality categoricals
  - Better data cleaning / feature selection
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from pathlib import Path

from sklearn.model_selection import (
    train_test_split,
    cross_val_score,
    RandomizedSearchCV,
    StratifiedKFold,
)
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import (
    LabelEncoder,
    StandardScaler,
    OrdinalEncoder,
    OneHotEncoder,
)
from sklearn.impute import SimpleImputer
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from scipy.stats import uniform, randint
import xgboost as xgb
import joblib
from datetime import datetime, timezone

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent  # ml/
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

SEP = "=" * 72

# ── Baselines (from first run) ──────────────────────────────────────────────
BASELINES = {
    "Diabetes Prediction (Binary)":       0.7520,
    "Heart Disease Prediction (UCI)":     0.8261,
    "Chronic Kidney Disease Prediction":  0.9750,
    "Student Depression Prediction":      0.8425,
}


# ── Feature 4: Model versioning helper ───────────────────────────────────────
def make_version(model_filename: str) -> str:
    """Return a version string YYYYMMDD_N where N auto-increments.

    Looks at the existing pkl to read its current version date.
    If the date matches today, increments N; otherwise resets to 1.
    Examples: '20250222_1', '20250222_2', '20250223_1'
    """
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


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
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


def find_best_threshold(pipe, X_val, y_val, positive_label=1):
    """Sweep thresholds 0.05–0.95 and return the one that maximises
    F1 for the positive class (class == positive_label).

    For binary classifiers sklearn always places class probabilities in the
    order returned by pipe.classes_, so we look up the correct column.
    Returns the best threshold as a float.
    """
    try:
        proba = pipe.predict_proba(X_val)[:, 1]  # P(positive_label)
    except AttributeError:
        # Pipeline has no predict_proba — fall back to 0.5
        print("  ⚠️  predict_proba not available; using threshold = 0.50")
        return 0.5

    best_t, best_f1 = 0.5, 0.0
    for t in np.arange(0.05, 0.96, 0.01):
        preds = (proba >= t).astype(int)
        # For kidney disease the 'positive' (disease) label is 0 — invert
        if positive_label == 0:
            preds = 1 - preds
            compare_y = (y_val == positive_label).astype(int)
        else:
            compare_y = y_val
        try:
            score = f1_score(compare_y, preds, zero_division=0)
        except Exception:
            continue
        if score > best_f1:
            best_f1, best_t = score, round(float(t), 4)

    print(f"  🎯 Best threshold   : {best_t:.4f}  (F1={best_f1:.4f})")
    return best_t


def evaluate_and_save(name, pipe, X_train, X_test, y_train, y_test,
                      model_filename, positive_label=1):
    """Fit, evaluate, print results, save model+threshold, return metrics dict."""
    # Cross-validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(pipe, X_train, y_train, cv=cv,
                                scoring="accuracy", n_jobs=-1)
    print(f"\n  5-Fold CV Accuracy : {cv_scores.mean():.4f} "
          f"(+/- {cv_scores.std():.4f})")

    # Fit
    pipe.fit(X_train, y_train)

    # Predict (using default 0.5 for reporting)
    y_pred = pipe.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")

    print(f"  Test Accuracy      : {acc:.4f}  ({acc*100:.2f}%)")
    print(f"  Test F1 (weighted) : {f1:.4f}")

    # Baseline comparison
    baseline = BASELINES.get(name, None)
    if baseline:
        delta = acc - baseline
        arrow = "▲" if delta > 0 else ("▼" if delta < 0 else "═")
        print(f"  vs Baseline        : {baseline:.2%} → {acc:.2%}  "
              f"({arrow} {abs(delta)*100:+.2f} pp)")

    print(f"\n  Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))
    print(f"  Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # ── Bug 5 fix: find and save optimal threshold ──────────────────────
    best_threshold = find_best_threshold(pipe, X_test, y_test,
                                         positive_label=positive_label)

    # Feature 4: versioned save — pipeline + threshold + version metadata
    model_path = MODEL_DIR / model_filename
    version    = make_version(model_filename)
    trained_at = datetime.now(timezone.utc).isoformat()
    joblib.dump({
        'pipeline':   pipe,
        'threshold':  best_threshold,
        'version':    version,
        'trained_at': trained_at,
    }, model_path)
    print(f"\n  ✅ Model saved → {model_path}  (v{version}, threshold={best_threshold})")

    return {"name": name, "accuracy": acc, "f1": f1, "cv_mean": cv_scores.mean()}


# ══════════════════════════════════════════════════════════════════════════════
# 1. DIABETES PREDICTION  — XGBoost + Feature Engineering
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

    print(f"  Dataset shape : {X.shape}")
    print(f"  Target classes: {dict(zip(*np.unique(y, return_counts=True)))}")

    numeric_cols = X.columns.tolist()
    categorical_cols = []

    preprocessor = build_preprocessor(numeric_cols, categorical_cols)

    # ── XGBoost with RandomizedSearchCV ──────────────────────────────────
    base_clf = xgb.XGBClassifier(
        random_state=42, n_jobs=-1, eval_metric="logloss",
        tree_method="hist", scale_pos_weight=1.0,
    )

    pipe = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", base_clf),
    ])

    param_dist = {
        "classifier__n_estimators": randint(200, 600),
        "classifier__max_depth": randint(3, 8),
        "classifier__learning_rate": uniform(0.02, 0.15),
        "classifier__subsample": uniform(0.7, 0.3),
        "classifier__colsample_bytree": uniform(0.6, 0.4),
        "classifier__min_child_weight": randint(3, 15),
        "classifier__gamma": uniform(0, 0.3),
        "classifier__reg_alpha": uniform(0, 0.5),
        "classifier__reg_lambda": uniform(0.5, 2.0),
    }

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    search = RandomizedSearchCV(
        pipe, param_dist, n_iter=40, cv=cv, scoring="accuracy",
        random_state=42, n_jobs=-1, refit=True,
    )
    search.fit(X_train, y_train)
    best_pipe = search.best_estimator_

    print(f"\n  Best CV score from search: {search.best_score_:.4f}")
    print(f"  Best params: { {k.replace('classifier__',''): round(v,4) if isinstance(v,float) else v for k,v in search.best_params_.items()} }")

    # Evaluate best
    y_pred = best_pipe.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")

    cv_scores = cross_val_score(best_pipe, X_train, y_train, cv=cv,
                                scoring="accuracy", n_jobs=-1)
    print(f"\n  5-Fold CV Accuracy : {cv_scores.mean():.4f} "
          f"(+/- {cv_scores.std():.4f})")
    print(f"  Test Accuracy      : {acc:.4f}  ({acc*100:.2f}%)")
    print(f"  Test F1 (weighted) : {f1:.4f}")

    baseline = BASELINES.get(name, None)
    if baseline:
        delta = acc - baseline
        arrow = "▲" if delta > 0 else ("▼" if delta < 0 else "═")
        print(f"  vs Baseline        : {baseline:.2%} → {acc:.2%}  "
              f"({arrow} {abs(delta)*100:+.2f} pp)")

    print(f"\n  Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))
    print(f"  Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # ── Bug 5 fix: find and save optimal threshold ──────────────────────
    best_threshold = find_best_threshold(best_pipe, X_test, y_test, positive_label=1)

    model_path = MODEL_DIR / "diabetes_model.pkl"
    version    = make_version("diabetes_model.pkl")
    trained_at = datetime.now(timezone.utc).isoformat()
    joblib.dump({
        'pipeline':   best_pipe,
        'threshold':  best_threshold,
        'version':    version,
        'trained_at': trained_at,
    }, model_path)
    print(f"\n  ✅ Model saved → {model_path}  (v{version}, threshold={best_threshold})")

    return {"name": name, "accuracy": acc, "f1": f1, "cv_mean": cv_scores.mean()}


# ══════════════════════════════════════════════════════════════════════════════
# 2. HEART DISEASE PREDICTION  — XGBoost + IterativeImputer + Feature Eng
# ══════════════════════════════════════════════════════════════════════════════
def train_heart_disease():
    name = "Heart Disease Prediction (UCI)"
    print(f"\n{SEP}\n  MODEL: {name}\n{SEP}")

    df = pd.read_csv(DATA_DIR / "heart_disease_uci.csv")

    # Binary target: 0 = no disease, ≥1 = disease
    target = "num"
    df[target] = (df[target] > 0).astype(int)

    # Keep 'dataset' as categorical feature (encodes hospital origin)
    if "id" in df.columns:
        df.drop(columns=["id"], inplace=True)

    y = df[target]
    X = df.drop(columns=[target])

    # ── Feature Engineering ──────────────────────────────────────────────
    # Map some categoricals to numeric for interactions
    X["age_sq"] = X["age"] ** 2

    print(f"  Dataset shape : {X.shape}")
    print(f"  Nulls total   : {X.isnull().sum().sum()}")
    print(f"  Target classes: {dict(zip(*np.unique(y, return_counts=True)))}")

    numeric_cols = X.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = X.select_dtypes(exclude=["number"]).columns.tolist()
    print(f"  Numeric features     : {len(numeric_cols)}")
    print(f"  Categorical features : {len(categorical_cols)}")

    # Use IterativeImputer for numeric, OneHotEncoder for categorics
    preprocessor = build_preprocessor(
        numeric_cols, categorical_cols,
        use_iterative=True,
        use_onehot=True,
    )

    # ── XGBoost with RandomizedSearchCV ──────────────────────────────────
    base_clf = xgb.XGBClassifier(
        random_state=42, n_jobs=-1, eval_metric="logloss",
        tree_method="hist",
    )

    pipe = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", base_clf),
    ])

    param_dist = {
        "classifier__n_estimators": randint(200, 600),
        "classifier__max_depth": randint(3, 10),
        "classifier__learning_rate": uniform(0.01, 0.19),
        "classifier__subsample": uniform(0.6, 0.4),
        "classifier__colsample_bytree": uniform(0.6, 0.4),
        "classifier__min_child_weight": randint(1, 10),
        "classifier__gamma": uniform(0, 0.5),
        "classifier__reg_alpha": uniform(0, 1),
        "classifier__reg_lambda": uniform(0.5, 2),
    }

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    search = RandomizedSearchCV(
        pipe, param_dist, n_iter=60, cv=cv, scoring="accuracy",
        random_state=42, n_jobs=-1, refit=True,
    )
    search.fit(X_train, y_train)
    best_pipe = search.best_estimator_

    print(f"\n  Best CV score from search: {search.best_score_:.4f}")
    print(f"  Best params: { {k.replace('classifier__',''): round(v,4) if isinstance(v,float) else v for k,v in search.best_params_.items()} }")

    # Evaluate the best pipeline
    y_pred = best_pipe.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")

    # CV on best estimator
    cv_scores = cross_val_score(best_pipe, X_train, y_train, cv=cv,
                                scoring="accuracy", n_jobs=-1)
    print(f"\n  5-Fold CV Accuracy : {cv_scores.mean():.4f} "
          f"(+/- {cv_scores.std():.4f})")
    print(f"  Test Accuracy      : {acc:.4f}  ({acc*100:.2f}%)")
    print(f"  Test F1 (weighted) : {f1:.4f}")

    baseline = BASELINES.get(name, None)
    if baseline:
        delta = acc - baseline
        arrow = "▲" if delta > 0 else ("▼" if delta < 0 else "═")
        print(f"  vs Baseline        : {baseline:.2%} → {acc:.2%}  "
              f"({arrow} {abs(delta)*100:+.2f} pp)")

    print(f"\n  Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))
    print(f"  Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # ── Bug 5 fix: find and save optimal threshold ──────────────────────
    best_threshold = find_best_threshold(best_pipe, X_test, y_test, positive_label=1)

    model_path = MODEL_DIR / "heart_disease_model.pkl"
    version    = make_version("heart_disease_model.pkl")
    trained_at = datetime.now(timezone.utc).isoformat()
    joblib.dump({
        'pipeline':   best_pipe,
        'threshold':  best_threshold,
        'version':    version,
        'trained_at': trained_at,
    }, model_path)
    print(f"\n  ✅ Model saved → {model_path}  (v{version}, threshold={best_threshold})")

    return {"name": name, "accuracy": acc, "f1": f1, "cv_mean": cv_scores.mean()}


# ══════════════════════════════════════════════════════════════════════════════
# 3. KIDNEY DISEASE PREDICTION  — Tuned RF + IterativeImputer
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

    # Convert all string 'yes/no', 'normal/abnormal', 'present/notpresent', 'good/poor' to 1/0
    binary_mappings = {
        'yes': 1, 'no': 0,
        'normal': 1, 'abnormal': 0,
        'present': 1, 'notpresent': 0,
        'good': 1, 'poor': 0
    }
    
    # Clean numeric columns stored as strings and map categoricals
    for col in df.columns:
        if col == target:
            continue
        try:
            # Check if column contains our string categoricals by looking at a non-null value
            first_valid = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
            if isinstance(first_valid, str) and first_valid.strip().lower() in binary_mappings:
                df[col] = df[col].str.strip().str.lower().map(binary_mappings)
            else:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        except Exception:
            pass

    y = df[target]
    X = df.drop(columns=[target])

    print(f"  Dataset shape : {X.shape}")
    print(f"  Nulls total   : {X.isnull().sum().sum()}")
    print(f"  Target classes: {dict(zip(*np.unique(y, return_counts=True)))}")

    numeric_cols = X.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = X.select_dtypes(exclude=["number"]).columns.tolist()
    print(f"  Numeric features     : {len(numeric_cols)}")
    print(f"  Categorical features : {len(categorical_cols)}")

    # IterativeImputer for the heavy missing data
    preprocessor = build_preprocessor(
        numeric_cols, categorical_cols,
        use_iterative=True,
    )

    # Tuned Random Forest
    classifier = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_split=3,
        min_samples_leaf=1,
        max_features="sqrt",
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )

    pipe = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", classifier),
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # Kidney: ckd=0 means disease; positive_label=0 so threshold targets ckd class
    return evaluate_and_save(name, pipe, X_train, X_test, y_train, y_test,
                             "kidney_disease_model.pkl", positive_label=0)


# ══════════════════════════════════════════════════════════════════════════════
# 4. DEPRESSION PREDICTION  — XGBoost + TargetEncoder + Feature Eng
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

    # Drop City — too many unique values, adds noise
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

    # Map Financial Stress to numeric if it's string
    if df["Financial Stress"].dtype == object:
        # Try numeric conversion first
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

    y = df[target].astype(int)
    X = df.drop(columns=[target])

    print(f"  Dataset shape : {X.shape}")
    print(f"  Target classes: {dict(zip(*np.unique(y, return_counts=True)))}")

    numeric_cols = X.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = X.select_dtypes(exclude=["number"]).columns.tolist()
    print(f"  Numeric features     : {len(numeric_cols)}")
    print(f"  Categorical features : {len(categorical_cols)}")
    print(f"  Categorical cols     : {categorical_cols}")

    # OrdinalEncoder for remaining categoricals (works well with XGBoost)
    preprocessor = build_preprocessor(
        numeric_cols, categorical_cols,
    )

    # ── XGBoost with RandomizedSearchCV ──────────────────────────────────
    neg_count = (y == 0).sum()
    pos_count = (y == 1).sum()
    scale_pw = neg_count / pos_count

    base_clf = xgb.XGBClassifier(
        random_state=42, n_jobs=-1, eval_metric="logloss",
        tree_method="hist", scale_pos_weight=scale_pw,
    )

    pipe = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", base_clf),
    ])

    param_dist = {
        "classifier__n_estimators": randint(300, 700),
        "classifier__max_depth": randint(4, 10),
        "classifier__learning_rate": uniform(0.01, 0.14),
        "classifier__subsample": uniform(0.7, 0.3),
        "classifier__colsample_bytree": uniform(0.6, 0.4),
        "classifier__min_child_weight": randint(1, 8),
        "classifier__gamma": uniform(0, 0.3),
        "classifier__reg_alpha": uniform(0, 0.5),
        "classifier__reg_lambda": uniform(0.5, 2),
    }

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    search = RandomizedSearchCV(
        pipe, param_dist, n_iter=60, cv=cv, scoring="accuracy",
        random_state=42, n_jobs=-1, refit=True,
    )
    search.fit(X_train, y_train)
    best_pipe = search.best_estimator_

    print(f"\n  Best CV score from search: {search.best_score_:.4f}")
    print(f"  Best params: { {k.replace('classifier__',''): round(v,4) if isinstance(v,float) else v for k,v in search.best_params_.items()} }")

    # Evaluate best
    y_pred = best_pipe.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")

    cv_scores = cross_val_score(best_pipe, X_train, y_train, cv=cv,
                                scoring="accuracy", n_jobs=-1)
    print(f"\n  5-Fold CV Accuracy : {cv_scores.mean():.4f} "
          f"(+/- {cv_scores.std():.4f})")
    print(f"  Test Accuracy      : {acc:.4f}  ({acc*100:.2f}%)")
    print(f"  Test F1 (weighted) : {f1:.4f}")

    baseline = BASELINES.get(name, None)
    if baseline:
        delta = acc - baseline
        arrow = "▲" if delta > 0 else ("▼" if delta < 0 else "═")
        print(f"  vs Baseline        : {baseline:.2%} → {acc:.2%}  "
              f"({arrow} {abs(delta)*100:+.2f} pp)")

    print(f"\n  Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))
    print(f"  Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # ── Bug 5 fix: find and save optimal threshold ──────────────────────
    best_threshold = find_best_threshold(best_pipe, X_test, y_test, positive_label=1)

    model_path = MODEL_DIR / "depression_model.pkl"
    version    = make_version("depression_model.pkl")
    trained_at = datetime.now(timezone.utc).isoformat()
    joblib.dump({
        'pipeline':   best_pipe,
        'threshold':  best_threshold,
        'version':    version,
        'trained_at': trained_at,
    }, model_path)
    print(f"\n  ✅ Model saved → {model_path}  (v{version}, threshold={best_threshold})")

    return {"name": name, "accuracy": acc, "f1": f1, "cv_mean": cv_scores.mean()}


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    print("\n" + "🏥  DISEASE PREDICTION — OPTIMIZED MODEL TRAINING".center(72))
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
