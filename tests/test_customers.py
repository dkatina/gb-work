from app import create_app
from app.models import db
import unittest
from app.config import TestingConfig

class TestCustomer(unittest.TestCase):
    def setUpClass(self):
        self.app = create_app(TestingConfig)
        with self.app_context():
            db.drop_all()
            db.create_all()
        self.client = self.app.test_client()
        