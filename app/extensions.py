from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import jsonify
from flask_caching import Cache

# Marshmallow for serialization and deserialization
ma = Marshmallow()

# Flask-Limiter for rate limiting
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
    
# Flask-Caching for caching
cache = Cache(config={'CACHE_TYPE': 'simple'})