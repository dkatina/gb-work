from app.models import Customer
from app.extensions import ma

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = True
        include_fk = True
    
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)