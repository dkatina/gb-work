from flask import Flask
from app.models import db
from app.extensions import ma, limiter, cache
from app.blueprints.customers import customers_bp
from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.mechanics import mechanics_bp
from app.config import DevelopmentConfig, TestingConfig, ProductionConfig

def create_app(config_class):
    
    app = Flask(__name__)
    
    # Config setup
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    
    # Register blueprints
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(service_tickets_bp, url_prefix='/service_tickets')
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
    

    return app

