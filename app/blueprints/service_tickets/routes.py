from sqlalchemy import select
from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.service_tickets.service_ticketsSchemas import service_tickets_schema, service_ticket_schema, update_service_ticket_schema
from app.models import Admin, Customer, Mechanic, Product, ProductServiceTicket, db, ServiceTicket
from app.blueprints.inventory.inventorySchemas import product_service_ticket_schema
from flask import jsonify, request
from marshmallow import ValidationError
from app.extensions import limiter, cache
from app.utils.util import encode_token, token_required, not_found


# ---------------------- Service Tickets Endpoints ---------------------
# Endpoint to CREATE a new service ticket with validation error handling
@service_tickets_bp.route('/', methods=['POST'], strict_slashes=False)
@limiter.limit("10 per minute; 20 per hour; 100 per day")
def create_service_ticket():
    try:
        data = request.get_json()
        service_ticket = service_ticket_schema.load(data, session=db.session)
        db.session.add(service_ticket)
        db.session.commit()
        
        return jsonify({
            "message": "Service ticket created successfully",
            "service_ticket_id": service_ticket.id,
            "service_ticket": service_ticket_schema.dump(service_ticket)
        }), 201
        
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        print("Create Service Ticket Error:", e)  # Debugging line
        return jsonify({"error": str(e)}), 500


