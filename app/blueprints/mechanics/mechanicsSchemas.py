from app.models import Mechanic, db
from app.extensions import ma
from marshmallow import fields, post_load, validate

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    password = fields.String(load_only=True, 
                            required=True,
                            validate=validate.Length(min=8, error="Password must be at least 8 characters long."))  # Accept password in requests but don't return it
    password_hash = fields.String(dump_only=True)  # Show the hash version of the password in responses

    class Meta:
        model = Mechanic
        sqla_session = db.session
        load_instance = True
        include_fk = True
        
    @post_load
    def hash_password(self, data, **kwargs):
        password = data.pop('password', None)
        if password:
            mech = Mechanic()
            mech.set_password(password)
            data['password_hash'] = mech.password_hash
            print("Data before load:", data) # Debugging line
        return data
    

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)