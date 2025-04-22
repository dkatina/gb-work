from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, backref, DeclarativeBase
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Creating Flask app and configuring database
app = Flask(__name__)

# Using environment variables for the database URI connection
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
print(f"DB_USER: {DB_USER}, DB_PASSWORD: {DB_PASSWORD}")
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@localhost/mechanicshop_db'

db.init_app(app)

# Creating the database tables
# Customer class
# This class represents the customers table in the database
class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    phone = Column(String(15), nullable=False)
    email = Column(String(50), nullable=False, unique=True)

    # Relationship with the Vehicle class
    vehicles = relationship('Vehicle', backref='customer', lazy=True)
    
# Service_Tickets class
# This class represents the service_tickets table in the database
class ServiceTicket(Base):
    __tablename__ = 'service_tickets'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    vin = Column(Integer, ForeignKey('VIN'), nullable=False)
    service_date = Column(DateTime, nullable=False)
    service_desc = Column(String(200), nullable=False)
    
    # Relationship with the Customer class
    customer = relationship('Customer', backref='service_tickets', lazy=True)
    
# Mechanics class
# This class represents the mechanics table in the database
class Mechanic(Base):
    __tablename__ = 'mechanics'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    phone = Column(String(15), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    salary = Column(Integer, nullable=False)
    
    # Relationship with the ServiceTicket class
    service_tickets = relationship('ServiceTicket', backref='mechanic', lazy=True)
    
# Service_Mechanics class
# This class represents the service_mechanics table in the database as a many-to-many relationship
class ServiceMechanic(Base):
    __tablename__ = 'service_mechanics'
    service_ticket_id = Column(Integer, ForeignKey('service_tickets.id'), primary_key=True)
    mechanic_id = Column(Integer, ForeignKey('mechanics.id'), primary_key=True)
    
    # Relationship with the ServiceTicket and Mechanic classes
    service_ticket = relationship('ServiceTicket', backref=backref('service_mechanics', lazy='dynamic'))
    mechanic = relationship('Mechanic', backref=backref('service_mechanics', lazy='dynamic'))
    
with app.app_context():
    db.create_all()
    
app.run(debug=True)   