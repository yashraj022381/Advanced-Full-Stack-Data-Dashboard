import os
from app import app, db
from models import User

# Change this to YOUR Neon URL
os.environ["DATABASE_URL"] = "postgresql://username:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require"

with app.app_context():
    db.create_all()
    print("Step 1 done — tables created!")

    existing = User.query.filter_by(username="admin").first()
    if not existing:
        u = User(username="admin", email="admin@gmail.com")
        u.set_password("admin123")
        db.session.add(u)
        db.session.commit()
        print("Step 2 done — admin user created!")
    else:
        print("Admin already exists!")

print("ALL DONE! Login with admin / admin123")
