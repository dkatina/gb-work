from app.blueprints.inventory import inventory_bp
from app.blueprints.inventory.inventorySchemas import InventorySchema, inventorys_schema, inventory_schema
from app.models import ServiceTicket, db, Inventory
from flask import jsonify, request
from marshmallow import ValidationError
from app.extensions import limiter, cache

# ---------------- inventory Endpoints --------------------
# Endpoint to create a new inventory product with validation error handling
@inventory_bp.route('/', methods=['POST'])
@limiter.limit("10 per minute; 20 per hour; 100 per day")
def create_inventory():
    try:
        data = request.get_json()
        product = inventory_schema.load(data, session=db.session)
        db.session.add(product)
        db.session.commit()
        return inventory_schema.jsonify(product), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to GET ALL inventory products with validation error handling
@inventory_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)  # Cache the response for 60 seconds to avoid repeated database calls
def get_all_inventory():
    try:
        products = Inventory.query.all()
        return inventorys_schema.jsonify(products), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to GET a SPECIFIC inventory product by ID with validation error handling
@inventory_bp.route('/<int:id>', methods=['GET'])
@cache.cached(timeout=60)  # Cache the response for 60 seconds to avoid repeated database calls
def get_inventory(id):
    try:
        product = Inventory.query.get_or_404(id)
        return inventory_schema.jsonify(product), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to UPDATE an existing inventory product with validation error handling
@inventory_bp.route('/<int:id>', methods=['PUT'], strict_slashes=False)
#@limiter.limit("10 per minute; 20 per hour; 100 per day")
def update_inventory(id):
    try:
        print(f"Updating inventory product with ID: {id}")
        # Fetching the inventory product by ID or raising a 404 error if not found
        inventory_product = Inventory.query.get_or_404(id)
        print(f"Found inventory product: {inventory_product}")
        # Getting data from the request body
        data = request.get_json()
        print(f"Data to update: {data}")
        # Loading the data into the schema for validation and updating
        updated_inventory_product = inventory_schema.load(data, instance=inventory_product, session=db.session)
        print(f"Updated inventory product: {updated_inventory_product}")
        # Committing the changes to the database
        db.session.commit()
        # Returning the updated inventory product as a JSON response
        return inventory_schema.jsonify(updated_inventory_product), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to DELETE an inventory product by id with validation error handling
@inventory_bp.route('/<int:id>', methods=['DELETE'], strict_slashes=False)
@limiter.limit("2 per day")
def delete_inventory(id):
    try:
        inventory_product = Inventory.query.get_or_404(id)
        db.session.delete(inventory_product)
        db.session.commit()
        return jsonify({"message": "Inventory product deleted successfully"}), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500