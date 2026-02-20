import os
import logging
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()

logger = logging.getLogger('api')

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-dev-secret-key')
    DEBUG = False
    TESTING = False
    MODEL_DIR = BASE_DIR.parent / 'ml' / 'models'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

    def __init__(self):
        # Prevent running in production with the insecure default key (BUG-10 fix)
        if os.getenv('SECRET_KEY', 'default-dev-secret-key') == 'default-dev-secret-key':
            logger.warning(
                "⚠️  WARNING: SECRET_KEY is not set via environment variable. "
                "Set SECRET_KEY env var before deploying to production!"
            )

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
