import uuid
from flask import jsonify, request
from app import create_app
from app.models import db, Mechanic, Admin
import unittest
from app.config import config_by_name


# python -m unittest discover tests -v
# python -m unittest tests.test_mechanics -v



class TestMechanic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        print(cls.app.config) # Debugging line
        cls.client = cls.app.test_client()

        # Create an application context
        cls.app.app_context = cls.app.app_context()
        cls.app.app_context.push()
        db.create_all()

        # Setting database session from MechanicSchema
        from app.blueprints.mechanics.mechanicsSchemas import MechanicSchema
        if hasattr(MechanicSchema, 'Meta'):
            setattr(MechanicSchema.Meta, 'sqla_session', db.session)
        else:
            # If MechanicSchema.Meta doesn't exist, create it
            class Meta:
                sqla_session = db.session
            MechanicSchema.Meta = Meta

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
        cls.app.app_context.pop()
    
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
        print("Login response data:", login_response.get_data(as_text=True))
        
        token = login_response.json.get('auth_token')
        self.auth_headers = {
            'Authorization': f'Bearer {token}'
        }
        
        print("Login response status:", login_response.status_code)

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
        self.assertIn('password', response.json)
        self.assertIn('Missing data for required field.', response.json['password'])

    
    # ------------Test Get All Mechanics----------------- ***
    def test_get_all_mechanics(self):
        response = self.client.get('/mechanics/', headers=self.auth_headers)
        
        response = self.client.get('/mechanics/')
        print("Response JSON:", response.json)  # Debugging line
        print("Response Status Code:", response.status_code)  # Debugging line
        print("Response Data:", response.get_data(as_text=True)) # Debugging line
        print("Raw Response:", response.get_data(as_text=True)) # Debugging line
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json['mechanics'], list)

    # ------------Test Invalid Get All Mechanics---------------- ***
    def test_get_all_mechanics_invalid(self):
        response = self.client.get('/mechanics/?page=not_a_number')
        
        print("Response JSON:", response.json)  # Debugging line
        print("Response Status Code:", response.status_code)  # Debugging line
        print("Response Data:", response.get_data(as_text=True)) # Debugging line
        
        self.assertEqual(response.status_code, 200, f"Expected 200 for invalid page number, got {response.status_code}")
        self.assertEqual(response.json.get('error'), 'Page not found or exceeds total pages')
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
        response = self.client.get('/mechanics/search/?name=invalidname', headers=self.auth_headers)
        
        print("Status Code:", response.status_code)
        print("Response JSON:", response.get_json())
        
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
    
    # --------------Test Invalid Get Mechanics by Most Worked---------------- ***
    def test_get_mechanics_by_most_worked_invalid(self):
        response = self.client.get('/mechanics/most-worked', headers=self.auth_headers, query_string={'invalid_param': 'value'})
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)  # Check if the response is a list
        if len(response.json) > 0:
            self.assertIn('id', response.json[0])
            self.assertIn('name', response.json[0])
            self.assertIn('phone', response.json[0])
            self.assertIn('email', response.json[0])
    
    # ---------------Test Update Mechanic-----------------
    def test_update_mechanic(self):
        # Getting the mechanic ID from the test mechanic created in setUp
        mechanic = Mechanic.query.filter_by(email=self.test_email).first()
        self.assertIsNotNone(mechanic, "Mechanic should exist in the database.")
        
        mechanic_id = mechanic.id
        
        mechanic_payload = {
            "name": "Update Mechanic",
            "phone": "444-666-6666",
            "email": f"tc_{self.short_uuid()}@em.com",
            "salary": 60000,
            "password": "password123"
        }
        response = self.client.put(f'/mechanics/{mechanic_id}/', json=mechanic_payload, headers=self.auth_headers)
        print("Response JSON:", response.json)  # Debugging line
        print("Response Status Code:", response.status_code)  # Debugging line
        print("Response Data:", response.get_data(as_text=True)) # Debugging line
        self.assertEqual(response.status_code, 200)
        
        expected = {
            "id": mechanic_id,
            "name": mechanic_payload['name'],
            "phone": mechanic_payload['phone'],
            "email": mechanic.email,
            "salary": mechanic_payload['salary'],
        }
        for key in expected:
            self.assertEqual(response.json[key], expected[key])
    
    # --------------Test Invalid Update Mechanic----------------
    def test_update_mechanic_invalid(self):
        # Getting the mechanic ID from the test mechanic created in setUp
        mechanic = Mechanic.query.filter_by(email=self.test_email).first()
        self.assertIsNotNone(mechanic, "Mechanic should exist in the database.")
        
        mechanic_id = mechanic.id
        response = self.client.put(f'/mechanics/{mechanic_id}', json={
            "salary": "sixty thousand",  # Invalid salary
        }, headers=self.auth_headers)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('salary', response.json)
    
    
    # ---------------Test Delete Mechanic---------------- ***
    def test_delete_mechanic(self):
        # Creating a mechanic to delete just for this test
        delete_em = f"delete_{self.short_uuid()}@em.com"
        delete_mechanic = Mechanic(
            name="Delete Mech",
            phone="777-444-7777",
            email=delete_em,
            salary=60000,
            password="password123"
        )
        db.session.add(delete_mechanic)
        db.session.commit()
        mechanic_id = delete_mechanic.id
        print("Mechanic ID to delete:", mechanic_id)  # Debugging line
        
        # Deleting the mechanic
        response = self.client.delete(f'/mechanics/{mechanic_id}', headers=self.auth_headers)
        print("Response JSON:", response.json)  # Debugging line
        print("Response Status Code:", response.status_code)  # Debugging line
        print("Response Data:", response.get_data(as_text=True)) # Debugging line
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], f"Mechanic {mechanic_id} deleted successfully")
        
    
    # --------------Test Invalid Delete Mechanic----------------
    def test_delete_mechanic_invalid(self):
        # Attempting to delete a non-existent mechanic
        response = self.client.delete('/mechanics/9999/', headers=self.auth_headers)
        mechanic_payload = {
            9999
            }
        
        print("Response JSON:", response.json)  # Debugging line
        print("Response Status Code:", response.status_code)  # Debugging line
        print("Response Data:", response.get_data(as_text=True)) # Debugging line
        self.assertEqual(response.status_code, 404, f"Expected 404 for invalid mechanic ID, got {response.status_code} with body: {response.get_json()}")
        self.assertEqual(response.json['error'], 'Mechanic not found.')
        
