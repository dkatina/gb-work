from datetime import datetime, timedelta, timezone
from jose import jwt
import jose
from functools import wraps
from flask import request, jsonify, current_app

def encode_token(user_id): # uses unique pieces of information to create a token specific to the user
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=1), # Token expires in 1 hour
        'iat': datetime.now(timezone.utc), # Issued at time
        'sub': str(user_id) # Subject of the token (user ID)
    }
    secret_key = current_app.config.get('SECRET_KEY', 'default_secret_key') # Get the secret key from the config
    token = jwt.encode(payload, secret_key, algorithm='HS256') # Encode the token using the secret key and algorithm
    return token # Return the encoded token

def is_testing_mode():
    from flask import current_app
    return current_app.config.get('TESTING', False)

def token_required(f): # Decorator to require token for certain routes
    @wraps(f) # Preserve the original function's metadata
    def decorated(*args, **kwargs):
        token = None # Initialize token variable
        
        if is_testing_mode():
            return f(*args, **kwargs)
        
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
            parts = token.split()
            if len(parts) == 2 and parts[0] == 'Bearer':
                token = parts[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        secret_key = current_app.config.get('SECRET_KEY', 'default_secret_key')
        try:
            data = jwt.decode(token, secret_key, algorithms=['HS256']) # Decode the token using the secret key and algorithm
            current_user_id = data['sub'] # Get the user ID from the decoded token
        except jose.JWTError as e: # Handle JWT errors
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user_id, *args, **kwargs) # Call the original function with the user ID
    
    return decorated # Return the decorated function