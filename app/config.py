from os import getenv
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

class CommonConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')  # -------------- Default key is set for development, when going to production, set a strong secret key in .env file
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable track modifications to save memory

class BaseConfig(CommonConfig):
    # Fetching DB_USER and DB_PASSWORD for all environments
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    # If DB_USER and DB_PASSWORD is not set and it is not testing environment, raise an error
    if not DB_USER or not DB_PASSWORD:
        raise ValueError("ERROR: DB_USER or DB_PASSWORD not set in environment.")
    
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@localhost/mechanicshop_db'
    
    # print(f"DB_USER: {DB_USER}, DB_PASSWORD: {DB_PASSWORD}")  # Debugging
    
class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False
    
class TestingConfig(CommonConfig):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory SQLite database for testing
    DEBUG = True
    TESTING = True
    CACHE_TYPE = 'null'  # Use null cache for testing
    RATELIMIT_ENABLED = False
    SECRET_KEY = 'testing_secret_key'

class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False

# Mapping configuration names to classes
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}


