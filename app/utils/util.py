from datetime import datetime, timedelta, timezone
from jose import jwt
import jose
from functools import wraps
from flask import request, jsonify, current_app
from app.models import Admin, Customer, Mechanic

def encode_token(user_id, user_type): # uses unique pieces of information to create a token specific to the user
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=1), # Token expires in 1 hour
        'iat': datetime.now(timezone.utc), # Issued at time
        'sub': str(user_id), # Subject of the token (user ID)
        'user_type': user_type # User type (e.g., customer, mechanic, etc.)
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
        print("====== Incoming request ======") # Debugging line
        print(f"Request Headers: {request.headers}") # Debugging line
        
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
            print(f"Token found: {token}") # Debugging line
            parts = token.split()
            if len(parts) == 2 and parts[0] == 'Bearer':
                token = parts[1]
            else:
                print("Invalid token format") # Debugging line
                return jsonify({'error': 'Invalid token format Unauthorized'}), 401
            
        else:
            print("Authorization header not found") # Debugging line
            return jsonify({'error': 'Authorization header not found Unauthorized'}), 401

        print(f"Decoded token: {token}")
        
        secret_key = current_app.config.get('SECRET_KEY', 'default_secret_key')
        try:
            data = jwt.decode(token, secret_key, algorithms=['HS256']) # Decode the token using the secret key and algorithm
            print(f"Decoded data: {data}") # Debugging line
            
            user_id = data['sub'] # Get the user ID from the decoded token
            user_type = data['user_type'] # Get the user type from the decoded token
            
            # Loading appropriate user based on user_type
            if user_type == 'customer':
                user = Customer.query.get(user_id)
            elif user_type == 'mechanic':
                user = Mechanic.query.get(user_id)
            elif user_type == 'admin':
                user = Admin.query.get(user_id)
            else:
                print(f"Invalid user type: {user_type} in token")
                return jsonify({'error': 'Invalid user type!'}), 401
            
            if not user:
                print(f"User not found for ID: {user_id} and type: {user_type}")
                return jsonify({'error': 'Token invalid or user not found'}), 401

            # Attaching the user_type to the user object
            user.user_type = user_type
            
        except jose.JWTError as e: # Handle JWT errors
            print(f"JWT decode Error: {e}")
            return jsonify({'error': 'Unauthorized'}), 401

        return f(user, *args, **kwargs) # Call the original function with the user ID
    
    return decorated # Return the decorated function

# Error handler for 404 Not Found
def not_found(message="Resource not found."):
    return jsonify({"error": message}), 404
