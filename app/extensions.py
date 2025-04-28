from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import jsonify
from flask_caching import Cache

# Marshmallow for serialization and deserialization
ma = Marshmallow()

# Error handling for rate limiting
def rate_limit_error(e):
    return jsonify({
        "error": "Rate limit exceeded. Please try again later.",
        "message": "You have exceeded the allowed number of requests.",
        "code": 429,
    }), 429
    
# Flask-Limiter for rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    on_breach=rate_limit_error
)
    
# Flask-Caching for caching
cache = Cache(config={'CACHE_TYPE': 'simple'})