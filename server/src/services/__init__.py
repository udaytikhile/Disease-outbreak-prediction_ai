"""
Services package — business logic layer.

Services contain all domain logic and are independent of the HTTP layer.
Routes (controllers) delegate to services and never contain business rules.

Available services:
    model_service: ML model loading, prediction, SHAP explanations
    llm_service: Gemini-powered conversational symptom checker
    report_service: PDF report generation
    symptom_service: Rule-based symptom analysis engine
    symptom_data: Symptom checker data constants
"""

__all__ = [
    'model_service',
    'llm_service',
    'report_service',
    'symptom_service',
    'symptom_data',
]
