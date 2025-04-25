from app.blueprints.customers import customers_bp
from app.blueprints.customers.customersSchemas import CustomerSchema, customers_schema
from app.models import db, Customer
from flask import jsonify, request
from marshmallow import ValidationError
from app.extensions import limiter

# Customers Endpoints
# Endpoint to CREATE a new customer with validation error handling
@customers_bp.route('/', methods=['POST'])
@limiter.limit("10 per minute; 20 per hour; 100 per day")
def create_customer():
    try:
        data = request.get_json()
        customer_schema = CustomerSchema()
        customer = customer_schema.load(data, session=db.session)
        db.session.add(customer)
        db.session.commit()
        return customer_schema.jsonify(customer), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to GET ALL customers with validation error handling
@customers_bp.route('/', methods=['GET'])
def get_customers():
    try:
        customers = Customer.query.all()
        return customers_schema.jsonify(customers), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to GET a SPECIFIC customer by ID with validation error handling
@customers_bp.route('/<int:id>', methods=['GET'])
def get_customer(id):
    try:
        customer = Customer.query.get_or_404(id)
        return CustomerSchema().jsonify(customer), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to UPDATE an existing customer with validation error handling
@customers_bp.route('/<int:id>', methods=['PUT'])
@limiter.limit("10 per minute; 20 per hour; 100 per day")
def update_customer(id):
    try:
        customer = Customer.query.get_or_404(id)
        data = request.get_json()
        customer_schema = CustomerSchema()
        customer = customer_schema.load(data, instance=customer, session=db.session)
        db.session.commit()
        return customer_schema.jsonify(customer), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to DELETE a customer with validation error handling
@customers_bp.route('/<int:id>', methods=['DELETE'])
@limiter.limit("2 per day")
def delete_customer(id):
    try:
        customer = Customer.query.get_or_404(id)
        db.session.delete(customer)
        db.session.commit()
        return jsonify({"message": "Customer deleted successfully"}), 204
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
