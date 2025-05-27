from marshmallow import Schema, fields
from app.models import Admin, db
from app.extensions import ma

class LoginSchema(ma.Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

    class Meta:
            model = Admin
            load_instance = True
            include_fk = True