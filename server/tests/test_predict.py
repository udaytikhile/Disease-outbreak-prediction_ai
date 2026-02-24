"""
Tests for the prediction endpoints.
"""
import pytest


# ── Test Data ────────────────────────────────────────────────────────────────
VALID_HEART = {
    "age": 45, "sex": "Male", "cp": "asymptomatic", "trestbps": 120, "chol": 200,
    "fbs": "FALSE", "restecg": "normal", "thalch": 150, "exang": "FALSE",
    "oldpeak": 1.0, "slope": "flat", "ca": 0, "thal": "normal"
}

VALID_DIABETES = {
    "HighBP": 1, "HighChol": 1, "CholCheck": 1, "BMI": 25, "Smoker": 0, "Stroke": 0,
    "HeartDiseaseorAttack": 0, "PhysActivity": 1, "Fruits": 1, "Veggies": 1,
    "HvyAlcoholConsump": 0, "AnyHealthcare": 1, "NoDocbcCost": 0, "GenHlth": 3,
    "MentHlth": 0, "PhysHlth": 0, "DiffWalk": 0, "Sex": 1, "Age": 5,
    "Education": 4, "Income": 5
}

VALID_KIDNEY = {
    "age": 45, "bp": 80, "sg": 1.020, "al": 0, "su": 0, "rbc": 1, "pc": 1,
    "pcc": 0, "ba": 0, "bgr": 120, "bu": 30, "sc": 1.0, "sod": 140, "pot": 4.5,
    "hemo": 15, "pcv": 44, "wc": 8000, "rc": 5.0, "htn": 0, "dm": 0, "cad": 0,
    "appet": 1, "pe": 0, "ane": 0
}

VALID_DEPRESSION = {
    "gender": "Male", "age": 20, "profession": "Student", "academic_pressure": 3,
    "work_pressure": 0, "cgpa": 8.0, "study_satisfaction": 4, "job_satisfaction": 0,
    "sleep_duration": "7-8 hours", "dietary_habits": "Moderate", "degree": "BSc",
    "suicidal_thoughts": "No", "work_study_hours": 6, "financial_stress": 2,
    "family_history": "No"
}


# ── Validation Tests ─────────────────────────────────────────────────────────

def test_heart_missing_fields(client):
    """Heart prediction with missing fields should return 400."""
    response = client.post('/api/predict/heart', json={"age": 45})
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False


def test_diabetes_missing_fields(client):
    """Diabetes prediction with missing fields should return 400."""
    response = client.post('/api/predict/diabetes', json={"BMI": 25})
    assert response.status_code == 400


def test_kidney_missing_fields(client):
    """Kidney prediction with missing fields should return 400."""
    response = client.post('/api/predict/kidney', json={})
    assert response.status_code == 400


def test_depression_missing_fields(client):
    """Depression prediction with missing fields should return 400."""
    response = client.post('/api/predict/depression', json={"age": 20})
    assert response.status_code == 400


def test_heart_invalid_sex(client):
    """Heart prediction with invalid sex value should return 400."""
    data = {**VALID_HEART, "sex": "InvalidValue"}
    response = client.post('/api/predict/heart', json=data)
    assert response.status_code == 400


def test_empty_body(client):
    """POST with empty body should return 400."""
    response = client.post('/api/predict/heart', json={})
    assert response.status_code == 400


# ── Disease List Tests ───────────────────────────────────────────────────────

def test_get_diseases(client):
    """GET /diseases should return the 4 supported diseases."""
    response = client.get('/api/diseases')
    assert response.status_code == 200
    data = response.get_json()
    diseases = data['diseases']
    assert len(diseases) == 4
    ids = [d['id'] for d in diseases]
    assert 'heart' in ids
    assert 'diabetes' in ids
    assert 'kidney' in ids
    assert 'depression' in ids


# ── 404 Test ─────────────────────────────────────────────────────────────────

def test_unknown_endpoint(client):
    """Unknown endpoint should return 404 JSON."""
    response = client.get('/api/predict/unknown')
    assert response.status_code == 404
