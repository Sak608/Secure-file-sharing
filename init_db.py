from app import db
from app.models import User, File
from app import create_app  # assumes you wrap your app in create_app()

app = create_app()

with app.app_context():
    db.create_all()
    print("Database initialized.")
