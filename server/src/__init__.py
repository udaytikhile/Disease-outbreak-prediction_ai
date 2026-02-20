from flask import Flask, jsonify
from .extensions import cors, logger
from .routes.health import health_bp
from .routes.predict import predict_bp
from config import config
from .services.model_service import model_service

def create_app(config_name='default'):
    """Application factory"""
    app = Flask(__name__)
    
    # Load config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    cors.init_app(app, origins=['http://localhost:5173', 'http://127.0.0.1:5173'])
    
    from .extensions import limiter
    limiter.init_app(app)
    
    # Initialize services
    with app.app_context():
        # Load models on startup
        try:
            model_service.load_models(app.config['MODEL_DIR'])
        except Exception as e:
            logger.error(f"Failed to load models: {e}")

    # Register blueprints
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(predict_bp, url_prefix='/api')
    
    # Error handlers
    from marshmallow import ValidationError
    from werkzeug.exceptions import HTTPException

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return jsonify({'success': False, 'error': e.messages}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def server_error(error):
        logger.error(f"500 error: {error}", exc_info=True)
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({'success': False, 'error': f"Rate limit exceeded: {e.description}"}), 429

    @app.errorhandler(HTTPException)
    def handle_exception(e):
        """Return JSON instead of HTML for HTTP errors."""
        response = e.get_response()
        response.data = jsonify({
            "success": False,
            "error": e.description,
        }).data
        response.content_type = "application/json"
        return response

    return app
