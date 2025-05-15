import uuid
from flask import jsonify, request
from app import create_app
from app.models import db, Mechanic, Admin
import unittest
from app.config import TestingConfig

# python -m unittest discover tests -v
# python -m unittest tests.test_mechanics -v



class TestMechanic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(TestingConfig)
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        
        cls.client = cls.app.test_client()
        db.create_all()
        
        # Creating a test admin for all tests
        # This admin will be used for authentication in the tests
        admin = Admin(
            name="Super Admin",
            email="admin@email.com"
            )
        admin.set_password("adminpassword")
        db.session.add(admin)
        db.session.commit()
    
    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()
    
    @staticmethod
    def short_uuid():
        #Generate a short UUID for unique test data.
        import uuid
        return str(uuid.uuid4())[:8]

    def setUp(self):
        self.connection = db.engine.connect()
        self.transaction = self.connection.begin()
        db.session.bind = self.connection
        db.session.begin_nested()
        
        # Creating a test mechanic
        self.test_email = f"tc_{self.short_uuid()}@em.com"
        test_mechanic = Mechanic(
            name="Test Mechanic",
            phone="666-666-6666",
            email=self.test_email,
            salary=60000
        )
        test_mechanic.set_password("password123")
        db.session.add(test_mechanic)
        db.session.commit()
        print("Test Mechanic ID:", test_mechanic.id)  # Debugging line
        
        # Setting up test login credentials
        login_response = self.client.post('/auth/login', json={
            "email": "admin@email.com",
            "password": "adminpassword"
        })
        token = login_response.json.get('auth_token')
        self.auth_headers = {
            'Authorization': f'Bearer {token}'
        }
        
    def tearDown(self):
        db.session.rollback()
        self.transaction.rollback()
        self.connection.close()
        db.session.remove()
        
# Mechanic Routes: Create Mechanic, Get All Mechanics, Get Mechanic by ID, Get list of mechanics in order of who has worked on the most tickets /most-worked, Get Mechanic by Name, Update Existing Mechanic, Delete Mechanic