# Endpoint to GET ALL service tickets with validation error handling
@service_tickets_bp.route('/', methods=['GET'], strict_slashes=False)
#@cache.cached(timeout=60)  # Cache the response for 60 seconds to avoid repeated database calls
def get_service_tickets():
    try:
        page_str = request.args.get('page', '1')
        per_page_str = request.args.get('per_page', '10')
        
        try:
            page = int(page_str)
            per_page = int(per_page_str)
        except ValueError:
            return jsonify({"current_page": page_str,
                "service_tickets": [],
                "has_next": False,
                "has_prev": False,
                "page": page_str,
                "per_page": per_page_str,
                "total": 0,
                "total_pages": 0,
                "error": "Page not found or exceeds total pages"
            }), 200
            
        # Using .order_by() to ensure consisten pagination
        base_query = ServiceTicket.query.order_by(ServiceTicket.id)
        # Getting total number of service tickets
        total = base_query.count()
        # Calculating total pages
        total_pages = (total + per_page - 1) // per_page
        
        print(f"[DEBUG] total: {total}, total_pages: {total_pages}, requested page: {page}") # Debugging line
        
        # Checking if the requested page exceeds the total pages
        if total == 0 or page > total_pages or page < 1:
            return jsonify({
                            "current_page": page,
                            "service_tickets": [],
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
        service_tickets = pagination.items
        
        print(f"Requested page: {page}, total pages: {pagination.pages}") # Debugging line

        return jsonify({
            "current_page": pagination.page,
            "service_tickets": [service_ticket_schema.dump(ticket) for ticket in service_tickets],
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "total_pages": pagination.pages
        }), 200  
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Endpoint to GET ALL service tickets for a specific customer or mechanic requiring authentication and uses validation error handling
@service_tickets_bp.route('/my-tickets', methods=['GET'], strict_slashes=False)
#@limiter.limit("10 per minute; 20 per hour; 100 per day")
@token_required
def get_my_tickets(current_user):
    try:
        if isinstance(current_user, Customer):
            customer = Customer.query.get(current_user.id)
            if not customer:
                return not_found("Unauthorized")
            service_tickets = ServiceTicket.query.filter_by(customer_id=customer.id).all()
        elif isinstance(current_user, Mechanic):
            mechanic = Mechanic.query.get(current_user.id)
            if not mechanic:
                return not_found("Unauthorized")
            service_tickets = ServiceTicket.query.filter(ServiceTicket.mechanics.any(id=mechanic.id)).all()
        else:
            return not_found("Unauthorized")
        return service_tickets_schema.jsonify(service_tickets), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to GET a SPECIFIC service ticket by ID with validation error handling
@service_tickets_bp.route('/<int:service_ticket_id>', methods=['GET'], strict_slashes=False)
@cache.cached(timeout=60)  # Cache the response for 60 seconds to avoid repeated database calls
def get_service_ticket(service_ticket_id):
    try:
        service_ticket = db.session.get(ServiceTicket,service_ticket_id)
        if not service_ticket:
            return jsonify({"error": "Service ticket not found"}), 404
        return jsonify({
            "message": "Service ticket retrieved successfully",
            "service_ticket": service_ticket_schema.dump(service_ticket)
        }), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to UPDATE an existing service ticket with validation error handling
@service_tickets_bp.route('/<int:service_ticket_id>', methods=['PUT'], strict_slashes=False)
#@limiter.limit("10 per minute; 20 per hour; 100 per day")
def update_service_ticket(service_ticket_id):
    try:
        service_ticket_update = update_service_ticket_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    query = select(ServiceTicket).where(ServiceTicket.id == service_ticket_id)
    service_ticket = db.session.execute(query).scalars().first()
    if not service_ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    
    # Update the vin if provided
    if 'vin' in service_ticket_update:
        service_ticket.vin = service_ticket_update['vin']
    
    # Update the service ticket description if provided
    if 'service_desc' in service_ticket_update:
        service_ticket.service_desc = service_ticket_update['service_desc']
    
    # Add mechanics to the service ticket
    for mechanic_id in service_ticket_update.get('add_mechanic_ids', []):
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()
        
        if mechanic and mechanic not in service_ticket.mechanics:
            service_ticket.mechanics.append(mechanic)

    # Remove mechanics from the service ticket
    for mechanic_id in service_ticket_update.get('remove_mechanic_ids', []):
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()
        
        if mechanic and mechanic in service_ticket.mechanics:
            service_ticket.mechanics.remove(mechanic)

    db.session.commit()
    return jsonify({
        "message": "Service ticket updated successfully",
        "service_ticket": service_ticket_schema.dump(service_ticket)
    }), 200


# Endpoint to Add a product to an existing service ticket with validation error handling
@service_tickets_bp.route('/<int:service_ticket_id>/add_product', methods=['PUT'], strict_slashes=False)
@limiter.limit("10 per minute; 20 per hour; 100 per day")
def add_product_to_service_ticket(service_ticket_id):
    try:
        # Get the data from the request body
        data = request.get_json()
        if not data or 'product_id' not in data or 'quantity' not in data:
            return jsonify({"error": "Missing product_id or quantity"}), 400
        
        quantity = data['quantity']
        if not isinstance(quantity, int) or quantity <= 0:
            return jsonify({"error": "Quantity must be a positive number"}), 400
        
        # Get the service ticket and product item from the database
        service_ticket = ServiceTicket.query.get(service_ticket_id)
        if not service_ticket:
            return jsonify({"error": "Service ticket not found"}), 404

        product = Product.query.get(data['product_id'])
        if not product:
            return jsonify({"error": "Product item not found"}), 404

        # Check if the product item is already linked to the service ticket
        existing_link = ProductServiceTicket.query.filter_by(
            service_ticket_id=service_ticket.id,
            product_id=product.id
        ).first()
        
        if existing_link:
            return jsonify({"error": "This product is already linked to the service ticket"}), 400

        # Create a new ProductServiceTicket instance
        product_service_ticket = ProductServiceTicket(
            product_id=product.id,
            service_ticket_id=service_ticket.id,
            quantity=quantity
        )
        
        # Add the new product service ticket to the database
        db.session.add(product_service_ticket)
        db.session.commit()
        
        return jsonify({
            "message": "Product added successfully",
            "product_service_ticket_id": product_service_ticket.id,
            "product": product_service_ticket_schema.dump(product_service_ticket)
        }), 201
    
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        print(f"Error adding product to service ticket: {e}")  # Debugging line
        return jsonify({"error": str(e)}), 500


# Endpoint to DELETE a service ticket with validation error handling
@service_tickets_bp.route('/<int:service_ticket_id>', methods=['DELETE'], strict_slashes=False)
@limiter.limit("2 per day")
@token_required
def delete_service_ticket(current_user, service_ticket_id):
    if not isinstance(current_user, Admin):
        return jsonify({"error": "Only admins can delete service tickets"}), 403
    
    # Check if the service ticket exists
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)
    if not service_ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    
    # Delete the service ticket
    db.session.delete(service_ticket)
    db.session.commit()
    return jsonify({"message": f"Service ticket {service_ticket_id} deleted successfully"}), 200




