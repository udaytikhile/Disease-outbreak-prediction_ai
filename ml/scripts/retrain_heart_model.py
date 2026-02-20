#!/usr/bin/env python3
"""
Retrain Heart Disease Model
This script retrains the heart disease prediction model and scaler
to match the current dataset (13 features).
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_PATH = BASE_DIR / "data" / "heart.csv"
MODEL_DIR = BASE_DIR / "models"

print("=" * 60)
print("RETRAINING HEART DISEASE MODEL")
print("=" * 60)

# Load data
print("\n📂 Loading data...")
df = pd.read_csv(DATA_PATH)
print(f"✅ Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
print(f"Features: {list(df.columns[:-1])}")
print(f"Number of features: {len(df.columns) - 1}")

# Separate features and target
X = df.drop('target', axis=1)
y = df['target']

print(f"\n📊 Class distribution:")
print(y.value_counts())

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"\n✂️ Data split:")
print(f"   Training set: {X_train.shape[0]} samples")
print(f"   Test set: {X_test.shape[0]} samples")

# Scale features
print("\n🔄 Scaling features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
print(f"✅ Scaler fitted with {scaler.n_features_in_} features")

# Train ensemble model
print("\n🤖 Training ensemble model...")

# Individual models
rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

gb = GradientBoostingClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    random_state=42
)

svc = SVC(
    kernel='rbf',
    C=1.0,
    gamma='scale',
    probability=True,
    random_state=42
)

# Voting ensemble
model = VotingClassifier(
    estimators=[
        ('rf', rf),
        ('gb', gb),
        ('svc', svc)
    ],
    voting='soft',
    n_jobs=-1
)

# Train model
model.fit(X_train_scaled, y_train)
print("✅ Model trained successfully!")

# Evaluate
print("\n📈 Evaluating model...")
y_pred = model.predict(X_test_scaled)
accuracy = accuracy_score(y_test, y_pred)
print(f"   Test Accuracy: {accuracy * 100:.2f}%")

# Cross-validation
print("\n🔍 Cross-validation scores (5-fold):")
cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
print(f"   CV Scores: {[f'{score:.4f}' for score in cv_scores]}")
print(f"   Mean CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")

# Classification report
print("\n📊 Classification Report:")
print(classification_report(y_test, y_pred, target_names=['No Disease', 'Disease']))

# Confusion matrix
print("🔢 Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Save model and scaler
print("\n💾 Saving model and scaler...")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

with open(MODEL_DIR / "heart_disease_model.sav", 'wb') as f:
    pickle.dump(model, f)
with open(MODEL_DIR / "scaler_heart_disease.sav", 'wb') as f:
    pickle.dump(scaler, f)

print(f"✅ Model saved to: {MODEL_DIR / 'heart_disease_model.sav'}")
print(f"✅ Scaler saved to: {MODEL_DIR / 'scaler_heart_disease.sav'}")

print("\n" + "=" * 60)
print("✨ RETRAINING COMPLETE!")
print("=" * 60)
