from flask import Blueprint, jsonify
from datetime import datetime, timezone
from ..services.model_service import model_service

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint — reports model versions and SHAP availability."""
    try:
        import shap  # noqa
        shap_available = True
    except ImportError:
        shap_available = False

    return jsonify({
        'status':         'healthy',
        'timestamp':      datetime.now(timezone.utc).isoformat(),
        'models_loaded':  model_service.loaded,
        'shap_available': shap_available,
        # Feature 4: per-model version info
        'model_versions': model_service.get_model_versions() if model_service.loaded else {},
    })

