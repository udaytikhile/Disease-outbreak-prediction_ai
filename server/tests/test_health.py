"""
Tests for the /api/health endpoint.
"""


def test_health_returns_200(client):
    """Health check should return 200 with status 'healthy'."""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'


def test_health_has_required_fields(client):
    """Health check response should contain all required fields."""
    response = client.get('/api/health')
    data = response.get_json()
    assert 'status' in data
    assert 'timestamp' in data
    assert 'models_loaded' in data
    assert 'shap_available' in data
    assert 'model_versions' in data


def test_health_timestamp_is_iso(client):
    """Timestamp should be ISO 8601 format."""
    response = client.get('/api/health')
    data = response.get_json()
    # Should contain a 'T' separator (ISO 8601)
    assert 'T' in data['timestamp']
