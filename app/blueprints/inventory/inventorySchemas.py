from app.models import Inventory
from app.extensions import ma
from marshmallow import fields, validate

class InventorySchema(ma.SQLAlchemyAutoSchema):
    name = fields.String(
        required=True,
        validate=validate.Length(min=1, error="Name cannot be empty.")
    )
    price = fields.Float(
        required=True,
        validate=validate.Range(min=0.01, error="Price must be greater than zero.")
    )
    
    class Meta:
        model = Inventory
        load_instance = True
        include_fk = True
        
    
inventory_schema = InventorySchema()
inventorys_schema = InventorySchema(many=True)