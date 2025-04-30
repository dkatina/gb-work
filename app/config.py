from os import getenv
import os
from pathlib import Path

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

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}


