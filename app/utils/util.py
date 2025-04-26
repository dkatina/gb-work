from datetime import datetime, timedelta, timezone
from jose import jwt
import jose
from functools import wraps
from flask import request, jsonify

SECRET_KEY = "default_secret_key"

def encode_token(user_id): # uses unique pieces of information to create a token specific to the user
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=1), # Token expires in 1 hour
        'iat': datetime.now(timezone.utc), # Issued at time
        'sub': str(user_id) # Subject of the token (user ID)
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256') # Encode the token using the secret key and algorithm
    return token # Return the encoded token

def token_required(f): # Decorator to require token for certain routes
    @wraps(f) # Preserve the original function's metadata
    def decorated(*args, **kwargs):
        token = None # Initialize token variable
        
        if 'Authorization' in request.headers: # Check if token is in the headers
            token = request.headers['Authorization'].split(" ")[1] # Extract the token from the header
        
        if not token: # If no token is provided, return an error
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256']) # Decode the token using the secret key and algorithm
            current_user_id = data['sub'] # Get the user ID from the decoded token
        except jose.JWTError as e: # Handle JWT errors
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user_id, *args, **kwargs) # Call the original function with the user ID
    
    return decorated # Return the decorated function