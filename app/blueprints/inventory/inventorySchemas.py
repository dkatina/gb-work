from app.models import Inventory
from app.extensions import ma

class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        load_instance = True
        include_fk = True
    
inventory_schema = InventorySchema()
inventorys_schema = InventorySchema(many=True)