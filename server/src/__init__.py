from flask import Flask, jsonify
from .extensions import cors, logger, db, migrate
from .routes.health import health_bp
from .routes.predict import predict_bp
from .routes.symptom_checker import symptom_checker_bp
from .routes.history import history_bp
from .routes.reports import reports_bp
from config import config
from .services.model_service import model_service  # noqa: F401

def create_app(config_name='default'):
    """Application factory"""
    app = Flask(__name__)

    # Load config
    app.config.from_object(config[config_name])

    # Initialize extensions
    # Bug 1 fix: CORS_ORIGINS comes from config — never hard-coded or wildcard
    cors.init_app(app, origins=app.config['CORS_ORIGINS'])

    from .extensions import limiter
    limiter.init_app(app)

    # Initialize database
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so Alembic can detect them
    from . import models  # noqa: F401

    # Initialize Swagger/OpenAPI docs
    try:
        from flasgger import Swagger
        from .swagger_config import SWAGGER_TEMPLATE
        Swagger(app, template=SWAGGER_TEMPLATE)
    except ImportError:
        logger.warning("⚠️  flasgger not installed — Swagger docs disabled.")

    # Initialize services
    with app.app_context():
        # Create tables if they don't exist (for dev/SQLite)
        db.create_all()

        # Load models on startup
        try:
            model_service.load_models(app.config['MODEL_DIR'])
        except RuntimeError as e:
            if config_name == 'production':
                logger.critical(
                    f"🚨 STARTUP FAILURE: {e}. "
                    "The server will not start until models are available."
                )
                raise
            else:
                # In dev/testing, warn but don't crash — allows tests to run
                # without ML models present
                logger.warning(
                    f"⚠️  Model loading skipped: {e}. "
                    "Prediction endpoints will return errors."
                )

    # Register blueprints
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(predict_bp, url_prefix='/api')
    app.register_blueprint(symptom_checker_bp, url_prefix='/api')
    app.register_blueprint(history_bp, url_prefix='/api')
    app.register_blueprint(reports_bp, url_prefix='/api')

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
