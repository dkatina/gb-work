from os import getenv
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')  # -------------- Default key is set for development, when going to production, set a strong secret key in .env file
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable track modifications to save memory
    DB_USER = DB_USER
    DB_PASSWORD = DB_PASSWORD

class DevelopmentConfig:
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@localhost/mechanicshop_db'
       
class TestingConfig:
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@localhost/mechanicshop_db'
    
class ProductionConfig:
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@localhost/mechanicshop_db'

print("DB_USER from config:", DB_USER)
print("DB_PASSWORD from config:", DB_PASSWORD)


