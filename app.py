from app import create_app
from app.models import db
import os
from app.config import config_by_name
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Determine config name
env = os.getenv('FLASK_ENV', 'development')
config_class = config_by_name.get(env, config_by_name['development'])

print(f"Using configuration: {config_class.__name__}")

config_name = os.getenv("FLASK_ENV", "development")

app = create_app(config_name)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()   