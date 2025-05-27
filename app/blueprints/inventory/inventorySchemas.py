from app.models import Product, ProductServiceTicket, db
from app.extensions import ma
from marshmallow import fields, validate

class ProductSchema(ma.SQLAlchemyAutoSchema):
    name = fields.String(
        required=True,
        validate=validate.Length(min=1, error="Name cannot be empty.")
    )
    price = fields.Float(
        required=True,
        validate=validate.Range(min=0.01, error="Price must be greater than zero.")
    )
    
    class Meta:
        model = Product
        load_instance = True
        include_fk = True
        
class ProductServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    product = fields.Nested(ProductSchema)
    quantity = fields.Int()
    
    class Meta:
        model = ProductServiceTicket
        sqla_session = db.session
        load_instance = True
        include_fk = True


product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
product_service_ticket_schema = ProductServiceTicketSchema()