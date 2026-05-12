import os
from app import app, db
from models import User

# Change this to YOUR Neon URL
os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_J4XPGqNfC6Hl@ep-icy-shadow-ap159j2b-pooler.c-7.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

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
