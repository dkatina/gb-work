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
    vin = Column(String(17), nullable=False, unique=True)
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
    
# RESTful API Schema
# Customers Endpoints
# Endpoint to get all customers
@app.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return jsonify([{'id': customer.id, 'name': customer.name, 'phone': customer.phone, 'email': customer.email} for customer in customers])

# Endpoint to get a specific customer by ID
@app.route('/customers/<int:id>', methods=['GET'])
def get_customer(id):
    customer = Customer.query.get_or_404(id)
    return jsonify({'id': customer.id, 'name': customer.name, 'phone': customer.phone, 'email': customer.email})

# Endpoint to create a new customer
@app.route('/customers', methods=['POST'])
def create_customer():
    data = request.get_json()
    new_customer = Customer(name=data['name'], phone=data['phone'], email=data['email'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({'id': new_customer.id, 'name': new_customer.name, 'phone': new_customer.phone, 'email': new_customer.email}), 201

# Endpoint to update an existing customer
@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    data = request.get_json()
    customer.name = data['name']
    customer.phone = data['phone']
    customer.email = data['email']
    db.session.commit()
    return jsonify({'id': customer.id, 'name': customer.name, 'phone': customer.phone, 'email': customer.email})

# Endpoint to delete a customer
@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Customer deleted successfully'}), 204

# Service Tickets Endpoints
# Endpoint to get all service tickets
@app.route('/service_tickets', methods=['GET'])
def get_service_tickets():
    service_tickets = ServiceTicket.query.all()
    return jsonify([{'id': ticket.id, 'customer_id': ticket.customer_id, 'vin': ticket.vin, 'service_date': ticket.service_date, 'service_desc': ticket.service_desc} for ticket in service_tickets])

# Endpoint to get a specific service ticket by ID
@app.route('/service_tickets/<int:id>', methods=['GET'])
def get_service_ticket(id):
    service_ticket = ServiceTicket.query.get_or_404(id)
    return jsonify({'id': service_ticket.id, 'customer_id': service_ticket.customer_id, 'vin': service_ticket.vin, 'service_date': service_ticket.service_date, 'service_desc': service_ticket.service_desc})

# Endpoint to create a new service ticket
@app.route('/service_tickets', methods=['POST'])
def create_service_ticket():
    data = request.get_json()
    new_service_ticket = ServiceTicket(customer_id=data['customer_id'], vin=data['vin'], service_date=data['service_date'], service_desc=data['service_desc'])
    db.session.add(new_service_ticket)
    db.session.commit()
    return jsonify({'id': new_service_ticket.id, 'customer_id': new_service_ticket.customer_id, 'vin': new_service_ticket.vin, 'service_date': new_service_ticket.service_date, 'service_desc': new_service_ticket.service_desc}), 201

# Endpoint to update an existing service ticket
@app.route('/service_tickets/<int:id>', methods=['PUT'])
def update_service_ticket(id):
    service_ticket = ServiceTicket.query.get_or_404(id)
    data = request.get_json()
    service_ticket.customer_id = data['customer_id']
    service_ticket.vin = data['vin']
    service_ticket.service_date = data['service_date']
    service_ticket.service_desc = data['service_desc']
    db.session.commit()
    return jsonify({'id': service_ticket.id, 'customer_id': service_ticket.customer_id, 'vin': service_ticket.vin, 'service_date': service_ticket.service_date, 'service_desc': service_ticket.service_desc})

# Endpoint to delete a service ticket
@app.route('/service_tickets/<int:id>', methods=['DELETE'])
def delete_service_ticket(id):
    service_ticket = ServiceTicket.query.get_or_404(id)
    db.session.delete(service_ticket)
    db.session.commit()
    return jsonify({'message': 'Service ticket deleted successfully'}), 204

# Mechanics Endpoints
# Endpoint to get all mechanics
@app.route('/mechanics', methods=['GET'])
def get_mechanics():
    mechanics = Mechanic.query.all()
    return jsonify([{'id': mechanic.id, 'name': mechanic.name, 'phone': mechanic.phone, 'email': mechanic.email, 'salary': mechanic.salary} for mechanic in mechanics])

# Endpoint to get a specific mechanic by ID
@app.route('/mechanics/<int:id>', methods=['GET'])
def get_mechanic(id):
    mechanic = Mechanic.query.get_or_404(id)
    return jsonify({'id': mechanic.id, 'name': mechanic.name, 'phone': mechanic.phone, 'email': mechanic.email, 'salary': mechanic.salary})

# Endpoint to create a new mechanic
@app.route('/mechanics', methods=['POST'])
def create_mechanic():
    data = request.get_json()
    new_mechanic = Mechanic(name=data['name'], phone=data['phone'], email=data['email'], salary=data['salary'])
    db.session.add(new_mechanic)
    db.session.commit()
    return jsonify({'id': new_mechanic.id, 'name': new_mechanic.name, 'phone': new_mechanic.phone, 'email': new_mechanic.email, 'salary': new_mechanic.salary}), 201

# Endpoint to update an existing mechanic
@app.route('/mechanics/<int:id>', methods=['PUT'])
def update_mechanic(id):
    mechanic = Mechanic.query.get_or_404(id)
    data = request.get_json()
    mechanic.name = data['name']
    mechanic.phone = data['phone']
    mechanic.email = data['email']
    mechanic.salary = data['salary']
    db.session.commit()
    return jsonify({'id': mechanic.id, 'name': mechanic.name, 'phone': mechanic.phone, 'email': mechanic.email, 'salary': mechanic.salary})

# Endpoint to delete a mechanic
@app.route('/mechanics/<int:id>', methods=['DELETE'])
def delete_mechanic(id):
    mechanic = Mechanic.query.get_or_404(id)
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({'message': 'Mechanic deleted successfully'}), 204


    
with app.app_context():
    db.create_all()
    
app.run(debug=True)   