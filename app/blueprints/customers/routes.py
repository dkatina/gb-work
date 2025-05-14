from sqlalchemy import select
from app.blueprints.customers import customers_bp
from app.blueprints.customers.customersSchemas import CustomerSchema, customers_schema
from app.models import db, Customer
from flask import jsonify, request
from marshmallow import ValidationError
from app.extensions import limiter, cache
from app.utils.util import encode_token, not_found, token_required

# -----------------Customers Endpoints--------------------

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

# Endpoint to GET ALL customers using pagination and has validation error handling
@customers_bp.route('/', methods=['GET'])
@limiter.limit("10 per minute; 20 per hour; 100 per day")
def get_customers():
     try:
         # Setting default values for page and per_page
         page = int(request.args.get('page', 1))
         per_page = min(int(request.args.get('per_page', 10)), 100)  # Limit per_page to a maximum of 100
         
         query = select (Customer)
         pagination = db.paginate(query, page=page, per_page=per_page, error_out=False)
         
         if not pagination.items:
             return not_found({"No customers found on this page."}), 404
         
         return jsonify({
            "customers": customers_schema.dump(pagination.items),
            "total": pagination.total,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "current_page": pagination.page,
            "total_pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
         }), 200
         
     except ValidationError as err:
         return jsonify(err.messages), 400
     except Exception as e:
         return jsonify({"error": str(e)}), 500

# Endpoint to GET a SPECIFIC customer by ID with validation error handling
@customers_bp.route('/<int:id>', methods=['GET'])
@cache.cached(timeout=60)  # Cache the response for 60 seconds to avoid repeated database calls
def get_customer(id):
    try:
        customer = Customer.query.get_or_404(id)
        return CustomerSchema().jsonify(customer), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to UPDATE an existing customer with validation error handling
@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@limiter.limit("10 per minute; 20 per hour; 100 per day")
@token_required
def update_customer(user, customer_id): # Receiving customer_id from the token
    try:
        customer = Customer.query.get_or_404(customer_id)
        
        # Check if the customer_id in the token matches the customer_id in the URL
        if user.id != customer_id:
            return jsonify({"error": "Unauthorized access"}), 403
        
        data = request.get_json()
        customer_schema = CustomerSchema()
        customer = customer_schema.load(data, instance=customer, session=db.session)
        db.session.commit()
        return customer_schema.jsonify(customer), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to DELETE a customer with validation error handling and requires token authentication
@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
@limiter.limit("2 per day")
@token_required
def delete_customer(user, customer_id): # Receiving customer_id from the token
    try:
        customer = Customer.query.get_or_404(customer_id)
        
        # Check if the customer_id in the token matches the customer_id in the URL
        if user.id != customer_id:
            return jsonify({"error": "Unauthorized access"}), 403
    
        db.session.delete(customer)
        db.session.commit()
        return jsonify({"message": f"Customer {customer_id} deleted successfully"}), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

