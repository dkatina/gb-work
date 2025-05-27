import uuid
from flask import jsonify, request
from app import create_app
from app.models import Product, db, Mechanic, Admin, Customer
import unittest
from app.config import config_by_name
from app.utils.util import not_found


# python -m unittest discover tests -v
# python -m unittest tests.test_inventory -v


class TestServiceTicket(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        print(cls.app.config) # Debugging line
        cls.client = cls.app.test_client()

        # Create an application context
        cls.app.app_context = cls.app.app_context()
        cls.app.app_context.push()
        db.create_all()
        
        # Setting database session from inventorySchemas
        from app.blueprints.inventory.inventorySchemas import ProductSchema
        if hasattr(ProductSchema, 'Meta'):
            setattr(ProductSchema.Meta, 'sqla_session', db.session)
        else:
            # If ProductSchema.Meta doesn't exist, create it
            class Meta:
                sqla_session = db.session
            ProductSchema.Meta = Meta
            
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
        
        # Creating a test customer
        self.test_email = f"tc_{self.short_uuid()}@em.com"
        test_customer = Customer(
            name="Test Customer",
            phone="666-666-6636",
            email=self.test_email,
            password="password123"
        )
        db.session.add(test_customer)
        db.session.commit()
        print("Test Customer ID:", test_customer.id)  # Debugging line
        
        # Creating a test mechanic
        self.test_email = f"tc_{self.short_uuid()}@em.com"
        test_mechanic = Mechanic(
            name="Test Mechanic",
            phone="696-666-6666",
            email=self.test_email,
            salary=60000,
            password="password123"
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
        
# Inventory Routes: Create new inventory product, Invalid Create new inventory product, Get all Inventory Products, Invalid Get all inventory products, 
# Get Specific Inventory Product, Invalid Get Specific Inventory Product, Update Existing Inventory Product, Invalid Update Existing Inventory Product, 
# Delete Inventory Product, Invalid Delete Inventory Product

# ------------------------------ Test Create Inventory Product ------------------------------
    def test_create_inventory_product(self):
        # Test creating a new inventory product
        response = self.client.post('/inventory/', json={
            "name": "Test Product",
            "price": 19.99 
        }, headers=self.auth_headers)
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.json)
        self.assertEqual(response.json['name'], 'Test Product')
        self.assertEqual(response.json['price'], 19.99)
        
    
# ------------------------------ Test Invalid Create Inventory Product ------------------------------
    def test_invalid_create_inventory_product(self):
        # Test creating a new inventory product with invalid data
        response = self.client.post('/inventory/', json={
            "name": "",
            "price": -19.99
        }, headers=self.auth_headers)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('name', response.json)
        self.assertIn('price', response.json)
        self.assertIn('Name cannot be empty.', response.json['name'])
        self.assertIn('Price must be greater than zero.', response.json['price'])

    
# ------------------------------ Test Get All Inventory Products ------------------------------
    def test_get_all_inventory_products(self):
        # Test getting all inventory products
        response = self.client.get('/inventory/', headers=self.auth_headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('products', response.json)
        self.assertIsInstance(response.json['products'], list)
        self.assertGreater(len(response.json['products']), 0)  # Ensure there is at least one product
        for product in response.json['products']:
            self.assertIn('id', product)
            self.assertIn('name', product)
            self.assertIn('price', product)

        # Ensure the product has the correct attributes
        first_product = response.json["products"][0]
        self.assertEqual(first_product['name'], 'Test Product')
        self.assertEqual(first_product['price'], 19.99)

# ------------------------------ Test Invalid Get All Inventory Products ------------------------------
    def test_invalid_get_all_inventory_products(self):
        # Test getting all inventory products with invalid headers
        response = self.client.get('/inventory/?page=not_a_number')
        
        print("Response JSON:", response.json)  # Debugging line
        print("Response Status Code:", response.status_code)  # Debugging line
        print("Response Data:", response.get_data(as_text=True)) # Debugging line
        
        self.assertEqual(response.status_code, 200, f"Expected 200 for invalid page number, got {response.status_code}")
        self.assertEqual(response.json.get('error'), 'Page not found or exceeds total pages')
        self.assertEqual(len(response.json.get('products', [])), 0)


# ------------------------------ Test Get Specific Inventory Product ------------------------------
    def test_get_specific_inventory_product(self):
        # Test getting a specific inventory product
        response = self.client.get('/inventory/1', headers=self.auth_headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.json)
        self.assertIn('name', response.json)
        self.assertIn('price', response.json)
        self.assertEqual(response.json['id'], 1)
        

# ------------------------------ Test Invalid Get Specific Inventory Product ------------------------------
    def test_invalid_get_specific_inventory_product(self):
        # Test getting a specific inventory product with invalid ID
        response = self.client.get('/inventory/999', headers=self.auth_headers)

        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json)
        self.assertIn('Product not found', response.json['error'])

    
# ------------------------------ Test Update Existing Inventory Product ------------------------------
    def test_update_existing_inventory_product(self):
        # Test updating an existing inventory product
        response = self.client.put('/inventory/1', json={
            "name": "Updated Product",
            "price": 29.99
        }, headers=self.auth_headers)

        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.json)
        self.assertEqual(response.json['id'], 1)
        self.assertEqual(response.json['name'], 'Updated Product')
        self.assertEqual(response.json['price'], 29.99)
        
        
# ------------------------------ Test Invalid Update Existing Inventory Product ------------------------------
    def test_invalid_update_existing_inventory_product(self):
        # Test updating an existing inventory product with invalid data
        response = self.client.put('/inventory/1', json={
            "name": "",
            "price": -29.99 
        }, headers=self.auth_headers)
    
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data.get('error'), 'Invalid input')


# ------------------------------ Test Delete Inventory Product ------------------------------
    def test_delete_inventory_product(self):
        # Creating a product to delete
        new_product = Product(name="Product to Delete", price=10.99)
        db.session.add(new_product)
        db.session.commit()

        # Test deleting an inventory product
        response = self.client.delete(f'/inventory/{new_product.id}', headers=self.auth_headers)

        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data.get('message'), 'Product deleted successfully from inventory')

    
# ------------------------------ Test Invalid Delete Inventory Product ------------------------------
    def test_invalid_delete_inventory_product(self):
        # Test deleting an inventory product with invalid ID
        response = self.client.delete('/inventory/999', headers=self.auth_headers)
        
        data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data.get('error'), 'Product not found')
        
