from os import getenv
import os
from pathlib import Path

class CommonConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')  # -------------- Default key is set for development, when going to production, set a strong secret key in .env file
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable track modifications to save memory

class BaseConfig(CommonConfig):
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    
    # Debugging DB credentials loading
    if not DB_USER or not DB_PASSWORD:
        print("ERROR: DB_USER or DB_PASSWORD not set in .env file.")
    
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@localhost/mechanicshop_db'
    
    print(f"DB_USER: {DB_USER}, DB_PASSWORD: {DB_PASSWORD}")  # Debugging
    
class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False
    
class TestingConfig(CommonConfig):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'  # Use in-memory SQLite database for testing
    DEBUG = True
    TESTING = True
    CACHE_TYPE = 'null'  # Use null cache for testing
    RATELIMIT_ENABLED = False
    
class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}


