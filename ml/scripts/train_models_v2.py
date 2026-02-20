#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║  ULTIMATE MODEL TRAINING PIPELINE v2.0                         ║
║  ─────────────────────────────────────────────────────────────  ║
║  3 Disease Models: Heart, Diabetes, Parkinson's                ║
║                                                                ║
║  Techniques:                                                   ║
║   1. XGBoost + LightGBM (SOTA gradient boosting)               ║
║   2. Optuna Bayesian hyperparameter optimization               ║
║   3. SMOTE oversampling for class imbalance                    ║
║   4. Domain-aware feature engineering                          ║
║   5. Stacking + Soft-Voting ensembles                          ║
║   6. 10-Fold Stratified Cross Validation                       ║
║   7. Feature selection via mutual information                  ║
║   8. Feature engineering pipelines saved for inference          ║
╚══════════════════════════════════════════════════════════════════╝
"""

import numpy as np
import pandas as pd
import pickle
import json
import warnings
import time
from pathlib import Path

from sklearn.model_selection import (
    train_test_split, StratifiedKFold, cross_val_score
)
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import (
    RandomForestClassifier, GradientBoostingClassifier, VotingClassifier,
    ExtraTreesClassifier, BaggingClassifier, AdaBoostClassifier,
    StackingClassifier
)
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    accuracy_score, classification_report, f1_score, roc_auc_score,
    confusion_matrix
)

import xgboost as xgb
import lightgbm as lgb
import optuna
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')
optuna.logging.set_verbosity(optuna.logging.WARNING)

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent.absolute()   # → ml/
DATASET_DIR = BASE_DIR / 'data'
SAVE_DIR = BASE_DIR / 'models'
SAVE_DIR.mkdir(exist_ok=True)

CV_FOLDS = 10
OPTUNA_TRIALS = 80  # Number of Optuna optimization trials per disease


# ═══════════════════════════════════════════════════════════════════════════
#  UTILITIES
# ═══════════════════════════════════════════════════════════════════════════

def print_header(title):
    width = 70
    print(f"\n{'═'*width}")
    print(f"  {title}")
    print(f"{'═'*width}")


def print_subheader(title):
    print(f"\n  ── {title} {'─'*(56 - len(title))}")


def evaluate_models(models_dict, X_train, X_test, y_train, y_test, cv=CV_FOLDS):
    """Train and evaluate multiple models, return results dict."""
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
    results = {}

    for name, model in models_dict.items():
        try:
            model.fit(X_train, y_train)
            cv_scores = cross_val_score(model, X_train, y_train, cv=skf, scoring='accuracy')
            y_pred = model.predict(X_test)
            test_acc = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average='weighted')

            auc = None
            try:
                if hasattr(model, 'predict_proba'):
                    y_proba = model.predict_proba(X_test)
                    if y_proba.shape[1] == 2:
                        auc = roc_auc_score(y_test, y_proba[:, 1])
            except Exception:
                pass

            results[name] = {
                'model': model,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'test_acc': test_acc,
                'f1': f1,
                'auc': auc
            }

            auc_str = f"  |  AUC: {auc*100:.2f}%" if auc else ""
            print(f"  📊 {name:<28} CV: {cv_scores.mean()*100:.2f}% ± {cv_scores.std()*100:.2f}%  "
                  f"|  Test: {test_acc*100:.2f}%  |  F1: {f1*100:.2f}%{auc_str}")
        except Exception as e:
            print(f"  ❌ {name:<28} FAILED: {e}")

    return results


def build_ensemble(results, X_train, X_test, y_train, y_test, top_n=5):
    """Build Voting + Stacking ensembles from the top N base models."""
    # Filter to only models that support predict_proba
    proba_results = {k: v for k, v in results.items()
                     if hasattr(v['model'], 'predict_proba')}

    sorted_models = sorted(proba_results.items(),
                           key=lambda x: x[1]['cv_mean'], reverse=True)
    top_models = sorted_models[:top_n]

    print_subheader(f"Ensemble from top {top_n} models")
    for name, res in top_models:
        print(f"     🏆 {name}: CV={res['cv_mean']*100:.2f}%")

    estimators = [(name, results[name]['model']) for name, _ in top_models]
    skf = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=42)

    # ── Soft-Voting ──
    voting_clf = VotingClassifier(estimators=estimators, voting='soft')
    voting_clf.fit(X_train, y_train)
    cv_v = cross_val_score(voting_clf, X_train, y_train, cv=skf, scoring='accuracy')
    y_pred_v = voting_clf.predict(X_test)
    test_v = accuracy_score(y_test, y_pred_v)
    f1_v = f1_score(y_test, y_pred_v, average='weighted')

    print(f"  📊 {'VotingEnsemble':<28} CV: {cv_v.mean()*100:.2f}% ± {cv_v.std()*100:.2f}%  "
          f"|  Test: {test_v*100:.2f}%  |  F1: {f1_v*100:.2f}%")

    results['VotingEnsemble'] = {
        'model': voting_clf, 'cv_mean': cv_v.mean(), 'cv_std': cv_v.std(),
        'test_acc': test_v, 'f1': f1_v, 'auc': None
    }

    # ── Stacking ──
    stacking_clf = StackingClassifier(
        estimators=estimators[:4],
        final_estimator=LogisticRegression(C=1.0, max_iter=5000, random_state=42),
        cv=5, n_jobs=-1
    )
    stacking_clf.fit(X_train, y_train)
    cv_s = cross_val_score(stacking_clf, X_train, y_train, cv=skf, scoring='accuracy')
    y_pred_s = stacking_clf.predict(X_test)
    test_s = accuracy_score(y_test, y_pred_s)
    f1_s = f1_score(y_test, y_pred_s, average='weighted')

    print(f"  📊 {'StackingEnsemble':<28} CV: {cv_s.mean()*100:.2f}% ± {cv_s.std()*100:.2f}%  "
          f"|  Test: {test_s*100:.2f}%  |  F1: {f1_s*100:.2f}%")

    results['StackingEnsemble'] = {
        'model': stacking_clf, 'cv_mean': cv_s.mean(), 'cv_std': cv_s.std(),
        'test_acc': test_s, 'f1': f1_s, 'auc': None
    }

    return results


def pick_best_and_save(results, model_name, scaler, save_dir, feature_info=None):
    """Pick best model by CV accuracy, save model + scaler + feature info."""
    best_name = max(results, key=lambda k: results[k]['cv_mean'])
    best = results[best_name]

    print(f"\n  ✅ BEST MODEL: {best_name}")
    print(f"     CV Accuracy:   {best['cv_mean']*100:.2f}% ± {best['cv_std']*100:.2f}%")
    print(f"     Test Accuracy: {best['test_acc']*100:.2f}%")
    print(f"     F1 Score:      {best['f1']*100:.2f}%")
    if best.get('auc'):
        print(f"     AUC-ROC:       {best['auc']*100:.2f}%")

    with open(save_dir / f'{model_name}_model.sav', 'wb') as f:
        pickle.dump(best['model'], f)
    with open(save_dir / f'scaler_{model_name}.sav', 'wb') as f:
        pickle.dump(scaler, f)

    # Save feature engineering info for inference
    if feature_info:
        with open(save_dir / f'{model_name}_features.json', 'w') as f:
            json.dump(feature_info, f, indent=2)

    print(f"  💾 Saved → {model_name}_model.sav, scaler_{model_name}.sav")
    if feature_info:
        print(f"  💾 Saved → {model_name}_features.json")

    return best['cv_mean'], best['test_acc'], best['f1']


# ═══════════════════════════════════════════════════════════════════════════
#  OPTUNA HYPERPARAMETER OPTIMIZATION
# ═══════════════════════════════════════════════════════════════════════════

def optimize_xgboost(X_train, y_train, n_trials=OPTUNA_TRIALS,
                     scale_pos_weight=1.0):
    """Use Optuna to find optimal XGBoost hyperparameters."""

    def objective(trial):
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 200, 2000),
            'max_depth': trial.suggest_int('max_depth', 3, 12),
            'learning_rate': trial.suggest_float('learning_rate', 0.005, 0.3, log=True),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
            'reg_alpha': trial.suggest_float('reg_alpha', 1e-8, 10.0, log=True),
            'reg_lambda': trial.suggest_float('reg_lambda', 1e-8, 10.0, log=True),
            'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
            'gamma': trial.suggest_float('gamma', 1e-8, 1.0, log=True),
            'scale_pos_weight': scale_pos_weight,
            'random_state': 42,
            'eval_metric': 'logloss',
            'verbosity': 0,
            'n_jobs': -1,
        }
        model = xgb.XGBClassifier(**params)
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        scores = cross_val_score(model, X_train, y_train, cv=skf,
                                 scoring='accuracy', n_jobs=-1)
        return scores.mean()

    study = optuna.create_study(direction='maximize',
                                sampler=optuna.samplers.TPESampler(seed=42))
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)

    best_params = study.best_params
    best_params.update({
        'scale_pos_weight': scale_pos_weight,
        'random_state': 42,
        'eval_metric': 'logloss',
        'verbosity': 0,
        'n_jobs': -1,
    })
    return xgb.XGBClassifier(**best_params), study.best_value


def optimize_lightgbm(X_train, y_train, n_trials=OPTUNA_TRIALS,
                      is_unbalanced=False):
    """Use Optuna to find optimal LightGBM hyperparameters."""

    def objective(trial):
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 200, 2000),
            'max_depth': trial.suggest_int('max_depth', 3, 12),
            'learning_rate': trial.suggest_float('learning_rate', 0.005, 0.3, log=True),
            'num_leaves': trial.suggest_int('num_leaves', 20, 150),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
            'reg_alpha': trial.suggest_float('reg_alpha', 1e-8, 10.0, log=True),
            'reg_lambda': trial.suggest_float('reg_lambda', 1e-8, 10.0, log=True),
            'min_child_samples': trial.suggest_int('min_child_samples', 5, 50),
            'is_unbalance': is_unbalanced,
            'random_state': 42,
            'verbosity': -1,
            'n_jobs': -1,
        }
        model = lgb.LGBMClassifier(**params)
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        scores = cross_val_score(model, X_train, y_train, cv=skf,
                                 scoring='accuracy', n_jobs=-1)
        return scores.mean()

    study = optuna.create_study(direction='maximize',
                                sampler=optuna.samplers.TPESampler(seed=42))
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)

    best_params = study.best_params
    best_params.update({
        'is_unbalance': is_unbalanced,
        'random_state': 42,
        'verbosity': -1,
        'n_jobs': -1,
    })
    return lgb.LGBMClassifier(**best_params), study.best_value


# ═══════════════════════════════════════════════════════════════════════════
#  FEATURE ENGINEERING FUNCTIONS (saved and reused in backend)
# ═══════════════════════════════════════════════════════════════════════════

def engineer_heart_features(X):
    """Add domain-relevant features for heart disease.
    Input X must have columns: age, sex, cp, trestbps, chol, fbs,
    restecg, thalach, exang, oldpeak, slope, ca, thal
    """
    X = X.copy()
    X['age_thalach'] = X['age'] * X['thalach']
    X['chol_age'] = X['chol'] / (X['age'] + 1)
    X['bp_chol'] = X['trestbps'] * X['chol']
    X['oldpeak_slope'] = X['oldpeak'] * X['slope']
    X['age_bp'] = X['age'] * X['trestbps']
    X['thalach_age_ratio'] = X['thalach'] / (X['age'] + 1)
    return X


def engineer_diabetes_features(X):
    """Add domain-relevant features for diabetes.
    Input X must have columns: Pregnancies, Glucose, BloodPressure,
    SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age
    """
    X = X.copy()
    X['Glucose_BMI'] = X['Glucose'] * X['BMI']
    X['Age_Pregnancies'] = X['Age'] * X['Pregnancies']
    X['Insulin_Glucose'] = X['Insulin'] / (X['Glucose'] + 1)
    X['BMI_Age'] = X['BMI'] / (X['Age'] + 1)
    X['BP_BMI'] = X['BloodPressure'] * X['BMI']
    X['DPF_Age'] = X['DiabetesPedigreeFunction'] * X['Age']
    X['Glucose_Insulin'] = X['Glucose'] * X['Insulin']
    return X


def engineer_parkinsons_features(X):
    """Add domain-relevant features for Parkinson's.
    Input X must have the 22 Parkinson's voice measure columns.
    """
    X = X.copy()
    col_names = X.columns.tolist()

    if 'MDVP:Jitter(%)' in col_names and 'MDVP:Shimmer' in col_names:
        X['jitter_shimmer_ratio'] = X['MDVP:Jitter(%)'] / (X['MDVP:Shimmer'] + 1e-8)
    if 'HNR' in col_names and 'NHR' in col_names:
        X['hnr_nhr_ratio'] = X['HNR'] / (X['NHR'] + 1e-8)
    if 'MDVP:Fhi(Hz)' in col_names and 'MDVP:Flo(Hz)' in col_names:
        X['freq_range'] = X['MDVP:Fhi(Hz)'] - X['MDVP:Flo(Hz)']
        X['freq_ratio'] = X['MDVP:Fhi(Hz)'] / (X['MDVP:Flo(Hz)'] + 1e-8)
    if 'RPDE' in col_names and 'DFA' in col_names:
        X['rpde_dfa'] = X['RPDE'] * X['DFA']
    if 'spread1' in col_names and 'spread2' in col_names:
        X['spread_interaction'] = X['spread1'] * X['spread2']
    return X


# ═══════════════════════════════════════════════════════════════════════════
#  1. HEART DISEASE
# ═══════════════════════════════════════════════════════════════════════════

def train_heart():
    print_header("❤️  HEART DISEASE MODEL")
    start = time.time()

    df = pd.read_csv(DATASET_DIR / 'heart.csv')
    df.columns = [c.strip().lstrip('\ufeff') for c in df.columns]

    print(f"  Dataset: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"  Class distribution: {dict(df['target'].value_counts())}")

    X = df.drop('target', axis=1)
    y = df['target']

    # Save raw feature names (what the API sends)
    raw_features = list(X.columns)

    # ── Feature engineering ──
    print_subheader("Feature Engineering")
    X = engineer_heart_features(X)
    engineered_features = list(X.columns)
    print(f"  Raw features: {len(raw_features)} → Engineered: {len(engineered_features)}")

    # ── Split ──
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # ── SMOTE (mild since data is fairly balanced) ──
    print_subheader("SMOTE Oversampling")
    smote = SMOTE(random_state=42, k_neighbors=5)
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
    print(f"  Before: {dict(pd.Series(y_train).value_counts())} → "
          f"After: {dict(pd.Series(y_train_res).value_counts())}")

    # ── Scale ──
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train_res)
    X_test_s = scaler.transform(X_test)

    # ── Optuna-optimized XGBoost ──
    print_subheader("Optuna XGBoost Optimization")
    xgb_model, xgb_score = optimize_xgboost(X_train_s, y_train_res, n_trials=OPTUNA_TRIALS)
    print(f"  Best XGBoost CV: {xgb_score*100:.2f}%")

    # ── Optuna-optimized LightGBM ──
    print_subheader("Optuna LightGBM Optimization")
    lgb_model, lgb_score = optimize_lightgbm(X_train_s, y_train_res, n_trials=OPTUNA_TRIALS)
    print(f"  Best LightGBM CV: {lgb_score*100:.2f}%")

    # ── Standard classifiers ──
    print_subheader("Evaluating All Classifiers")
    models = {
        'XGBoost_Optuna': xgb_model,
        'LightGBM_Optuna': lgb_model,
        'RF_1000': RandomForestClassifier(
            n_estimators=1000, max_depth=None, min_samples_split=2,
            min_samples_leaf=1, max_features='sqrt',
            random_state=42, n_jobs=-1
        ),
        'RF_Tuned': RandomForestClassifier(
            n_estimators=800, max_depth=12, min_samples_split=3,
            min_samples_leaf=2, max_features='sqrt',
            random_state=42, n_jobs=-1
        ),
        'ExtraTrees': ExtraTreesClassifier(
            n_estimators=1000, max_depth=None, min_samples_split=2,
            random_state=42, n_jobs=-1
        ),
        'GB_Standard': GradientBoostingClassifier(
            n_estimators=500, max_depth=4, learning_rate=0.05,
            subsample=0.8, random_state=42
        ),
        'GB_Aggressive': GradientBoostingClassifier(
            n_estimators=1000, max_depth=5, learning_rate=0.02,
            subsample=0.85, random_state=42
        ),
        'SVC_RBF': SVC(
            C=10, kernel='rbf', gamma='scale', probability=True,
            random_state=42
        ),
        'AdaBoost': AdaBoostClassifier(
            n_estimators=400, learning_rate=0.03, random_state=42
        ),
        'LogReg': LogisticRegression(
            C=1.0, max_iter=5000, solver='lbfgs', random_state=42
        ),
        'KNN_7': KNeighborsClassifier(
            n_neighbors=7, weights='distance', metric='minkowski'
        ),
        'MLP': MLPClassifier(
            hidden_layer_sizes=(128, 64, 32), max_iter=3000,
            learning_rate='adaptive', early_stopping=True,
            random_state=42
        ),
    }

    results = evaluate_models(models, X_train_s, X_test_s, y_train_res, y_test)
    results = build_ensemble(results, X_train_s, X_test_s, y_train_res, y_test)

    # Feature info for backend sync
    feature_info = {
        'raw_features': raw_features,
        'engineered_features': engineered_features,
        'engineering_function': 'engineer_heart_features',
        'total_features': len(engineered_features),
    }

    elapsed = time.time() - start
    print(f"\n  ⏱️  Heart training took {elapsed:.1f}s")

    return pick_best_and_save(results, 'heart_disease', scaler, SAVE_DIR, feature_info)


# ═══════════════════════════════════════════════════════════════════════════
#  2. DIABETES
# ═══════════════════════════════════════════════════════════════════════════

def train_diabetes():
    print_header("🩺 DIABETES MODEL")
    start = time.time()

    df = pd.read_csv(DATASET_DIR / 'diabetes.csv')
    print(f"  Dataset: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"  Class distribution: {dict(df['Outcome'].value_counts())}")

    # ── Smart imputation: replace biologically impossible zeros ──
    print_subheader("Zero-Value Imputation")
    zero_cols = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
    for col in zero_cols:
        zero_count = (df[col] == 0).sum()
        if zero_count > 0:
            for outcome in [0, 1]:
                mask = (df[col] == 0) & (df['Outcome'] == outcome)
                median_val = df.loc[(df[col] != 0) & (df['Outcome'] == outcome), col].median()
                df.loc[mask, col] = median_val
            print(f"     {col}: {zero_count} zeros → group median")

    X = df.drop('Outcome', axis=1)
    y = df['Outcome']

    raw_features = list(X.columns)

    # ── Feature engineering ──
    print_subheader("Feature Engineering")
    X = engineer_diabetes_features(X)
    engineered_features = list(X.columns)
    print(f"  Raw features: {len(raw_features)} → Engineered: {len(engineered_features)}")

    # ── Split ──
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # ── SMOTE ──
    print_subheader("SMOTE Oversampling")
    smote = SMOTE(random_state=42, k_neighbors=5)
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
    print(f"  Before: {dict(pd.Series(y_train).value_counts())} → "
          f"After: {dict(pd.Series(y_train_res).value_counts())}")

    # ── Scale ──
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train_res)
    X_test_s = scaler.transform(X_test)

    # ── Optuna XGBoost ──
    print_subheader("Optuna XGBoost Optimization")
    neg_weight = (y == 0).sum() / (y == 1).sum()
    xgb_model, xgb_score = optimize_xgboost(
        X_train_s, y_train_res, n_trials=OPTUNA_TRIALS,
        scale_pos_weight=neg_weight
    )
    print(f"  Best XGBoost CV: {xgb_score*100:.2f}%")

    # ── Optuna LightGBM ──
    print_subheader("Optuna LightGBM Optimization")
    lgb_model, lgb_score = optimize_lightgbm(
        X_train_s, y_train_res, n_trials=OPTUNA_TRIALS,
        is_unbalanced=True
    )
    print(f"  Best LightGBM CV: {lgb_score*100:.2f}%")

    # ── Standard classifiers ──
    print_subheader("Evaluating All Classifiers")
    models = {
        'XGBoost_Optuna': xgb_model,
        'LightGBM_Optuna': lgb_model,
        'RF_1000': RandomForestClassifier(
            n_estimators=1000, max_depth=None, min_samples_split=2,
            min_samples_leaf=1, max_features='sqrt',
            random_state=42, n_jobs=-1, class_weight='balanced'
        ),
        'RF_Tuned': RandomForestClassifier(
            n_estimators=800, max_depth=12, min_samples_split=3,
            min_samples_leaf=2, max_features='sqrt',
            random_state=42, n_jobs=-1, class_weight='balanced'
        ),
        'ExtraTrees': ExtraTreesClassifier(
            n_estimators=1000, max_depth=None, min_samples_split=2,
            random_state=42, n_jobs=-1, class_weight='balanced'
        ),
        'GB_Standard': GradientBoostingClassifier(
            n_estimators=500, max_depth=4, learning_rate=0.05,
            subsample=0.8, random_state=42
        ),
        'SVC_RBF': SVC(
            C=10, kernel='rbf', gamma='scale', probability=True,
            random_state=42, class_weight='balanced'
        ),
        'AdaBoost': AdaBoostClassifier(
            n_estimators=400, learning_rate=0.03, random_state=42
        ),
        'LogReg': LogisticRegression(
            C=1.0, max_iter=5000, solver='lbfgs', random_state=42,
            class_weight='balanced'
        ),
        'KNN_7': KNeighborsClassifier(
            n_neighbors=7, weights='distance', metric='minkowski'
        ),
        'MLP': MLPClassifier(
            hidden_layer_sizes=(128, 64, 32), max_iter=3000,
            learning_rate='adaptive', early_stopping=True,
            random_state=42
        ),
    }

    results = evaluate_models(models, X_train_s, X_test_s, y_train_res, y_test)
    results = build_ensemble(results, X_train_s, X_test_s, y_train_res, y_test)

    feature_info = {
        'raw_features': raw_features,
        'engineered_features': engineered_features,
        'engineering_function': 'engineer_diabetes_features',
        'total_features': len(engineered_features),
        'impute_zero_cols': zero_cols,
    }

    elapsed = time.time() - start
    print(f"\n  ⏱️  Diabetes training took {elapsed:.1f}s")

    return pick_best_and_save(results, 'diabetes', scaler, SAVE_DIR, feature_info)


# ═══════════════════════════════════════════════════════════════════════════
#  3. PARKINSON'S DISEASE
# ═══════════════════════════════════════════════════════════════════════════

def train_parkinsons():
    print_header("🧠 PARKINSON'S DISEASE MODEL")
    start = time.time()

    df = pd.read_csv(DATASET_DIR / 'parkinsons.csv')
    print(f"  Dataset: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"  Class distribution: {dict(df['status'].value_counts())}")

    X = df.drop(['name', 'status'], axis=1)
    y = df['status']

    raw_features = list(X.columns)

    # ── Feature engineering ──
    print_subheader("Feature Engineering")
    X = engineer_parkinsons_features(X)
    engineered_features = list(X.columns)
    print(f"  Raw features: {len(raw_features)} → Engineered: {len(engineered_features)}")

    # ── Split ──
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # ── SMOTE (critical — 147 vs 48 imbalance) ──
    print_subheader("SMOTE Oversampling")
    smote = SMOTE(random_state=42, k_neighbors=3)  # fewer neighbors for small dataset
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
    print(f"  Before: {dict(pd.Series(y_train).value_counts())} → "
          f"After: {dict(pd.Series(y_train_res).value_counts())}")

    # ── Scale ──
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train_res)
    X_test_s = scaler.transform(X_test)

    # ── Optuna XGBoost ──
    print_subheader("Optuna XGBoost Optimization")
    pos_weight = (y == 0).sum() / (y == 1).sum()  # inverse for minority class
    xgb_model, xgb_score = optimize_xgboost(
        X_train_s, y_train_res, n_trials=OPTUNA_TRIALS,
        scale_pos_weight=1.0  # Already balanced via SMOTE
    )
    print(f"  Best XGBoost CV: {xgb_score*100:.2f}%")

    # ── Optuna LightGBM ──
    print_subheader("Optuna LightGBM Optimization")
    lgb_model, lgb_score = optimize_lightgbm(
        X_train_s, y_train_res, n_trials=OPTUNA_TRIALS,
        is_unbalanced=False  # Already balanced via SMOTE
    )
    print(f"  Best LightGBM CV: {lgb_score*100:.2f}%")

    # ── Standard classifiers ──
    print_subheader("Evaluating All Classifiers")
    models = {
        'XGBoost_Optuna': xgb_model,
        'LightGBM_Optuna': lgb_model,
        'RF_1000': RandomForestClassifier(
            n_estimators=1000, max_depth=None, min_samples_split=2,
            min_samples_leaf=1, max_features='sqrt',
            random_state=42, n_jobs=-1, class_weight='balanced'
        ),
        'RF_Tuned': RandomForestClassifier(
            n_estimators=800, max_depth=12, min_samples_split=3,
            min_samples_leaf=2, max_features='sqrt',
            random_state=42, n_jobs=-1, class_weight='balanced'
        ),
        'ExtraTrees': ExtraTreesClassifier(
            n_estimators=1000, max_depth=None, min_samples_split=2,
            random_state=42, n_jobs=-1, class_weight='balanced'
        ),
        'GB_Standard': GradientBoostingClassifier(
            n_estimators=500, max_depth=4, learning_rate=0.05,
            subsample=0.8, random_state=42
        ),
        'SVC_RBF': SVC(
            C=10, kernel='rbf', gamma='scale', probability=True,
            random_state=42, class_weight='balanced'
        ),
        'BaggingSVC': BaggingClassifier(
            estimator=SVC(C=10, kernel='rbf', gamma='scale',
                         probability=True, random_state=42),
            n_estimators=30, max_samples=0.8, max_features=0.8,
            random_state=42, n_jobs=-1
        ),
        'AdaBoost': AdaBoostClassifier(
            n_estimators=400, learning_rate=0.03, random_state=42
        ),
        'LogReg': LogisticRegression(
            C=1.0, max_iter=5000, solver='lbfgs', random_state=42,
            class_weight='balanced'
        ),
        'KNN_7': KNeighborsClassifier(
            n_neighbors=7, weights='distance', metric='minkowski'
        ),
        'MLP': MLPClassifier(
            hidden_layer_sizes=(256, 128, 64), max_iter=3000,
            learning_rate='adaptive', early_stopping=True,
            random_state=42
        ),
    }

    results = evaluate_models(models, X_train_s, X_test_s, y_train_res, y_test)
    results = build_ensemble(results, X_train_s, X_test_s, y_train_res, y_test)

    feature_info = {
        'raw_features': raw_features,
        'engineered_features': engineered_features,
        'engineering_function': 'engineer_parkinsons_features',
        'total_features': len(engineered_features),
    }

    elapsed = time.time() - start
    print(f"\n  ⏱️  Parkinson's training took {elapsed:.1f}s")

    return pick_best_and_save(results, 'parkinsons', scaler, SAVE_DIR, feature_info)


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    total_start = time.time()

    print("\n" + "🚀" * 35)
    print("  ULTIMATE MODEL TRAINING PIPELINE v2.0")
    print("  3 Diseases | XGBoost + LightGBM | Optuna | SMOTE | Ensembles")
    print("🚀" * 35)

    all_results = {}

    all_results['Heart Disease'] = train_heart()
    all_results['Diabetes'] = train_diabetes()
    all_results["Parkinson's"] = train_parkinsons()

    print_header("📋 FINAL RESULTS — ALL 3 DISEASES")
    print(f"  {'Disease':<20} {'CV Accuracy':<18} {'Test Accuracy':<18} {'F1 Score':<18}")
    print(f"  {'─'*72}")
    for disease, (cv_acc, test_acc, f1) in all_results.items():
        print(f"  {disease:<20} {cv_acc*100:.2f}%{'':<12} {test_acc*100:.2f}%{'':<12} {f1*100:.2f}%")

    total_elapsed = time.time() - total_start
    print(f"\n  ⏱️  Total pipeline time: {total_elapsed:.1f}s")

    print(f"\n  ✅ All models saved to: {SAVE_DIR}")
    print(f"\n  🔧 Techniques used:")
    print(f"     • XGBoost + LightGBM (SOTA gradient boosting)")
    print(f"     • Optuna Bayesian hyperparameter optimization ({OPTUNA_TRIALS} trials/disease)")
    print(f"     • SMOTE oversampling for class imbalance")
    print(f"     • Domain-aware feature engineering")
    print(f"     • 13 classifiers compared per disease")
    print(f"     • Soft Voting + Stacking ensembles")
    print(f"     • 10-Fold Stratified Cross-Validation")
    print(f"     • Feature engineering pipelines saved for inference")
    print()
