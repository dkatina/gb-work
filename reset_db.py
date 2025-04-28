# reset_db.py

from app import create_app, db # Import the db object from your models module
from app.config import DevelopmentConfig

app = create_app(DevelopmentConfig)

with app.app_context():
    db.drop_all()
    db.create_all()
    print("✅ Database reset: all tables recreated, no data.")
