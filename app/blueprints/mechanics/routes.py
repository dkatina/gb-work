from app.blueprints.mechanics import mechanics_bp
from app.blueprints.mechanics.mechanicsSchemas import MechanicSchema, mechanics_schema, mechanic_schema
from app.models import ServiceTicket, db, Mechanic, Admin
from flask import jsonify, request
from marshmallow import ValidationError
from app.extensions import limiter, cache
from werkzeug.exceptions import NotFound
from app.utils.util import encode_token, not_found, token_required

# ---------------- Mechanics Endpoints --------------------
# Endpoint to create a new mechanic with validation error handling
@mechanics_bp.route('/', methods=['POST'], strict_slashes=False)
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
@mechanics_bp.route('/', methods=['GET'], strict_slashes=False)
#@cache.cached(timeout=60)  # Cache the response for 60 seconds to avoid repeated database calls
def get_mechanics():
    try:
        page_str = request.args.get('page', '1')
        per_page_str = request.args.get('per_page', '10')
        
        try:
            page = int(page_str)
            per_page = int(per_page_str)
        except ValueError:
            return jsonify({"current_page": page_str,
                "mechanics": [],
                "has_next": False,
                "has_prev": False,
                "page": page_str,
                "per_page": per_page_str,
                "total": 0,
                "total_pages": 0,
                "error": "Page not found or exceeds total pages"
            }), 200
            
        # Using .order_by() to ensure consisten pagination
        base_query = Mechanic.query.order_by(Mechanic.id)
        # Getting total number of mechanics
        total = base_query.count()
        # Calculating total pages
        total_pages = (total + per_page - 1) // per_page
        
        print(f"[DEBUG] total: {total}, total_pages: {total_pages}, requested page: {page}") # Debugging line
        
        # Checking if the requested page exceeds the total pages
        if total == 0 or page > total_pages or page < 1:
            return jsonify({
                            "current_page": page,
                            "mechanics": [],
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
        mechanics = pagination.items
        
        print(f"Requested page: {page}, total pages: {pagination.pages}") # Debugging line

        return jsonify({
            "current_page": pagination.page,
            "mechanics": [MechanicSchema().dump(mechanic) for mechanic in mechanics],
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "total_pages": pagination.pages
        }), 200  
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Endpoint to GET a SPECIFIC mechanic by ID with validation error handling
@mechanics_bp.route('/<int:id>', methods=['GET'])
#@cache.cached(timeout=60)  # Cache the response for 60 seconds to avoid repeated database calls
def get_mechanic(id):
    try:
        mechanic = Mechanic.query.get_or_404(id)
        return MechanicSchema().jsonify(mechanic), 200
    except NotFound:
        return jsonify({"error": "Mechanic not found."}), 404
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Endpoint to GET a list of mechanics in the order of who has worked on the most tickets with validation error handling
@mechanics_bp.route('/most-worked', methods=['GET'], strict_slashes=False)
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
@mechanics_bp.route('/search', methods=['GET'], strict_slashes=False)
@cache.cached(timeout=60)  # Cache the response for 60 seconds to avoid repeated database calls
def search_mechanics():
    try:
        name = request.args.get('name')
        if not name:
            return jsonify({"error": "Name query parameter is required"}), 400
        
        mechanics = Mechanic.query.filter(Mechanic.name.ilike(f"%{name}%")).all()
        return jsonify(mechanics_schema.dump(mechanics)), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        print(f"Search Mechanics Exception: {e}") # Debugging line
        return jsonify({"error": str(e)}), 500

# Endpoint to UPDATE an existing mechanic with validation error handling
@mechanics_bp.route('/<int:mechanic_id>', methods=['PUT'], strict_slashes=False)
#@limiter.limit("10 per minute; 20 per hour; 100 per day")
@token_required
def update_mechanic(user, mechanic_id):
    try:
        mechanic = Mechanic.query.get_or_404(mechanic_id)
        
        # Check if the mechanic_id in the token matches the mechanic_id in the URL
        if getattr(user, 'user_type', None) != 'admin' and user.id != mechanic_id:
            return jsonify({"error": "Unauthorized access"}), 403
        
        data = request.get_json()
        data.pop("email", None)  # Remove email from data if present
        mechanic_schema = MechanicSchema()
        mechanic = mechanic_schema.load(data, instance=mechanic, session=db.session)
        db.session.commit()
        return mechanic_schema.jsonify(mechanic), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        print("Update Mechanic Exception:", e) # Debugging line
        return jsonify({"error": str(e)}), 500
    
# Endpoint to DELETE a mechanic by id with validation error handling
@mechanics_bp.route('/<int:mechanic_id>', methods=['DELETE'], strict_slashes=False)
#@limiter.limit("2 per day")
@token_required
def delete_mechanic(user, mechanic_id):
    protected_emails = ["jane.mechanic@example.com"]
    try:
        mechanic = Mechanic.query.get(mechanic_id)
        if not mechanic:
            return jsonify({"error": "Mechanic not found."}), 404
        if mechanic.email in protected_emails:
            return jsonify({"error": "This test account cannot be deleted."}), 403
        db.session.delete(mechanic)
        db.session.commit()
        return jsonify({"message": f"Mechanic {mechanic_id} deleted successfully"}), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500