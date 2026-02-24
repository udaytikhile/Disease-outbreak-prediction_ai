"""
Tests for the history and reports endpoints.
"""


# ── History Tests ────────────────────────────────────────────────────────────

def test_history_empty(client):
    """GET /history on empty DB should return empty list."""
    response = client.get('/api/history')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['predictions'] == []
    assert data['total'] == 0


def test_history_stats(client):
    """GET /history/stats should return stats structure."""
    response = client.get('/api/history/stats')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'total_predictions' in data
    assert 'by_disease' in data


def test_history_pagination(client):
    """History should support pagination params."""
    response = client.get('/api/history?page=1&per_page=5')
    assert response.status_code == 200
    data = response.get_json()
    assert 'page' in data
    assert 'pages' in data


def test_delete_nonexistent(client):
    """DELETE /history/999 should return 404."""
    response = client.delete('/api/history/999')
    assert response.status_code == 404


# ── Reports Tests ────────────────────────────────────────────────────────────

def test_report_missing_body(client):
    """POST /reports/generate without body should return 400 or 415."""
    response = client.post('/api/reports/generate')
    assert response.status_code in (400, 415)


def test_report_missing_fields(client):
    """POST /reports/generate with missing fields should return 400."""
    response = client.post('/api/reports/generate', json={"disease": "heart"})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
