from app.blueprints.mechanics import mechanics_bp
from app.blueprints.mechanics.mechanicsSchemas import MechanicSchema, mechanics_schema
from app.models import db, Mechanic
from flask import jsonify, request
from marshmallow import ValidationError


# Mechanics Endpoints
# Endpoint to create a new mechanic with validation error handling
@mechanics_bp.route('/mechanics', methods=['POST'])
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

# Endpoint to get all mechanics with validation error handling
@mechanics_bp.route('/mechanics', methods=['GET'])
def get_mechanics():
    try:
        mechanics = Mechanic.query.all()
        return mechanics_schema.jsonify(mechanics), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to get a specific mechanic by ID with validation error handling
@mechanics_bp.route('/mechanics/<int:id>', methods=['GET'])
def get_mechanic(id):
    try:
        mechanic = Mechanic.query.get_or_404(id)
        return mechanics_schema.jsonify(mechanic), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to update an existing mechanic with validation error handling
@mechanics_bp.route('/mechanics/<int:id>', methods=['PUT'])
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

# Endpoint to delete a mechanic with validation error handling
@mechanics_bp.route('/mechanics/<int:id>', methods=['DELETE'])
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