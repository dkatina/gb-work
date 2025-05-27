import uuid
from flask import jsonify, request
from app import create_app
from app.models import Product, db, Mechanic, Admin, ServiceTicket, Customer
import unittest
from app.config import config_by_name
from app.utils.util import not_found


# python -m unittest discover tests -v
# python -m unittest tests.test_service_tickets -v


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

        # Setting database session from ServiceTicketSchema
        from app.blueprints.service_tickets.service_ticketsSchemas import ServiceTicketSchema
        if hasattr(ServiceTicketSchema, 'Meta'):
            setattr(ServiceTicketSchema.Meta, 'sqla_session', db.session)
        else:
            # If ServiceTicketSchema.Meta doesn't exist, create it
            class Meta:
                sqla_session = db.session
            ServiceTicketSchema.Meta = Meta

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
        
    # Service Ticket Routes: Create Service Ticket, Invalid Create Service Ticket, Get All Service Tickets, Invalid Get All Service Tickets, 
    # Get All Service Tickets for Specific Customer or Mechanic, Invalid Get All Service Tickets for Specific Customer or Mechanic, Get Service Ticket by ID, 
    # Invalid Get Service Ticket by ID, Update Existing Service Ticket, Invalid Update Existing Service Ticket, Add a Part to a Service Ticket using PUT, 
    # Invalid Adding Part to Service Ticket using PUT, Delete Service Ticket, Invalid Delete Service Ticket

    # ---------------------- Test Create Service Ticket ----------------------
    def test_create_service_ticket(self):
        # Create a test customer
        test_customer = Customer(
            name="Test Customer",
            phone="123-456-7890",
            email=f"testcustomer_{self.short_uuid()}@em.com",
            password="password123"
        )
        db.session.add(test_customer)
        db.session.commit()
        
        # Create a service ticket
        response = self.client.post('/service_tickets/', json={
            "customer_id": test_customer.id,
            "vin": "1HGCM82633A123456",
            "service_desc": "Test Service Ticket"
        }, headers=self.auth_headers)
        
        self.assertEqual(response.status_code, 201)
        data = response.json['service_ticket']
        self.assertEqual(data['service_desc'], "Test Service Ticket")
        self.assertEqual(data['vin'], "1HGCM82633A123456")
    
        
    # ---------------------- Test Invalid Create Service Ticket ----------------------
    def test_invalid_create_service_ticket(self):
        # Attempt to create a service ticket without a customer ID
        response = self.client.post('/service_tickets', json={
            "vin": "2GHCM82633A123456",
            "service_desc": "Invalid Test Service Ticket"
        }, headers=self.auth_headers)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Missing data for required field.', response.get_data(as_text=True))
    
        
    # ---------------------- Test Get All Service Tickets ----------------------
    def test_get_all_service_tickets(self):
        # Create a service ticket
        test_customer = Customer(
            name="Getall Customer",
            phone="135-456-7890",
            email=f"testcustomer_{self.short_uuid()}@em.com",
            password="password123"
        )
        db.session.add(test_customer)
        db.session.commit()
        
        response = self.client.post('/service_tickets/', json={
            "customer_id": test_customer.id,
            "vin": "3TNCM82633A123456",
            "service_desc": "Test Get All Service Ticket"
        }, headers=self.auth_headers)
        
        # Get all service tickets
        response = self.client.get('/service_tickets/', headers=self.auth_headers)
        print("Response JSON:", response.json)  # Debugging line
        print("Response Status Code:", response.status_code)  # Debugging line
        print("Response Data:", response.get_data(as_text=True)) # Debugging line
        print("Raw Response:", response.get_data(as_text=True)) # Debugging line
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json['service_tickets'], list)
    
    
    # ---------------------- Test Invalid Get All Service Tickets ----------------------
    def test_invalid_get_all_service_tickets(self):
        response = self.client.get('/service_tickets/?page=not_a_number')
        
        print("Response JSON:", response.json)  # Debugging line
        print("Response Status Code:", response.status_code)  # Debugging line
        print("Response Data:", response.get_data(as_text=True)) # Debugging line
        
        self.assertEqual(response.status_code, 200, f"Expected 200 for invalid page number, got {response.status_code}")
        self.assertEqual(response.json.get('error'), 'Page not found or exceeds total pages')
        self.assertEqual(len(response.json.get('service_tickets', [])), 0)

    
    # ---------------------- Test Get All Service Tickets for Specific Customer ----------------------
    def test_get_all_service_tickets_for_customer(self):
        # Create a test customer
        test_customer = Customer(
            name="Specific Customer",
            phone="123-456-7140",
            email=f"testcustomer_{self.short_uuid()}@em.com",
            password="password123"
        )
        db.session.add(test_customer)
        db.session.commit()
        
        # Create a service ticket for the test customer
        response = self.client.post('/service_tickets/', json={
            "customer_id": test_customer.id,
            "vin": "4IAEM82633A123456",
            "service_desc": "Test Get All Service Ticket Specific Customer"
        }, headers=self.auth_headers)
        
        # Login as the test customer
        login_response = self.client.post('/auth/login', json={
            "email": test_customer.email,
            "password": "password123"
        })
        
        self.auth_headers = {
            'Authorization': f'Bearer {login_response.json.get("auth_token")}'
        }
    
        # Get all service tickets for the test customer
        response = self.client.get(f'/service_tickets/my-tickets/', headers=self.auth_headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(ticket["customer_id"] == test_customer.id for ticket in response.json))


    
    # ---------------------- Test Get All Service Tickets for Specific Mechanic ----------------------
    def test_get_all_service_tickets_for_mechanic(self):
        # Create a test customer
        test_customer = Customer(
            name="Specific Customer",
            phone="123-916-7140",
            email=f"testcustomer_{self.short_uuid()}@em.com",
            password="password123"
        )
        db.session.add(test_customer)
        db.session.commit()
        
        # Create a test mechanic
        test_mechanic = Mechanic(
            name="Specific Mechanic",
            phone="129-456-7890",
            email=f"testmechanic_{self.short_uuid()}@em.com",
            salary=60000,
            password="password123"
        )
        db.session.add(test_mechanic)
        db.session.commit()

        # Create a service ticket for the test customer
        response = self.client.post('/service_tickets/', json={
            "customer_id": test_customer.id,
            "mechanic_ids": [test_mechanic.id],
            "vin": "4IAEM82633A123456",
            "service_desc": "Test Get All Service Ticket Specific Mechanic"
        }, headers=self.auth_headers)
        
        # Login as the test mechanic
        login_response = self.client.post('/auth/login', json={
            "email": test_mechanic.email,
            "password": "password123"
        })
        
        self.auth_headers = {
            'Authorization': f'Bearer {login_response.json.get("auth_token")}'
        }
        
        # Get all service tickets for the test mechanic
        response = self.client.get(f'/service_tickets/my-tickets/', headers=self.auth_headers)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(test_mechanic.id in ticket["mechanic_ids"] for ticket in response.json))


    # ---------------------- Test Invalid Get All Service Tickets for Specific Customer ----------------------
    def test_invalid_get_all_service_tickets_for_customer(self):
        # Creating a test customer
        test_customer = Customer(
            name="Invalid Customer",
            phone="123-456-7890",
            email=f"testcustomer_{self.short_uuid()}@em.com",
            password="password123"
        )
        db.session.add(test_customer)
        db.session.commit()
        print("Test Customer ID:", test_customer.id)  # Debugging line
        
        # Logging in as the test customer
        login_response = self.client.post('/auth/login', json={
            "email": test_customer.email,
            "password": "password123"
        })
        print("Login response data:", login_response.get_data(as_text=True))
        token = login_response.json.get('auth_token')
        self.auth_headers = {
            'Authorization': f'Bearer {token}'
        }
        
        # Delete the test customer
        db.session.delete(test_customer)
        db.session.commit()
        
        # Attempt to get all service tickets for a non-existent customer
        response = self.client.get('/service_tickets/my-tickets/', headers=self.auth_headers)
        self.assertEqual(response.status_code, 401)
        self.assertIn('Token invalid or user not found', response.get_json().get('error', ''))
        

    # ---------------------- Test Invalid Get All Service Tickets for Specific Mechanic ----------------------
    def test_invalid_get_all_service_tickets_for_mechanic(self):
        # Create a test mechanic
        test_mechanic = Mechanic(
            name="Invalid Mechanic",
            phone="123-456-7890",
            email=f"testmechanic_{self.short_uuid()}@em.com",
            salary=60000,
            password="password123"
        )
        db.session.add(test_mechanic)
        db.session.commit()

        # Logging in as the test mechanic
        login_response = self.client.post('/auth/login', json={
            "email": test_mechanic.email,
            "password": "password123"
        })
        token = login_response.json.get('auth_token')
        self.auth_headers = {
            'Authorization': f'Bearer {token}'
        }

        # Delete the test mechanic
        db.session.delete(test_mechanic)
        db.session.commit()

        # Attempt to get all service tickets for a non-existent mechanic
        response = self.client.get('/service_tickets/my-tickets/', headers=self.auth_headers)

        self.assertEqual(response.status_code, 401)
        self.assertIn('Token invalid or user not found', response.get_json().get('error', ''))


    # ---------------------- Test Get Service Ticket by ID ----------------------
    def test_get_service_ticket_by_id(self):
        # Create a test customer
        test_customer = Customer(
            name="ID Customer",
            phone="123-436-7890",
            email=f"testcustomer_{self.short_uuid()}@em.com",
            password="password123"
        )
        db.session.add(test_customer)
        db.session.commit()
        
        # Create a service ticket for the test customer
        response = self.client.post('/service_tickets/', json={
            "customer_id": test_customer.id,
            "vin": "5UXHM82633A123456",
            "service_desc": "Test Get Service Ticket by ID"
        }, headers=self.auth_headers)
        
        service_ticket_id = response.json.get('service_ticket_id')
        self.assertIsNotNone(service_ticket_id, "Service ticket ID should not be None")
        print("Create ticket response:", response.status_code, response.json) # Debugging line
        print("Service ticket ID:", service_ticket_id)  # Debugging line
        print("Auth headers:", self.auth_headers) # Debugging line

        # Get the service ticket by ID
        response = self.client.get(f'/service_tickets/{service_ticket_id}', headers=self.auth_headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Service ticket retrieved successfully', response.get_data(as_text=True))
        
    
    # ---------------------- Test Invalid Get Service Ticket by ID ----------------------
    def test_invalid_get_service_ticket_by_id(self):
        # Attempt to get a service ticket by a non-existent ID
        response = self.client.get('/service_tickets/99999999', headers=self.auth_headers)
        
        self.assertEqual(response.status_code, 404)
        self.assertIn('Service ticket not found', response.get_data(as_text=True))
    
    
    # ---------------------- Test Update Existing Service Ticket ----------------------
    def test_update_service_ticket(self):
        # Create a test customer
        test_customer = Customer(
            name="UpdateST Customer",
            phone="723-456-7890",
            email=f"testcustomer_{self.short_uuid()}@em.com",
            password="password123"
        )
        db.session.add(test_customer)
        db.session.commit()
        
        # Create a service ticket for the test customer
        response = self.client.post('/service_tickets/', json={
            "customer_id": test_customer.id,
            "vin": "5UXHM82633A123456",
            "service_desc": "Test Update Service Ticket"
        }, headers=self.auth_headers)
        
        service_ticket_id = response.json.get('service_ticket_id')
        
        # Updating the service ticket with new description and VIN
        updated_desc = "Updated Service Ticket Description"
        updated_vin = "5UXHM82633A123456"
        
        # Update the service ticket
        response = self.client.put(f'/service_tickets/{service_ticket_id}', json={
            "service_desc": updated_desc,
            "vin": updated_vin,
        }, headers=self.auth_headers)
        
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertIsNotNone(response_json, "Response JSON should not be None")
        
        ticket = response_json.get('service_ticket')
        self.assertIsNotNone(ticket, "Response should include 'service_ticket' key")
        self.assertEqual(ticket.get('service_desc'), updated_desc)
        self.assertEqual(ticket.get('vin'), updated_vin)

    
    # ---------------------- Test Invalid Update Existing Service Ticket ----------------------
    def test_invalid_update_service_ticket(self):
        # Attempt to update a service ticket with a non-existent ID
        response = self.client.put('/service_tickets/99999999', json={
            "service_desc": "Updated Service Ticket",
        }, headers=self.auth_headers)
        
        self.assertEqual(response.status_code, 404)
        self.assertIn('Service ticket not found', response.get_data(as_text=True))
    
    
        
    # ---------------------- Test Add a product to a Service Ticket using PUT ----------------------
    def test_add_product_to_service_ticket(self):
        # Create a test customer
        test_customer = Customer(
            name="Test Customer",
            phone="123-456-4290",
            email=f"testcustomer_{self.short_uuid()}@em.com",
            password="password123"
        )
        db.session.add(test_customer)
        db.session.commit()
        
        # Create a service ticket for the test customer
        response = self.client.post('/service_tickets/', json={
            "customer_id": test_customer.id,
            "service_desc": "Test Add Part Service Ticket",
            "vin": "6PQTM82633A123456",
        }, headers=self.auth_headers)
        
        service_ticket_id = response.json.get('service_ticket_id')

        # Create a test product
        test_product = Product(
            name="Test product",
            price=100.00,
            )
        db.session.add(test_product)
        db.session.commit()
        
        # Add a part to the service ticket
        response = self.client.put(f'/service_tickets/{service_ticket_id}/add_product/', json={
            "product_id": test_product.id,
            "quantity": 1
        }, headers=self.auth_headers)
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data.get('message'), 'Product added successfully')
    

    # ---------------------- Test Invalid Adding Product to Service Ticket using PUT ----------------------
    def test_invalid_add_product_to_service_ticket(self):
        # Create a test product
        test_product = Product(
            name="Product Test",
            price=150.00,
            )
        db.session.add(test_product)
        db.session.commit()
        
        # Attempt to add a product to a service ticket with a non-existent ID
        response = self.client.put('/service_tickets/99999999/add_product/', json={
            "product_id": test_product.id,
            "quantity": 1
        }, headers=self.auth_headers)
        
        self.assertEqual(response.status_code, 404)
        self.assertIn('Service ticket not found', response.get_data(as_text=True))
    
        
    # ---------------------- Test Delete Service Ticket ----------------------
    def test_delete_service_ticket(self):
        # Create a test customer
        test_customer = Customer(
            name="Test Customer",
            phone="123-456-7890",
            email=f"testcustomer_{self.short_uuid()}@em.com",
            password="password123"
        )
        db.session.add(test_customer)
        db.session.commit()
        
        # Create a service ticket for the test customer
        response = self.client.post('/service_tickets', json={
            "customer_id": test_customer.id,
            "service_desc": "Test Delete Service Ticket",
            "vin": "7XHQM82633A123456",
        }, headers=self.auth_headers)
        
        service_ticket_id = response.json.get('service_ticket_id')
        
        # Delete the service ticket
        response = self.client.delete(f'/service_tickets/{service_ticket_id}', headers=self.auth_headers)
        
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data.get('message'), f"Service ticket {service_ticket_id} deleted successfully")
    
    
    # ---------------------- Test Invalid Delete Service Ticket ----------------------
    def test_invalid_delete_service_ticket(self):
        # Attempt to delete a service ticket with a non-existent ID
        response = self.client.delete('/service_tickets/99999999', headers=self.auth_headers)
        
        data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data.get('error'), 'Service ticket not found')