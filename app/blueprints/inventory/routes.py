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
        print("Internal Server Error:", e)
        return jsonify({"error": str(e)}), 500

# Endpoint to GET ALL inventory products with validation error handling
@inventory_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)  # Cache the response for 60 seconds to avoid repeated database calls
def get_all_inventory():
    try:
        page_str = request.args.get('page', '1')
        per_page_str = request.args.get('per_page', '10')
        
        try:
            page = int(page_str)
            per_page = int(per_page_str)
        except ValueError:
            return jsonify({"current_page": page_str,
                "products": [],
                "has_next": False,
                "has_prev": False,
                "page": page_str,
                "per_page": per_page_str,
                "total": 0,
                "total_pages": 0,
                "error": "Page not found or exceeds total pages"
            }), 200
            
        # Using .order_by() to ensure consisten pagination
        base_query = Inventory.query.order_by(Inventory.id)
        # Getting total number of inventory products
        total = base_query.count()
        # Calculating total pages
        total_pages = (total + per_page - 1) // per_page
        
        print(f"[DEBUG] total: {total}, total_pages: {total_pages}, requested page: {page}") # Debugging line
        
        # Checking if the requested page exceeds the total pages
        if total == 0 or page > total_pages or page < 1:
            return jsonify({
                            "current_page": page,
                            "products": [],
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
        products = pagination.items
        
        print(f"Requested page: {page}, total pages: {pagination.pages}") # Debugging line

        return jsonify({
            "current_page": pagination.page,
            "products": inventorys_schema.dump(products),
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "total_pages": pagination.pages
        }), 200  
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