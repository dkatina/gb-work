from app import create_app, db
from app.models import Customer, Mechanic
import unittest
from app.config import config_by_name

# python -m unittest discover tests -v
# python -m unittest tests.test_authentication -v

class TestAuthentication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        print(cls.app.config) # Debugging line
        cls.client = cls.app.test_client()

        # Create an application context
        cls.app.app_context = cls.app.app_context()
        cls.app.app_context.push()
        db.create_all()
        
        # Setting database session from LoginSchema
        from app.blueprints.authentication.authSchemas import LoginSchema
        if hasattr(LoginSchema, 'Meta'):
            setattr(LoginSchema.Meta, 'sqla_session', db.session)
        else:
            # If LoginSchema.Meta doesn't exist, create it
            class Meta:
                sqla_session = db.session
            LoginSchema.Meta = Meta

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app.app_context.pop()
    
    def setUp(self):
        self.connection = db.engine.connect()
        self.transaction = self.connection.begin()
        db.session.bind = self.connection
        db.session.begin_nested()
        
    def tearDown(self):
        db.session.rollback()
        self.transaction.rollback()
        self.connection.close()
        db.session.remove()
    
    
    # -------------------Customer Login Test-------------------
    def test_customer_login(self):
        # Create a test customer
        customer = Customer(name="John Doe", phone="555-555-5555", email="johndoe1@email.com", password="password123")
        db.session.add(customer)
        db.session.commit()
        
        # Attempt to log in
        response = self.client.post('/auth/login', json={
            "email": "johndoe1@email.com",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('auth_token', response.json)
        
    # -------------------Mechanic Login Test-------------------    
    def test_mechanic_login(self):
        # Create a test mechanic
        mechanic = Mechanic(name="Test Mechanic", 
                            phone="555-555-5556", 
                            email="TestMechanic@email.com", 
                            password="password456", 
                            salary=50000)
        mechanic.set_password("password456")  # Hash the password
        db.session.add(mechanic)
        db.session.commit()
        
        # Attempt to log in Mechanic
        response = self.client.post('/auth/login', json={
            "email": "TestMechanic@email.com",
            "password": "password456"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('auth_token', response.json)
    
    # -------------------Invalid Login Test-------------------   
    def test_invalid_login(self):
        # Attempt to log in with invalid credentials should return 401
        response = self.client.post('/auth/login', json={
            "email": "notfound@email.com",
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 401, f"Expected 401 for unauthorized login attempt, got {response.status_code} with body: {response.get_json()}")
        
    @classmethod
    def tearDownClass(cls):
        print("\nFinished Customer route tests.")

