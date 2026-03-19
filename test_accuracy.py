import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import lightgbm as lgb
from pathlib import Path
import numpy as np

DATA_DIR = Path("/home/udaylinux/Desktop/Disease-outbreak-prediction_ai/ml/data")

def test_diabetes():
    df = pd.read_csv(DATA_DIR / "diabetes_binary.csv")
    y = df["Diabetes_binary"].astype(int)
    X = df.drop(columns=["Diabetes_binary"])
    # A few basic features
    X["BMI_Age"] = X["BMI"] * X["Age"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)
    
    # Try LightGBM for accuracy
    clf = lgb.LGBMClassifier(random_state=42, n_estimators=200, learning_rate=0.05, class_weight=None)
    clf.fit(X_train, y_train)
    preds = clf.predict(X_test)
    print(f"Diabetes LGBM Default Threshold Accuracy: {accuracy_score(y_test, preds):.4f}")

def test_heart():
    df = pd.read_csv(DATA_DIR / "heart_disease_uci.csv")
    df["num"] = (df["num"] > 0).astype(int)
    if "id" in df.columns: df.drop(columns=["id"], inplace=True)
    df.fillna(df.median(numeric_only=True), inplace=True)
    for col in df.select_dtypes(include='object').columns:
        df[col] = pd.factorize(df[col])[0]
    
    y = df["num"]
    X = df.drop(columns=["num"])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)
    
    clf = RandomForestClassifier(random_state=42, n_estimators=100, max_depth=5)
    clf.fit(X_train, y_train)
    preds = clf.predict(X_test)
    print(f"Heart RF Accuracy: {accuracy_score(y_test, preds):.4f}")

def test_depression():
    df = pd.read_csv(DATA_DIR / "student_depression_dataset.csv")
    if "id" in df.columns: df.drop(columns=["id"], inplace=True)
    df.fillna(df.median(numeric_only=True), inplace=True)
    for col in df.select_dtypes(include='object').columns:
        df[col] = pd.factorize(df[col])[0]
        
    y = df["Depression"].astype(int)
    X = df.drop(columns=["Depression"])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)
    
    clf = lgb.LGBMClassifier(random_state=42, n_estimators=200, learning_rate=0.05)
    clf.fit(X_train, y_train)
    preds = clf.predict(X_test)
    print(f"Depression LGBM Accuracy: {accuracy_score(y_test, preds):.4f}")

if __name__ == "__main__":
    test_diabetes()
    test_heart()
    test_depression()
