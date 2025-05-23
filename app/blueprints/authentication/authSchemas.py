from marshmallow import Schema, fields
from app.models import Admin, db
from app.extensions import ma

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

    class Meta:
            model = Admin
            sqla_session = db.session
            load_instance = True
            include_fk = True