# ----------------Test Create Mechanic-------------------- ***
    def test_create_mechanic(self):
        response = self.client.post('/mechanics/', json={
            "name": "John Doe",
            "phone": "123-456-7890",
            "email": f"john_doe_{self.short_uuid()}@example.com",
            "salary": 50000,
            "password": "password123"
        }, headers=self.auth_headers)
        
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.json)
        self.assertIn('name', response.json)
        self.assertIn('phone', response.json)
        self.assertIn('email', response.json)
    
    # ------------Test Invalid Create Mechanic---------------- ***
    def test_create_mechanic_invalid(self):
        response = self.client.post('/mechanics/', json={
            "name": "John Doe",
            "phone": "123-456-7890",
            "email": f"john_doe_{self.short_uuid()}@example.com",
            "salary": 50000,
            # Missing password
        }, headers=self.auth_headers)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
    
    # ------------Test Get All Mechanics----------------- ***
    def test_get_all_mechanics(self):
        response = self.client.get('/mechanics/', headers=self.auth_headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)  # Check if the response is a list
        if len(response.json) > 0:
            self.assertIn('id', response.json[0])
            self.assertIn('name', response.json[0])
            self.assertIn('phone', response.json[0])
            self.assertIn('email', response.json[0])
    
    # ------------Test Invalid Get All Mechanics---------------- ***
    def test_get_all_mechanics_invalid(self):
        response = self.client.get('/mechanics/?page=not_a_number')
        
        print("Response JSON:", response.json)  # Debugging line
        print("Response Status Code:", response.status_code)  # Debugging line
        print("Response Data:", response.get_data(as_text=True)) # Debugging line
        
        self.assertEqual(response.status_code, 200, f"Expected 200 for invalid page number, got {response.status_code}")
        self.assertEqual(response.json.get('error'), 'Page not found.')
        self.assertEqual(len(response.json.get('mechanics', [])), 0)
    
    # ---------------Test Get Mechanic by ID----------------- ***
    def test_get_mechanic_by_id(self):
        # Assuming the first mechanic in the database is the one we just created
        mechanic_id = Mechanic.query.first().id
        response = self.client.get(f'/mechanics/{mechanic_id}', headers=self.auth_headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.json)
        self.assertIn('name', response.json)
        self.assertIn('phone', response.json)
        self.assertIn('email', response.json)
    
    # --------------Test Invalid Get Mechanic by ID---------------- ***
    def test_get_mechanic_by_id_invalid(self):
        response = self.client.get('/mechanics/999999', headers=self.auth_headers)
        
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'], 'Mechanic not found.')
    
    # -----------------Test Get Mechanic by Name---------------- ***
    def test_get_mechanic_by_name(self):
        response = self.client.get('/mechanics/search', headers=self.auth_headers, query_string={'name': 'Test Mechanic'})
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)  # Check if the response is a list
        if len(response.json) > 0:
            self.assertIn('id', response.json[0])
            self.assertIn('name', response.json[0])
            self.assertIn('phone', response.json[0])
            self.assertIn('email', response.json[0])
    
    # --------------Test Invalid Get Mechanic by Name---------------- ***
    def test_get_mechanic_by_name_invalid(self):
        response = self.client.get('/mechanics/search', headers=self.auth_headers, query_string={'name': 'Nonexistent Mechanic'})
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)  # Check if the response is a list
        self.assertEqual(len(response.json), 0)  # No mechanics should be found
    
    # ---------------Test Get Mechanics by Most Worked---------------- ***
    def test_get_mechanics_by_most_worked(self):
        response = self.client.get('/mechanics/most-worked', headers=self.auth_headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)  # Check if the response is a list
        if len(response.json) > 0:
            self.assertIn('id', response.json[0])
            self.assertIn('name', response.json[0])
            self.assertIn('phone', response.json[0])
            self.assertIn('email', response.json[0])
    
    # --------------Test Invalid Get Mechanics by Most Worked----------------
    def test_get_mechanics_by_most_worked_invalid(self):
        response = self.client.get('/mechanics/most-worked', headers=self.auth_headers, query_string={'invalid_param': 'value'})
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)  # Check if the response is a list
        if len(response.json) > 0:
            self.assertIn('id', response.json[0])
            self.assertIn('name', response.json[0])
            self.assertIn('phone', response.json[0])
            self.assertIn('email', response.json[0])
    '''
    # ---------------Test Update Mechanic-----------------
    def test_update_mechanic(self):
        # Assuming the first mechanic in the database is the one we just created
        mechanic_id = Mechanic.query.first().id
        response = self.client.put(f'/mechanics/{mechanic_id}', json={
            "name": "Updated Mechanic",
            "phone": "987-654-3210",
            "email": f"updated_{self.short_uuid()}@example.com",
            "password": "newpassword123"
        }, headers=self.auth_headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.json)
        self.assertIn('name', response.json)
        self.assertIn('phone', response.json)
        self.assertIn('email', response.json)
    
    # --------------Test Invalid Update Mechanic----------------
    def test_update_mechanic_invalid(self):
        # Assuming the first mechanic in the database is the one we just created
        mechanic_id = Mechanic.query.first().id
        response = self.client.put(f'/mechanics/{mechanic_id}', json={
            "name": "Updated Mechanic",
            "phone": "987-654-3210",
            # Missing email and password
        }, headers=self.auth_headers)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
    
       
    # ---------------Test Delete Mechanic----------------
    def test_delete_mechanic(self):
        # Assuming the first mechanic in the database is the one we just created
        mechanic_id = Mechanic.query.first().id
        response = self.client.delete(f'/mechanics/{mechanic_id}', headers=self.auth_headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)
        
    
    # --------------Test Invalid Delete Mechanic----------------
    def test_delete_mechanic_invalid(self):
        response = self.client.delete('/mechanics/999999', headers=self.auth_headers)
        
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'], 'Mechanic not found.')
        
    '''