from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref, DeclarativeBase
from flask_sqlalchemy import SQLAlchemy

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Creating the database tables
# Customer class
# This class represents the customers table in the database
class Customer(db.Model):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    phone = Column(String(15), nullable=False)
    email = Column(String(50), nullable=False, unique=True)

    # Relationship with the ServiceTicket class
    service_tickets = relationship('ServiceTicket', back_populates='customer', lazy=True)
    
# Service_Tickets class
# This class represents the service_tickets table in the database
class ServiceTicket(db.Model):
    __tablename__ = 'service_tickets'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    vin = Column(String(17), nullable=False, unique=True)
    service_date = Column(DateTime, nullable=False)
    service_desc = Column(String(200), nullable=False)
    
    # Relationship with the Customer class and Mechanic class
    customer = relationship('Customer', back_populates='service_tickets', lazy=True)
    mechanics = relationship('Mechanic', secondary='service_mechanics', backref='service_tickets', lazy=True)
    
# Mechanics class
# This class represents the mechanics table in the database
class Mechanic(db.Model):
    __tablename__ = 'mechanics'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    phone = Column(String(15), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    salary = Column(Integer, nullable=False)
    
# Service_Mechanics class
# This class represents the service_mechanics table in the database as a many-to-many relationship
class ServiceMechanic(db.Model):
    __tablename__ = 'service_mechanics'
    service_ticket_id = Column(Integer, ForeignKey('service_tickets.id'), primary_key=True)
    mechanic_id = Column(Integer, ForeignKey('mechanics.id'), primary_key=True)