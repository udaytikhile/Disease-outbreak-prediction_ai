"""
WSGI entry point for production servers (Gunicorn, uWSGI, etc.).
Ensures production config is used regardless of FLASK_ENV.
"""
from app import create_app

app = create_app('production')
