from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship, DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Creating the database tables
# Admin model
class Admin(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(128), nullable=False)
    
    def set_password(self, password):
        """Hash the password and store it in the database."""
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        """Check the hashed password against the provided password."""
        return check_password_hash(self.password_hash, password)

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
    
    # Relationship with the ServiceTicket class
    service_tickets = relationship('ServiceTicket', secondary='service_mechanics', back_populates='mechanics', lazy=True)
    
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
    mechanics = relationship('Mechanic', secondary='service_mechanics', back_populates='service_tickets', lazy=True)
    
    # Relationship with the Product class as many-to-many where one service ticket can have many products and one product can belong to many service tickets
    products = relationship(
        'Product',
        secondary='inventory_service_tickets',
        back_populates='service_tickets',
        lazy=True,
        primaryjoin='ProductServiceTicket.service_ticket_id==ServiceTicket.id',
        secondaryjoin='ProductServiceTicket.product_id==Product.id',
        overlaps='product_links'
    )
    product_links = relationship(
        'ProductServiceTicket',
        back_populates='service_ticket',
        lazy=True
        )
    
# Service_Mechanics class
# This class represents the service_mechanics table in the database as a many-to-many relationship
class ServiceMechanic(db.Model):
    __tablename__ = 'service_mechanics'
    service_ticket_id = Column(Integer, ForeignKey('service_tickets.id'), primary_key=True)
    mechanic_id = Column(Integer, ForeignKey('mechanics.id'), primary_key=True)
    

# Product class
# This class represents the inventory table in the database
class Product(db.Model):
    __tablename__ = 'inventory'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    
    # Relationship with the ServiceTicket class as many-to-many where one service ticket can have many inventory items and one inventory item can belong to many service tickets
    service_tickets = relationship('ServiceTicket',
                                secondary='inventory_service_tickets',
                                back_populates='products', 
                                lazy=True,
                                overlaps='product_links')
    product_links = relationship('ProductServiceTicket', back_populates='product', lazy=True)
    
# ProductServiceTicket class junction table between Product and ServiceTicket
# This class represents the Product_service_tickets table in the database as a many-to-many relationship
class ProductServiceTicket(db.Model):
    __tablename__ = 'inventory_service_tickets'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('inventory.id'), nullable=False)
    service_ticket_id = Column(Integer, ForeignKey('service_tickets.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)  # Quantity of the inventory item used in the service ticket

    # Relationship with the Product class and ServiceTicket class
    product = relationship(
        'Product', 
        back_populates='product_links', 
        lazy=True, 
        overlaps='service_tickets')
    
    service_ticket = relationship(
        'ServiceTicket', 
        back_populates='product_links', 
        lazy=True,
        overlaps='products')
