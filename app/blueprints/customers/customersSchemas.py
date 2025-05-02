from app.models import Customer
from app.extensions import ma
from marshmallow import fields, post_load

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    password = fields.String(load_only=True)  # Accept password in requests but don't return it
    password_hash = fields.String(dump_only=True)  # Show the hash version of the password in responses
    
    class Meta:
        model = Customer
        load_instance = True
        include_fk = True
    
    @post_load
    def hash_password(self, data, **kwargs):
        password = data.pop('password', None)
        if password:
            customer = Customer()
            customer.set_password(password)
            data['password_hash'] = customer.password_hash
        return data
    
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)