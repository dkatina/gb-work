from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify

ma = Marshmallow()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    default_limit_exempt_when=lambda: False,
    default_limit_exempt_when_func=lambda: False,
)

# Error handling for rate limiting
@limiter.error_handler
def rate_limit_error(e):
    return jsonify({
        "error": "Rate limit exceeded. Please try again later.",
        "message": str(e.description),
        "code": e.code,
    }), e.code