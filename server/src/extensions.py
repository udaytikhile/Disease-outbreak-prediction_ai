from flask import request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging


def composite_limit_key() -> str:
    """Rate-limit key = IP only (BUG-5 fix: removed User-Agent to prevent bypass).

    Previous implementation used IP + User-Agent, which allowed attackers to
    bypass rate limiting by rotating User-Agent strings. Now uses IP only.
    """
    return get_remote_address()


# Initialize extensions
cors = CORS()
limiter = Limiter(key_func=composite_limit_key)
db = SQLAlchemy()
migrate = Migrate()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('api')
