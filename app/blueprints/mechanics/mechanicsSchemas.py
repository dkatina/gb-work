from app.models import Mechanic
from app.extensions import ma
from marshmallow import fields, post_load

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    password = fields.String(load_only=True)  # Accept password in requests but don't return it
    password_hash = fields.String(dump_only=True)  # Show the hash version of the password in responses
    
    class Meta:
        model = Mechanic
        load_instance = True
        include_fk = True
        
    @post_load
    def make_mechanic(self, data, **kwargs):
        password = data.pop('password', None)
        mechanic = Mechanic(**data)
        if password:
            mechanic.set_password(password)
        return mechanic
    
mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)