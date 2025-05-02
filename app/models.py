from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

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
    password_hash = Column(String(255), nullable=False)
    
    # Relationship with the ServiceTicket class
    service_tickets = relationship('ServiceTicket', back_populates='customer', lazy=True)
    
    # Password Setter
    def set_password(self, password):
        """Hash the password and store it in the database."""
        self.password_hash = generate_password_hash(password)
    
    # Password Checker
    def check_password(self, password):
        """Check the hashed password against the provided password."""
        return check_password_hash(self.password_hash, password)
    
    # Virtual password property
    @property
    def password(self):
        """Prevent password from being accessed directly."""
        raise AttributeError('password is write-only')
    
    @password.setter
    def password(self, password_plaintext):
        """Set the password and hash it."""
        self.password_hash = generate_password_hash(password_plaintext)
        
# Mechanics class
# This class represents the mechanics table in the database
class Mechanic(db.Model):
    __tablename__ = 'mechanics'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    phone = Column(String(15), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    salary = Column(Integer, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    def set_password(self, password):
        """Hash the password and store it in the database."""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Check the hashed password against the provided password."""
        return check_password_hash(self.password_hash, password)

# Service_Tickets class
# This class represents the service_tickets table in the database
class ServiceTicket(db.Model):
    __tablename__ = 'service_tickets'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    vin = Column(String(17), nullable=False)
    service_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    service_desc = Column(String(200), nullable=False)
    
    # Relationship with the Customer class and Mechanic class
    customer = relationship('Customer', back_populates='service_tickets', lazy=True)
    mechanics = relationship('Mechanic', secondary='service_mechanics', backref='service_tickets', lazy=True)
    
# Service_Mechanics class
# This class represents the service_mechanics table in the database as a many-to-many relationship
class ServiceMechanic(db.Model):
    __tablename__ = 'service_mechanics'
    service_ticket_id = Column(Integer, ForeignKey('service_tickets.id'), primary_key=True)
    mechanic_id = Column(Integer, ForeignKey('mechanics.id'), primary_key=True)