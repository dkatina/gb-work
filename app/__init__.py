from flask import Flask, jsonify, request
from app.models import db, Customer, ServiceTicket, Vehicle, Mechanic, Service
from app.extensions import ma
from app.blueprints.customers import customers_bp
from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.mechanics import mechanics_bp

def create_app(config_name):
    
    app = Flask(__name__)
    
    # Config setup
    app.config.from_object(config_name)
    
    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    
    # Register blueprints
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(service_tickets_bp, url_prefix='/service_tickets')
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
    

    return app

