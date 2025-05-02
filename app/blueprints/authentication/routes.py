from sqlalchemy import select
from app.blueprints.authentication import authentications_bp
from app.blueprints.authentication.authSchemas import LoginSchema
from app.models import db, Customer
from flask import jsonify, request
from marshmallow import ValidationError
from app.extensions import limiter, cache
from app.utils.util import encode_token, token_required

# ----------------Authentication Endpoints-------------------
# Customer Login
@authentications_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute; 20 per hour; 100 per day")
def login_customer():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    
    try:
        credentials = LoginSchema().load(json_data)  # Validate and deserialize input data
    except ValidationError as err:
        return jsonify({"error": "Invalid input data", "details": err.messages}), 400
    
    email = credentials.get('email')
    password = credentials.get('password')

    query = select(Customer).where(Customer.email == email) # Query to find the customer by email
    customer = db.session.execute(query).scalar_one_or_none() # Fetch the customer by email
    
    if customer and customer.check_password(password):
        auth_token = encode_token(customer.id, user_type='customer') # Generate auth token for the customer
        return jsonify({
            "status": "success",
            "message": "Successfully logged in",
            "auth_token": auth_token,
            "customer": {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone,
            },
    }), 200
    
    return jsonify({"error": "Invalid email or password credentials"}), 401