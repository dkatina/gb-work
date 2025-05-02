from app.blueprints.inventory import inventory_bp
from app.blueprints.inventory.inventorySchemas import InventorySchema, inventorys_schema, inventory_schema
from app.models import ServiceTicket, db, Inventory
from flask import jsonify, request
from marshmallow import ValidationError
from app.extensions import limiter, cache

# ---------------- inventory Endpoints --------------------
# Endpoint to create a new inventory item with validation error handling
@inventory_bp.route('/', methods=['POST'])
@limiter.limit("10 per minute; 20 per hour; 100 per day")
def create_inventory():
    try:
        data = request.get_json()
        inventory_items = inventory_schema.load(data, session=db.session)
        db.session.add(inventory_items)
        db.session.commit()
        return inventory_schema.jsonify(inventory_items), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to GET ALL inventory items with validation error handling
@inventory_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)  # Cache the response for 60 seconds to avoid repeated database calls
def get_all_inventory():
    try:
        inventory_items = Inventory.query.all()
        return inventorys_schema.jsonify(inventory_items), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to GET a SPECIFIC inventory item by ID with validation error handling
@inventory_bp.route('/<int:id>', methods=['GET'])
@cache.cached(timeout=60)  # Cache the response for 60 seconds to avoid repeated database calls
def get_inventory(id):
    try:
        inventory_items = Inventory.query.get_or_404(id)
        return inventory_schema.jsonify(inventory_items), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Endpoint to do a search for an inventory item by name using GET with query parameters and validation error handling
@inventory_bp.route('/search', methods=['GET'])
@cache.cached(timeout=60)  # Cache the response for 60 seconds to avoid repeated database calls
def search_inventory():
    try:
        name = request.args.get('name')
        if not name:
            return jsonify({"error": "Name query parameter is required"}), 400
        
        inventory_items = Inventory.query.filter(Inventory.name.ilike(f"%{name}%")).all()
        return inventorys_schema.jsonify(inventory_items), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to UPDATE an existing inventory item with validation error handling
@inventory_bp.route('/<int:id>', methods=['PUT'])
@limiter.limit("10 per minute; 20 per hour; 100 per day")
def update_inventory(id):
    try:
        inventory_items = Inventory.query.get_or_404(id)
        data = request.get_json()
        inventory_items = inventory_schema.load(data, instance=inventory_items, session=db.session)
        db.session.commit()
        return inventory_schema.jsonify(inventory_items), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to DELETE an inventory item by id with validation error handling
@inventory_bp.route('/<int:id>', methods=['DELETE'])
@limiter.limit("2 per day")
def delete_inventory(id):
    try:
        inventory_items = Inventory.query.get_or_404(id)
        db.session.delete(inventory_items)
        db.session.commit()
        return jsonify({"message": "inventory deleted successfully"}), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500