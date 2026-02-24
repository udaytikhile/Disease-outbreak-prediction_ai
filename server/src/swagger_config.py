"""
Swagger / OpenAPI configuration for the Disease Outbreak Prediction API.
"""

SWAGGER_TEMPLATE = {
    "info": {
        "title": "Disease Outbreak Prediction API",
        "description": (
            "AI-powered disease prediction API supporting Heart Disease, Diabetes, "
            "Chronic Kidney Disease, and Depression screening models. "
            "Includes an NLP-based symptom checker and PDF report generation."
        ),
        "version": "2.0.0",
        "contact": {
            "name": "API Support",
        },
    },
    "basePath": "/api",
    "schemes": ["http", "https"],
    "tags": [
        {
            "name": "Health",
            "description": "Server health and readiness checks",
        },
        {
            "name": "Predictions",
            "description": "Disease prediction endpoints",
        },
        {
            "name": "Symptom Checker",
            "description": "AI sympom analysis and triage",
        },
        {
            "name": "History",
            "description": "Prediction history persistence",
        },
        {
            "name": "Reports",
            "description": "PDF report generation",
        },
    ],
}
