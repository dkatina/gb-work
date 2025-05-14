from flask import jsonify, request
from app import create_app
from app.models import db, Customer
import unittest
from app.config import TestingConfig

# python -m unittest discover tests -v
# Customer Routes: Create Customer, Get All Customers, Get Customer by ID, Update Existing Customer, Delete Customer

class TestCustomer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(TestingConfig)
        cls.app.config['PROPAGATE_EXCEPTIONS'] = True
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        cls.app.config['TESTING'] = True
        cls.app.config['DEBUG'] = True
        
        cls.client = cls.app.test_client()

        db.create_all()
    
    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()
        
    def setUp(self):
        self.connection = db.engine.connect()
        self.transaction = self.connection.begin()
        db.session.bind = self.connection
        db.session.begin_nested()
        # Setting up test login credentials
        login_response = self.client.post('/auth/login', json={
            "email": "test@email.com",
            "password": "password123"
        })
        token = login_response.json.get('auth_token')
        self.auth_headers = {
            'Authorization': f'Bearer {token}'
        }
        # Creating a test customer
        TestCustomer = {
            "id": 77,
            "name": "Test Customer",
            "phone": "666-666-6666",
            "email": "TestCustomer@email.com",
            "password": "password123"
        }
        TestCustomer = Customer(**TestCustomer)
        db.session.add(TestCustomer)
        
        
    def tearDown(self):
        db.session.rollback()
        self.transaction.rollback()
        self.connection.close()
        db.session.remove()
    
    # -------------------Create Customer Test-------------------
    def test_create_customer(self):
        customer_payload = {
            "name": "John Doe",
            "phone": "555-555-5555",
            "email": "johndoe@email.com",
            "password": "password123"
        }
        
        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], 'John Doe')
        print("Response JSON:", response.json)  # Debugging line
        print("Response Status Code:", response.status_code)  # Debugging line
        print("Response Data:", response.get_data(as_text=True))  # Debugging line
    
    
    # -------------------Invalid Customer Creation Test-------------------   
    def test_invalid_creation(self):
        customer_payload = {
            "name": "John Doe",
            "phone": "555-555-5555",
            "email": "johndoe@email.com"
        }
        
        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 400, f"Expected 400 for invalid customer creation, got {response.status_code} with body: {response.get_json()}")
        self.assertEqual(response.json['password'], ['Missing data for required field.'])
        print("Response JSON:", response.json)  # Debugging line
        print("Response Status Code:", response.status_code)  # Debugging line
        print("Response Data:", response.get_data(as_text=True)) # Debugging line
    
    ''' 
    # -------------------Get All Customers Test-------------------
    def test_get_all_customers(self):
        customer_payload = {
            }
        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json['customers'], list)
        print("Response JSON:", response.json)  # Debugging line
        print("Response Status Code:", response.status_code)  # Debugging line
        print("Response Data:", response.get_data(as_text=True)) # Debugging line
        
    # -------------------Invalid Get All Customers Test-------------------
    def test_invalid_get_all_customers(self):
        try:
            page = int(request.args.get('page', 1))
        except ValueError:
            return jsonify({"error": "Invalid page number"}), 400
        response = self.client.get('/customers/?page=9999')
        self.assertEqual(response.status_code, 404, f"Expected 404 for invalid page number, got {response.status_code} with body: {response.get_json()}")
        self.assertEqual(response.json['error'], 'Page not found')
        print("Response JSON:", response.json)  # Debugging line
        print("Response Status Code:", response.status_code)  # Debugging line
        print("Response Data:", response.get_data(as_text=True)) # Debugging line
        
    # -------------------Get Customer by ID Test-------------------
    def test_get_customer_by_id(self):
        
        # Retrieving the customer
        response = self.client.get('/customers/77/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['id'], 77)
        print("Response JSON:", response.json)  # Debugging line
        print("Response Status Code:", response.status_code)  # Debugging line
        print("Response Data:", response.get_data(as_text=True)) # Debugging line
        
    # -------------------Invalid Get Customer by ID Test-------------------
    def test_invalid_get_customer_by_id(self):
        customer_payload = {
            1
            }
        response = self.client.get('/customers/9999/')
        self.assertEqual(response.status_code, 404, f"Expected 404 for invalid customer ID, got {response.status_code} with body: {response.get_json()}")
        self.assertEqual(response.json['error'], 'Customer not found')
        print("Response JSON:", response.json)  # Debugging line
        print("Response Status Code:", response.status_code)  # Debugging line
        print("Response Data:", response.get_data(as_text=True)) # Debugging line
        
    # -------------------Update Customer Test-------------------
    def test_update_customer(self):
        customer_payload = {
            "name": "Test Update",
            "phone": "155-555-5555",
            "email": "testupdate@email.com",
            "password": "password123"
        }
        response = self.client.put('/customers/77/', json=customer_payload, headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json)
        print("Response JSON:", response.json)  # Debugging line
        print("Response Status Code:", response.status_code)  # Debugging line
        print("Response Data:", response.get_data(as_text=True)) # Debugging line
        
    # -------------------Invalid Update Customer Test-------------------
    def test_invalid_update_customer(self):
        customer_payload = {
            "name": "John Doe",
            "phone": "55-555-5555",
            "email": "johndoe@email.com",
            "password": "password123"
        }
        response = self.client.put('/customers/1/', json=customer_payload)
        self.assertEqual(response.status_code, 400, f"Expected 400 for invalid customer update, got {response.status_code} with body: {response.get_json()}")
        self.assertEqual(response.json['phone'], ['Shorter than minimum length 10.'])
        print("Response JSON:", response.json)  # Debugging line
        print("Response Status Code:", response.status_code)  # Debugging line
        print("Response Data:", response.get_data(as_text=True)) # Debugging line
        
    # -------------------Delete Customer Test-------------------
    def test_delete_customer(self):
        
        response = self.client.delete('/customers/77/', headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 404, f"Expected 404 for invalid customer ID, got {response.status_code} with body: {response.get_json()}")
        self.assertEqual(response.json['error'], 'Customer not found')
        print("Response JSON:", response.json)  # Debugging line
        print("Response Status Code:", response.status_code)  # Debugging line
        print("Response Data:", response.get_data(as_text=True)) # Debugging line
        
    # -------------------Invalid Delete Customer Test-------------------
    def test_invalid_delete_customer(self):
        # Attempting to delete a non-existent customer
        response = self.client.delete('/customers/9999/', headers=self.auth_headers)
        self.assertEqual(response.status_code, 404, f"Expected 404 for invalid customer ID, got {response.status_code} with body: {response.get_json()}")
        self.assertEqual(response.json['error'], 'Customer not found')
        print("Response JSON:", response.json)  # Debugging line
        print("Response Status Code:", response.status_code)  # Debugging line
        print("Response Data:", response.get_data(as_text=True)) # Debugging line
        
        
        '''