from app.models import Customer, db
from app.extensions import ma
from marshmallow import fields, post_load, validate

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    password = fields.String(load_only=True, 
                        required=True,
                        validate=validate.Length(min=8, error="Password must be at least 8 characters long."))  # Accept password in requests but don't return it
    password_hash = fields.String(dump_only=True)  # Show the hash version of the password in responses
    phone = fields.String(required=True, validate=validate.Length(min=10, max=15, error="Phone number must be between 10 and 15 characters long."))  # Validate phone number length
    
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
            print("Data before load:", data) # Debugging line
        return data
    
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)