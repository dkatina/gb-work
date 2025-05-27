from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.blueprints.customers import customers_bp
from app.blueprints.customers.customersSchemas import CustomerSchema, customers_schema, customer_schema
from app.models import ServiceTicket, db, Customer, Admin
from flask import jsonify, request
from marshmallow import ValidationError
from app.extensions import limiter, cache
from app.utils.util import encode_token, not_found, token_required
from werkzeug.exceptions import NotFound

# -----------------Customers Endpoints--------------------

# Endpoint to CREATE a new customer with validation error handling
@customers_bp.route('/', methods=['POST'], strict_slashes=False)
@limiter.limit("10 per minute; 20 per hour; 100 per day")
def create_customer():
    try:
        data = request.get_json()
        customer = customer_schema.load(data)
        db.session.add(customer)
        db.session.commit()
        return customer_schema.jsonify(customer), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to GET ALL customers using pagination and has validation error handling
@customers_bp.route('/', methods=['GET'])
#@cache.cached(timeout=60)  # Cache the response for 60 seconds to avoid repeated database calls
#@limiter.limit("10 per minute; 20 per hour; 100 per day")
def get_customers():
    try:
        page_str = request.args.get('page', '1')
        per_page_str = request.args.get('per_page', '10')
        
        try:
            page = int(page_str)
            per_page = int(per_page_str)
        except ValueError:
            return jsonify({"current_page": page_str,
                "customers": [],
                "has_next": False,
                "has_prev": False,
                "page": page_str,
                "per_page": per_page_str,
                "total": 0,
                "total_pages": 0,
                "error": "Page not found or exceeds total pages"
            }), 200
            
        # Using .order_by() to ensure consisten pagination
        base_query = Customer.query.order_by(Customer.id)
        # Getting total number of customers
        total = base_query.count()
        # Calculating total pages
        total_pages = (total + per_page - 1) // per_page
        
        print(f"[DEBUG] total: {total}, total_pages: {total_pages}, requested page: {page}") # Debugging line
        
        # Checking if the requested page exceeds the total pages
        if total == 0 or page > total_pages or page < 1:
            return jsonify({
                            "current_page": page,
                            "customers": [],
                            "has_next": False,
                            "has_prev": False,
                            "page": page,
                            "per_page": per_page,
                            "total": total,
                            "total_pages": total_pages,
                            "error": "Page not found or exceeds total pages"
                            }), 200
        
        # Paginating the query
        pagination = base_query.paginate(page=page, per_page=per_page, error_out=False)
        customers = pagination.items
        
        print(f"Requested page: {page}, total pages: {pagination.pages}") # Debugging line

        return jsonify({
            "current_page": pagination.page,
            "customers": [CustomerSchema().dump(customer) for customer in customers],
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "total_pages": pagination.pages
        }), 200  
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to GET a SPECIFIC customer by ID with validation error handling
@customers_bp.route('/<int:id>', methods=['GET'], strict_slashes=False)
#@cache.cached(timeout=60)  # Cache the response for 60 seconds to avoid repeated database calls
def get_customer(id):
    try:
        customer = Customer.query.get_or_404(id)
        return CustomerSchema().jsonify(customer), 200
    except NotFound:
        return jsonify({"error": "Customer not found"}), 404
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to UPDATE an existing customer with validation error handling
@customers_bp.route('/<int:customer_id>', methods=['PUT'], strict_slashes=False)
#@limiter.limit("10 per minute; 20 per hour; 100 per day")
@token_required
def update_customer(user, customer_id): # Receiving customer_id from the token
    protected_emails = ['test.customer@example.com']
    try:
        customer = Customer.query.get_or_404(customer_id)
        
        # Check if the customer_id in the token matches the customer_id in the URL
        if getattr(user, 'user_type', None) != 'admin' and user.id != customer_id:
            return jsonify({"error": "Unauthorized access"}), 403
        
        data = request.get_json()
        
        # Block password change for test accounts
        if customer.email in protected_emails and 'password' in data:
            print("Attempt to change password for test account") # Debugging line
            return jsonify({"error": "This test account cannot change the password."}), 403
        
        data.pop("email", None)  # Remove email from data if present
        customer_schema = CustomerSchema()
        customer = customer_schema.load(data, instance=customer, session=db.session, partial=True)
        
        db.session.commit()
        
        return customer_schema.jsonify(customer), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        print("Update Customer Exception:", e) # Debugging line
        return jsonify({"error": str(e)}), 500


# Endpoint to DELETE a customer with validation error handling and requires token authentication
@customers_bp.route('/<int:customer_id>', methods=['DELETE'], strict_slashes=False)
#@limiter.limit("2 per day")
@token_required
def delete_customer(user, customer_id): # Receiving customer_id from the token
    protected_emails = ['john.customer@example.com']
    try:
        customer = Customer.query.get(customer_id)
        
        # Check if the customer_id in the token matches the customer_id in the URL
        if user.user_type not in ['admin', 'customer']:
            return jsonify({"error": "Unauthorized access"}), 403
        
        if user.user_type == 'customer' and user.id != customer_id:
            return jsonify({"error": "Customers can only delete their own accounts"}), 403

        if not customer:
            return jsonify({"error": "Customer not found."}), 404

        if customer.email in protected_emails:
            return jsonify({"error": "This test account cannot be deleted."}), 403
        
        if not customer:
            return jsonify({"error": "Customer not found."}), 404
        
        # Update related service tickets to remove the customer_id
        service_tickets = ServiceTicket.query.filter_by(customer_id=customer_id).all()
        for ticket in service_tickets:
            ticket.customer_id = None
            db.session.add(ticket)
        
        # Commit the changes to the service tickets
        db.session.commit()
        
        # Delete the customer
        db.session.delete(customer)
        db.session.commit()
        
        return jsonify({"message": f"Customer {customer_id} deleted successfully"}), 200
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Cannot delete customer with existing service tickets."}), 400
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

