from os import getenv
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

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
print("DB_USER from config:", DB_USER)
print("DB_PASSWORD from config:", DB_PASSWORD)
