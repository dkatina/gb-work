from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.service_tickets.service_ticketsSchemas import service_tickets_schema, service_ticket_schema  
from app.models import db, ServiceTicket
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
@cache.cached(timeout=60)  # Cache the response for 60 seconds
def get_service_tickets():
    try:
        service_tickets = ServiceTicket.query.all()
        return service_tickets_schema.jsonify(service_tickets), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to GET a SPECIFIC service ticket by ID with validation error handling
@service_tickets_bp.route('/<int:id>', methods=['GET'])
@cache.cached(timeout=60)  # Cache the response for 60 seconds
def get_service_ticket(id):
    try:
        service_ticket = ServiceTicket.query.get_or_404(id)
        return service_ticket_schema.jsonify(service_ticket), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to UPDATE an existing service ticket with validation error handling
@service_tickets_bp.route('/<int:id>', methods=['PUT'])
@limiter.limit("10 per minute; 20 per hour; 100 per day")
def update_service_ticket(id):
    try:
        service_ticket = ServiceTicket.query.get_or_404(id)
        data = request.get_json()
        service_ticket = service_ticket_schema.load(data, instance=service_ticket, session=db.session)
        db.session.commit()
        return service_ticket_schema.jsonify(service_ticket), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to DELETE a service ticket with validation error handling
@service_tickets_bp.route('/<int:id>', methods=['DELETE'])
@limiter.limit("2 per day")
def delete_service_ticket(id):
    try:
        service_ticket = ServiceTicket.query.get_or_404(id)
        db.session.delete(service_ticket)
        db.session.commit()
        return jsonify({"message": "Service ticket deleted successfully"}), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
