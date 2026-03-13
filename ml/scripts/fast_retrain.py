import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from datetime import datetime, timezone
import xgboost as xgb
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin

# Define project directories
SCRIPT_DIR = Path(__file__).resolve().parent
ML_DIR = SCRIPT_DIR.parent
DATA_DIR = ML_DIR / "data"
MODEL_DIR = ML_DIR / "models"

import sys
sys.path.insert(0, str(SCRIPT_DIR))
from utils import build_preprocessor, find_best_threshold, build_stacking_ensemble

# 1. DIABETES FAST RETRAIN
print("--- Retraining Diabetes Model (Fast) ---")
df = pd.read_csv(DATA_DIR / "diabetes_binary.csv")
y = df["Diabetes_binary"].astype(int)
X = df.drop(columns=["Diabetes_binary"])

# Basic feature eng
X["BMI_Age"] = X["BMI"] * X["Age"]
X["HighBP_HighChol"] = X["HighBP"] * X["HighChol"]
X["GenHlth_PhysHlth"] = X["GenHlth"] * X["PhysHlth"]
X["GenHlth_MentHlth"] = X["GenHlth"] * X["MentHlth"]
X["BMI_HighBP"] = X["BMI"] * X["HighBP"]

numeric_cols = X.columns.tolist()
categorical_cols = []
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

scale_pw = (y_train == 0).sum() / (y_train == 1).sum()

stacker = build_stacking_ensemble(
    xgb_params={"n_estimators": 50, "max_depth": 3, "learning_rate": 0.1, "scale_pos_weight": scale_pw},
    lgb_params={"n_estimators": 50, "max_depth": 3, "learning_rate": 0.1, "scale_pos_weight": scale_pw},
    cat_params={"iterations": 50, "depth": 3, "learning_rate": 0.1},
    use_calibration=False
)

pipe = Pipeline([
    ("preprocessor", build_preprocessor(numeric_cols, categorical_cols)),
    ("classifier", stacker),
])

pipe.fit(X_train, y_train)
best_threshold = find_best_threshold(pipe, X_test, y_test, positive_label=1)
model_path = MODEL_DIR / "diabetes_model.pkl"
version = f"diabetes_fast_{datetime.now().strftime('%Y%m%d_%H%M')}"
joblib.dump({"pipeline": pipe, "threshold": best_threshold, "version": version, "trained_at": datetime.now(timezone.utc).isoformat()}, model_path)
print(f"✅ Saved Diabetes Model to {model_path} (Threshold: {best_threshold})")

# 2. HEART FAST RETRAIN
print("\n--- Retraining Heart Disease Model (Fast) ---")
df = pd.read_csv(DATA_DIR / "heart_disease_uci.csv")
target = "num"
df[target] = (df[target] > 0).astype(int)
if "id" in df.columns: df.drop(columns=["id"], inplace=True)
y = df[target]
X = df.drop(columns=[target])
X["age_sq"] = X["age"] ** 2

numeric_cols = X.select_dtypes(include=["number"]).columns.tolist()
categorical_cols = X.select_dtypes(exclude=["number"]).columns.tolist()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)
scale_pw = (y_train == 0).sum() / max(1, (y_train == 1).sum())

stacker_heart = build_stacking_ensemble(
    xgb_params={"n_estimators": 50, "max_depth": 3, "scale_pos_weight": scale_pw},
    lgb_params={"n_estimators": 50, "max_depth": 3, "scale_pos_weight": scale_pw},
    cat_params={"iterations": 50, "depth": 3},
    use_calibration=False
)

pipe_heart = Pipeline([
    ("preprocessor", build_preprocessor(numeric_cols, categorical_cols, use_iterative=True, use_onehot=True)),
    ("classifier", stacker_heart),
])

pipe_heart.fit(X_train, y_train)
best_threshold = find_best_threshold(pipe_heart, X_test, y_test, positive_label=1)
model_path = MODEL_DIR / "heart_disease_model.pkl"
version = f"heart_fast_{datetime.now().strftime('%Y%m%d_%H%M')}"
joblib.dump({"pipeline": pipe_heart, "threshold": best_threshold, "version": version, "trained_at": datetime.now(timezone.utc).isoformat()}, model_path)
print(f"✅ Saved Heart Model to {model_path} (Threshold: {best_threshold})")

# 3. DEPRESSION FAST RETRAIN
print("\n--- Retraining Depression Model (Fast) ---")
df = pd.read_csv(DATA_DIR / "student_depression_dataset.csv")
target = "Depression"
if "id" in df.columns: df.drop(columns=["id"], inplace=True)
if "Sleep Duration" in df.columns:
    df["Sleep Duration"] = df["Sleep Duration"].str.strip("'\"")
    df["Sleep_Hours"] = df["Sleep Duration"].map({"Less than 5 hours": 4, "5-6 hours": 5.5, "7-8 hours": 7.5, "More than 8 hours": 9, "Others": 6.5}).fillna(6.5)
    df.drop(columns=["Sleep Duration"], inplace=True)
if "City" in df.columns: df.drop(columns=["City"], inplace=True)
for col in ["Have you ever had suicidal thoughts ?", "Family History of Mental Illness"]:
    if col in df.columns: df[col] = df[col].map({"Yes": 1, "No": 0}).fillna(0).astype(int)
if "Gender" in df.columns: df["Gender"] = df["Gender"].map({"Male": 1, "Female": 0}).fillna(0).astype(int)
if "Dietary Habits" in df.columns:
    df["Dietary_Ordinal"] = df["Dietary Habits"].map({"Unhealthy": 0, "Moderate": 1, "Healthy": 2, "Others": 1}).fillna(1)
    df.drop(columns=["Dietary Habits"], inplace=True)
if "Financial Stress" in df.columns and df["Financial Stress"].dtype == object:
    df["Financial Stress"] = pd.to_numeric(df["Financial Stress"], errors="coerce").fillna(3)

y = df[target].astype(int)
X = df.drop(columns=[target])

numeric_cols = X.select_dtypes(include=["number"]).columns.tolist()
categorical_cols = X.select_dtypes(exclude=["number"]).columns.tolist()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)
scale_pw = (y_train == 0).sum() / max(1, (y_train == 1).sum())

stacker_dep = build_stacking_ensemble(
    xgb_params={"n_estimators": 50, "max_depth": 3, "scale_pos_weight": scale_pw},
    lgb_params={"n_estimators": 50, "max_depth": 3, "scale_pos_weight": scale_pw},
    cat_params={"iterations": 50, "depth": 3},
    use_calibration=False
)

pipe_dep = Pipeline([
    ("preprocessor", build_preprocessor(numeric_cols, categorical_cols)),
    ("classifier", stacker_dep),
])

pipe_dep.fit(X_train, y_train)
best_threshold = find_best_threshold(pipe_dep, X_test, y_test, positive_label=1)
model_path = MODEL_DIR / "depression_model.pkl"
version = f"depression_fast_{datetime.now().strftime('%Y%m%d_%H%M')}"
joblib.dump({"pipeline": pipe_dep, "threshold": best_threshold, "version": version, "trained_at": datetime.now(timezone.utc).isoformat()}, model_path)
print(f"✅ Saved Depression Model to {model_path} (Threshold: {best_threshold})")
print("\n✅ All OUTDATED models fast-retrained with current sklearn version!")
