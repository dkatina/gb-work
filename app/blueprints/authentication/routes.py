from sqlalchemy import select
from app.blueprints.authentication import authentications_bp
from app.blueprints.authentication.authSchemas import LoginSchema
from app.models import db, Customer, Mechanic, Admin
from flask import jsonify, request
from marshmallow import ValidationError
from app.extensions import limiter, cache
from app.utils.util import encode_token, token_required

# ----------------Authentication Endpoints-------------------
# Login endpoint for both customers and mechanics
@authentications_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute; 20 per hour; 100 per day")
def login():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    
    try:
        credentials = LoginSchema().load(json_data)  # Validate and deserialize input data
    except ValidationError as err:
        return jsonify({"error": "Invalid input data", "details": err.messages}), 400
    
    email = credentials.get('email')
    password = credentials.get('password')

    # First try to find the customer
    query = select(Customer).where(Customer.email == email)
    customer = db.session.execute(query).scalar_one_or_none()
    if customer and customer.check_password(password):
        auth_token = encode_token(customer.id, user_type='customer')
        return jsonify({
            "status": "success",
            "message": "Customer login successful",
            "auth_token": auth_token,
            "customer": {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone,
            },
        }), 200
        
    # Then try to find mechanic
    query = select(Mechanic).where(Mechanic.email == email)
    mechanic = db.session.execute(query).scalar_one_or_none()
    if mechanic and mechanic.check_password(password):
        auth_token = encode_token(mechanic.id, user_type='mechanic')
        return jsonify({
            "status": "success",
            "message": "Mechanic login successful",
            "auth_token": auth_token,
            "mechanic": {
                "id": mechanic.id,
                "name": mechanic.name,
                "email": mechanic.email,
                "phone": mechanic.phone,
            },
        }), 200
        
    # Finally try to find admin
    query = select(Admin).where(Admin.email == email)
    admin = db.session.execute(query).scalar_one_or_none()
    if admin and admin.check_password(password):
        auth_token = encode_token(admin.id, user_type='admin')
        return jsonify({
            "status": "success",
            "message": "Admin login successful",
            "auth_token": auth_token,
            "admin": {
                "id": admin.id,
                "name": admin.name,
                "email": admin.email,
            },
        }), 200
        
    return jsonify({"error": "Invalid email or password credentials"}), 401


