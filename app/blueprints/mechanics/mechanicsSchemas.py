from app.models import Mechanic
from app.extensions import ma

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        load_instance = True
        include_fk = True
    
mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)