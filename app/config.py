from os import getenv
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

class DevelopmentConfig:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@localhost/mechanicshop_db'
    DEBUG = True
    
class TestingConfig:
    pass
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@localhost/mechanicshop_test_db'
    DEBUG = True
    """
    
class ProductionConfig:
    pass
    """
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@localhost/mechanicshop_db'
    DEBUG = False
    TESTING = False
    """
