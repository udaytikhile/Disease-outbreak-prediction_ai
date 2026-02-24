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
    # Bug 1 fix: explicit CORS_ORIGINS — never use wildcard origins
    CORS_ORIGINS = ['http://localhost:5173', 'http://127.0.0.1:5173']

    # Database — SQLite by default for dev, PostgreSQL in production via DATABASE_URL
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f"sqlite:///{BASE_DIR.parent / 'outbreak.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # LLM
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')


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
        # Bug 1 fix: read CORS_ORIGINS from env var in production
        # Set CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
        cors_env = os.getenv('CORS_ORIGINS', '')
        if cors_env:
            self.CORS_ORIGINS = [o.strip() for o in cors_env.split(',') if o.strip()]
        else:
            logger.warning(
                "⚠️  WARNING: CORS_ORIGINS env var is not set. "
                "Defaulting to localhost only. Set CORS_ORIGINS before deploying!"
            )


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
