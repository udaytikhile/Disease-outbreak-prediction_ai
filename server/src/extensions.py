
import os
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


# Rate limiter storage backend.
# In production, set RATELIMIT_STORAGE_URI=redis://localhost:6379/0
# to share state across Gunicorn workers. Default: in-memory (dev only).
_ratelimit_storage_uri = os.getenv("RATELIMIT_STORAGE_URI", "memory://")

# Initialize extensions
cors = CORS()
limiter = Limiter(
    key_func=composite_limit_key,
    storage_uri=_ratelimit_storage_uri,
)
db = SQLAlchemy()
migrate = Migrate()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('api')

if _ratelimit_storage_uri == "memory://":
    logger.warning(
        "⚠️  Flask rate limiter is using in-memory storage (not safe for "
        "production with multiple workers). Set RATELIMIT_STORAGE_URI="
        "redis://localhost:6379/0 in your environment."
    )
else:
    logger.info("✅ Flask rate limiter using: %s", _ratelimit_storage_uri)

