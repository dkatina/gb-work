from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.service_tickets.service_ticketsSchemas import service_tickets_schema, service_ticket_schema  
from app.models import db, ServiceTicket
from flask import jsonify, request
from marshmallow import ValidationError


# Service Tickets Endpoints
# Endpoint to get all service tickets with validation error handling
@service_tickets_bp.route('/', methods=['GET'])
def get_service_tickets():
    try:
        service_tickets = ServiceTicket.query.all()
        return service_tickets_schema.jsonify(service_tickets), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to get a specific service ticket by ID with validation error handling
@service_tickets_bp.route('/<int:id>', methods=['GET'])
def get_service_ticket(id):
    try:
        service_ticket = ServiceTicket.query.get_or_404(id)
        return service_ticket_schema.jsonify(service_ticket), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to create a new service ticket with validation error handling
@service_tickets_bp.route('/', methods=['POST'])
def create_service_ticket():
    try:
        data = request.get_json()
        service_ticket = service_tickets_schema.load(data, session=db.session)
        db.session.add(service_ticket)
        db.session.commit()
        return service_ticket_schema.jsonify(service_ticket), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to update an existing service ticket with validation error handling
@service_tickets_bp.route('/<int:id>', methods=['PUT'])
def update_service_ticket(id):
    try:
        service_ticket = ServiceTicket.query.get_or_404(id)
        data = request.get_json()
        service_ticket = service_tickets_schema.load(data, instance=service_ticket, session=db.session)
        db.session.commit()
        return service_ticket_schema.jsonify(service_ticket), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to delete a service ticket with validation error handling
@service_tickets_bp.route('/<int:id>', methods=['DELETE'])
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