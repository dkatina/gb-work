from sqlalchemy import select
from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.service_tickets.service_ticketsSchemas import service_tickets_schema, service_ticket_schema, update_service_ticket_schema
from app.models import Mechanic, db, ServiceTicket
from flask import jsonify, request
from marshmallow import ValidationError
from app.extensions import limiter, cache


# Service Tickets Endpoints
# Endpoint to CREATE a new service ticket with validation error handling
@service_tickets_bp.route('/', methods=['POST'])
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
@service_tickets_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)  # Cache the response for 60 seconds to avoid repeated database calls
def get_service_tickets():
    try:
        service_tickets = ServiceTicket.query.all()
        return service_tickets_schema.jsonify(service_tickets), 200
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



# Endpoint to DELETE a service ticket with validation error handling
@service_tickets_bp.route('/<int:service_ticket_id>', methods=['DELETE'])
@limiter.limit("2 per day")
def delete_service_ticket(service_ticket_id):
    query = select(ServiceTicket).where(ServiceTicket.id == service_ticket_id)
    service_ticket = db.session.execute(query).scalars().first()
    
    db.session.delete(service_ticket)
    db.session.commit()
    return jsonify({"message": f"Service ticket {service_ticket_id} deleted successfully"}), 200




