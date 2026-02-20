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
    logger.info(f"🚀 Starting Flask server in {env} mode")
    
    port = int(os.getenv('FLASK_PORT', '5001'))
    app.run(host='0.0.0.0', port=port)
