import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Secret key for session security (login cookies)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-prod'

        # PostgreSQL connection string format:
    # postgresql://username:password@host:port/dbname
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:password@localhost/sales_db'


     # Disable modification tracking (saves memory)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# .env file (NEVER commit this to GitHub!)
# DATABASE_URL=postgresql://user:pass@host/dbname
# SECRET_KEY=your-random-secret-key
