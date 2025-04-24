from app.models import Mechanic, ServiceTicket
from app.extensions import ma
from marshmallow import ValidationError


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    mechanic_ids = ma.Method("get_mechanic_ids", deserialize="load_mechanic_ids")
    
    class Meta:
        model = ServiceTicket
        load_instance = True
        include_fk = True
        fields = ('mechanic_ids', 'customer_id', 'service_date', 'vin', 'service_desc')
        
    def get_mechanic_ids(self, obj):
        return [mechanic.id for mechanic in obj.mechanics]
    
    def load_mechanic_ids(self, value, obj, **kwargs):
        if isinstance(value, list):
            obj.mechanics = [Mechanic.query.get(id) for id in value]
        else:
            raise ValidationError("Invalid mechanic IDs format. Expected a list of integers.")

# Instances for serialization    
service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)