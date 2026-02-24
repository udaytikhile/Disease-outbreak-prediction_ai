"""
Tests for the symptom checker endpoints.
"""


def test_symptom_check_requires_body(client):
    """POST /symptom-check without body should return 400."""
    response = client.post('/api/symptom-check')
    assert response.status_code in (400, 415)


def test_symptom_check_requires_symptoms(client):
    """POST /symptom-check without symptoms list should return 400."""
    response = client.post('/api/symptom-check', json={})
    assert response.status_code == 400


def test_symptom_check_valid(client):
    """POST /symptom-check with valid symptoms should return analysis."""
    response = client.post('/api/symptom-check', json={
        "symptoms": ["chest pain", "shortness of breath"],
        "age": 55,
        "sex": "male"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'analysis' in data
    assert 'diseases' in data['analysis']
    assert 'advice' in data['analysis']


def test_symptom_check_emergency_detection(client):
    """Chest pain + shortness of breath should trigger emergency alert."""
    response = client.post('/api/symptom-check', json={
        "symptoms": ["chest pain", "shortness of breath", "cold sweats"]
    })
    data = response.get_json()
    assert data['success'] is True
    assert data['analysis']['emergency'] is True
    assert len(data['analysis']['emergency_alerts']) > 0


def test_symptom_suggestions(client):
    """GET /symptom-suggestions should return suggestions list."""
    response = client.get('/api/symptom-suggestions')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert isinstance(data['suggestions'], list)
    assert len(data['suggestions']) > 0


def test_symptom_checker_mode(client):
    """GET /symptom-checker/mode should return mode info."""
    response = client.get('/api/symptom-checker/mode')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'mode' in data


def test_symptom_check_too_many(client):
    """POST with >20 symptoms should return 400."""
    symptoms = [f"symptom_{i}" for i in range(25)]
    response = client.post('/api/symptom-check', json={"symptoms": symptoms})
    assert response.status_code == 400


def test_symptom_check_empty_strings(client):
    """POST with only empty strings should return 400."""
    response = client.post('/api/symptom-check', json={"symptoms": ["", "  ", ""]})
    assert response.status_code == 400
