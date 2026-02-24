"""
Application-wide constants.

Single source of truth for disease metadata, risk levels, and other
shared enumerations used across routes, services, and templates.
"""

# ── Supported Disease Registry ──────────────────────────────────────────
# Used by predict routes, symptom checker, reports, and health endpoint.
DISEASES = {
    'heart': {
        'id': 'heart',
        'name': 'Heart Disease',
        'description': 'Predict cardiovascular disease risk',
        'icon': '❤️',
    },
    'diabetes': {
        'id': 'diabetes',
        'name': 'Diabetes',
        'description': 'Predict diabetes risk',
        'icon': '🩺',
    },
    'kidney': {
        'id': 'kidney',
        'name': 'Chronic Kidney Disease',
        'description': 'Predict chronic kidney disease risk',
        'icon': '🫘',
    },
    'depression': {
        'id': 'depression',
        'name': 'Depression',
        'description': 'Predict depression risk',
        'icon': '🧠',
    },
}

# ── Risk Level Definitions ──────────────────────────────────────────────
RISK_LEVELS = {
    'High': {'color': '#ef4444', 'label': 'High Risk'},
    'Low': {'color': '#22c55e', 'label': 'Low Risk'},
}

# ── Rate Limit Defaults ────────────────────────────────────────────────
PREDICTION_RATE_LIMIT = "10 per minute"
SYMPTOM_RATE_LIMIT = "15 per minute"
CHAT_RATE_LIMIT = "20 per minute"
REPORT_RATE_LIMIT = "5 per minute"
