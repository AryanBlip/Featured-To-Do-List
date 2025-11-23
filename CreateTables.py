from app import create_app, db
from models import User, Task  # import ALL models here

app = create_app()

with app.app_context():
    db.create_all()
    print("All tables created successfully!")
