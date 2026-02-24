import os
import logging
from src import create_app

# Create app instance
env = os.getenv('FLASK_ENV', 'default')
app = create_app(env)

if __name__ == '__main__':
    # Configuration is already handled in create_app via config.py
    # Debug mode is set in config based on env
    
    logger = logging.getLogger('api')
    
    # Feature 5: Minimal Async
    logger.info(f"🚀 Starting Flask server in {env} mode")
    logger.info("ℹ️  Running with threaded=True (Flask default) for concurrent requests.")
    logger.info("ℹ️  For true async production scale, use Gunicorn: gunicorn -w 4 app:app")
    
    port = int(os.getenv('FLASK_PORT', '5001'))
    app.run(host='0.0.0.0', port=port, threaded=True)

