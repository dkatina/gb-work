from app.models import Mechanic, ServiceTicket
from app.extensions import ma
from marshmallow import ValidationError, post_load, fields
from app.blueprints.inventory.inventorySchemas import InventorySchema


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    mechanic_ids = ma.Method("get_mechanic_ids", deserialize="load_mechanic_ids")
    mechanics = fields.Nested('MechanicSchema', many=True)
    customer = fields.Nested('CustomerSchema')
    inventory_items = fields.Nested(InventorySchema, many=True)
    
    class Meta:
        model = ServiceTicket
        load_instance = True
        include_fk = True
        fields = ('mechanic_ids', 'customer_id', 'service_date', 'vin', 'service_desc', 'inventory_items')
        
    def get_mechanic_ids(self, obj):
        return [mechanic.id for mechanic in obj.mechanics]
    
    def load_mechanic_ids(self, value):
        if isinstance(value, list):
            mechanics = [Mechanic.query.get(id) for id in value]
            if None in mechanics:
                raise ValidationError("One or more mechanic IDs are invalid.")
            return mechanics
        else:
            raise ValidationError("Invalid mechanic IDs format. Expected a list of integers.")

    @post_load
    def assign_mechanics(self, data, **kwargs):
        mechanics = data.pop('mechanic_ids', [])
        data['mechanics'] = mechanics
        return data
        
class UpdateServiceTicketSchema(ma.Schema):
    add_mechanic_ids = fields.List(fields.Int(), required=True)
    remove_mechanic_ids = fields.List(fields.Int(), required=True)
    class Meta:
        fields = ('add_mechanic_ids', 'remove_mechanic_ids')
    
    
# Instances for serialization    
service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
update_service_ticket_schema = UpdateServiceTicketSchema()


'''



'''