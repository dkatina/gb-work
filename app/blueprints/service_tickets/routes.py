from sqlalchemy import select
from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.service_tickets.service_ticketsSchemas import service_tickets_schema, service_ticket_schema, update_service_ticket_schema
from app.models import Admin, Customer, Inventory, InventoryServiceTicket, Mechanic, db, ServiceTicket
from flask import jsonify, request
from marshmallow import ValidationError
from app.extensions import limiter, cache
from app.utils.util import encode_token, token_required


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
        return service_ticket_schema.jsonify(service_ticket), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Endpoint to GET ALL service tickets with validation error handling
@service_tickets_bp.route('/', methods=['GET'], strict_slashes=False)
@cache.cached(timeout=60)  # Cache the response for 60 seconds to avoid repeated database calls
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
@limiter.limit("10 per minute; 20 per hour; 100 per day")
@token_required
def get_my_tickets(current_user):
    try:
        if isinstance(current_user, Customer):
            customer_id = current_user.id
            service_tickets = ServiceTicket.query.filter_by(customer_id=customer_id).all()
        elif isinstance(current_user, Mechanic):
            mechanic_id = current_user.id
            service_tickets = ServiceTicket.query.filter(ServiceTicket.mechanics.any(id=mechanic_id)).all()
        else:
            return jsonify({"error": "Invalid user type"}), 400
        return service_tickets_schema.jsonify(service_tickets), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to GET a SPECIFIC service ticket by ID with validation error handling
@service_tickets_bp.route('/<int:service_ticket_id>', methods=['GET'])
@cache.cached(timeout=60)  # Cache the response for 60 seconds to avoid repeated database calls
def get_service_ticket(service_ticket_id):
    try:
        service_ticket = ServiceTicket.query.get_or_404(service_ticket_id)
        return service_ticket_schema.jsonify(service_ticket), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to UPDATE an existing service ticket with validation error handling
@service_tickets_bp.route('/<int:service_ticket_id>', methods=['PUT'])
@limiter.limit("10 per minute; 20 per hour; 100 per day")
def update_service_ticket(service_ticket_id):
    try:
        service_ticket_update = update_service_ticket_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    query = select(ServiceTicket).where(ServiceTicket.id == service_ticket_id)
    service_ticket = db.session.execute(query).scalars().first()
    
    for mechanic_id in service_ticket_update['add_mechanic_ids']:
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()
        
        if mechanic and mechanic not in service_ticket.mechanics:
            service_ticket.mechanics.append(mechanic)
            
    for mechanic_id in service_ticket_update['remove_mechanic_ids']:
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()
        
        if mechanic and mechanic in service_ticket.mechanics:
            service_ticket.mechanics.remove(mechanic)

    db.session.commit()
    return service_ticket_schema.jsonify(service_ticket), 200


# Endpoint to Add a part to an existing service ticket with validation error handling
@service_tickets_bp.route('/<int:service_ticket_id>/add_part', methods=['PUT'])
@limiter.limit("10 per minute; 20 per hour; 100 per day")
def add_part_to_service_ticket(service_ticket_id):
    try:
        # Get the data from the request body
        data = request.get_json()
        
        # Get the service ticket and inventory item from the database
        service_ticket = ServiceTicket.query.get_or_404(service_ticket_id)
        inventory_item = Inventory.query.get_or_404(data['inventory_id'])
        
        # Check if the inventory item is already linked to the service ticket
        existing_link = InventoryServiceTicket.query.filter_by(
            service_ticket_id=service_ticket.id,
            inventory_id=inventory_item.id
        ).first()
        if existing_link:
            return jsonify({"error": "This part is already linked to the service ticket"}), 400

        # Create a new InventoryServiceTicket instance
        inventory_service_ticket = InventoryServiceTicket(
            inventory_id=inventory_item.id,
            service_ticket_id=service_ticket.id,
            quantity=data['quantity']
        )
        
        db.session.add(inventory_service_ticket)
        db.session.commit()
        
        return jsonify({"message": "Part added successfully", "inventory_service_ticket_id": inventory_service_ticket.id}), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Endpoint to DELETE a service ticket with validation error handling
@service_tickets_bp.route('/<int:service_ticket_id>', methods=['DELETE'])
@limiter.limit("2 per day")
def delete_service_ticket(service_ticket_id):
    query = select(ServiceTicket).where(ServiceTicket.id == service_ticket_id)
    service_ticket = db.session.execute(query).scalars().first()
    
    db.session.delete(service_ticket)
    db.session.commit()
    return jsonify({"message": f"Service ticket {service_ticket_id} deleted successfully"}), 200




