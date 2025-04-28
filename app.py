from app import create_app
from app.models import db
import os
from app.config import DevelopmentConfig, TestingConfig, ProductionConfig

# Getting environment settings from env but will default to DevelopmentConfig if not set
flask_env = os.getenv('FLASK_ENV', 'development')

# Setting config class based on the environment variable
if flask_env == 'development':
    config_class = DevelopmentConfig
elif flask_env == 'testing':
    config_class = TestingConfig
elif flask_env == 'production': 
    config_class = ProductionConfig
else:
    config_class = DevelopmentConfig # Default to DevelopmentConfig if FLASK_ENV is not set
    
print(f"Using configuration: {config_class.__name__}") # Debugging line to check which config is being used

app = create_app(config_class)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()   