"""
Pytest fixtures for the Disease Outbreak Prediction API test suite.
"""
import pytest
import sys
import os

# Add server directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import create_app
from src.extensions import db as _db


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app('testing')
    yield app


@pytest.fixture(scope='function')
def client(app):
    """Create a test client."""
    with app.test_client() as client:
        with app.app_context():
            _db.create_all()
            yield client
            _db.session.remove()
            _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    """Provide the database session."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()
