from app.blueprints.mechanics import mechanics_bp
from app.blueprints.mechanics.mechanicsSchemas import MechanicSchema, mechanics_schema, mechanic_schema
from app.models import ServiceTicket, db, Mechanic, Admin
from flask import jsonify, request
from marshmallow import ValidationError
from app.extensions import limiter, cache

# ---------------- Mechanics Endpoints --------------------
# Endpoint to create a new mechanic with validation error handling
@mechanics_bp.route('/', methods=['POST'])
@limiter.limit("10 per minute; 20 per hour; 100 per day")
def create_mechanic():
    try:
        data = request.get_json()
        mechanic_schema = MechanicSchema()
        mechanic = mechanic_schema.load(data, session=db.session)
        db.session.add(mechanic)
        db.session.commit()
        return mechanic_schema.jsonify(mechanic), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to GET ALL mechanics with validation error handling
@mechanics_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)  # Cache the response for 60 seconds to avoid repeated database calls
def get_mechanics():
    try:
        mechanics = Mechanic.query.all()
        return mechanics_schema.jsonify(mechanics), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to GET a SPECIFIC mechanic by ID with validation error handling
@mechanics_bp.route('/<int:id>', methods=['GET'])
@cache.cached(timeout=60)  # Cache the response for 60 seconds to avoid repeated database calls
def get_mechanic(id):
    try:
        mechanic = Mechanic.query.get_or_404(id)
        return mechanic_schema.jsonify(mechanic), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Endpoint to GET a list of mechanics in the order of who has worked on the most tickets with validation error handling
@mechanics_bp.route('/most-worked', methods=['GET'])
@cache.cached(timeout=60)  # Cache the response for 60 seconds to avoid repeated database calls
def get_most_worked_mechanics():
    try:
        mechanics = db.session.query(Mechanic).join(ServiceTicket.mechanics).group_by(Mechanic.id).order_by(db.func.count(ServiceTicket.id).desc()).all()
        return mechanics_schema.jsonify(mechanics), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Endpoint to do a search for mechanics by name using GET with query parameters and validation error handling
@mechanics_bp.route('/search', methods=['GET'])
@cache.cached(timeout=60)  # Cache the response for 60 seconds to avoid repeated database calls
def search_mechanics():
    try:
        name = request.args.get('name')
        if not name:
            return jsonify({"error": "Name query parameter is required"}), 400
        
        mechanics = Mechanic.query.filter(Mechanic.name.ilike(f"%{name}%")).all()
        return mechanics_schema.jsonify(mechanics), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to UPDATE an existing mechanic with validation error handling
@mechanics_bp.route('/<int:id>', methods=['PUT'])
@limiter.limit("10 per minute; 20 per hour; 100 per day")
def update_mechanic(id):
    try:
        mechanic = Mechanic.query.get_or_404(id)
        data = request.get_json()
        mechanic_schema = MechanicSchema()
        mechanic = mechanic_schema.load(data, instance=mechanic, session=db.session)
        db.session.commit()
        return mechanic_schema.jsonify(mechanic), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to DELETE a mechanic by id with validation error handling
@mechanics_bp.route('/<int:id>', methods=['DELETE'])
@limiter.limit("2 per day")
def delete_mechanic(id):
    try:
        mechanic = Mechanic.query.get_or_404(id)
        db.session.delete(mechanic)
        db.session.commit()
        return jsonify({"message": "Mechanic deleted successfully"}), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500