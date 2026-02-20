from flask import Blueprint, jsonify
from datetime import datetime, timezone
from ..services.model_service import model_service

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'models_loaded': model_service.loaded
    })
