from app import create_app
from app.models import db
import unittest
from app.config import TestingConfig

# python -m unittest discover tests

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
        
    def test_invalid_creation(self):
        customer_payload = {
            "name": "John Doe",
            "phone": "555-555-5555",
            "email": "johndoe@email.com"
        }
        
        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['password'], ['Missing data for required field.'])
        print("Response JSON:", response.json)  # Debugging line
        print("Response Status Code:", response.status_code)  # Debugging line
        print("Response Data:", response.get_data(as_text=True)) # Debugging line