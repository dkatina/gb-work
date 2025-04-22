from app.models import ServiceTicket
from app.extensions import ma

class ServiceTicketsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket
        load_instance = True
        include_fk = True
    
ServiceTicketsSchema = ServiceTicketsSchema()
service_tickets_schema = ServiceTicketsSchema()