from datetime import datetime, timedelta, timezone
from jose import jwt
import jose

SECRET_KEY = "default_secret_key"

def encode_token(user_id): # uses unique pieces of information to create a token specific to the user
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=1), # Token expires in 1 hour
        'iat': datetime.now(timezone.utc), # Issued at time
        'sub': str(user_id) # Subject of the token (user ID)
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256') # Encode the token using the secret key and algorithm
    return token # Return the encoded token