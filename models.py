from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# ── TABLE 1: users ──────────────────────────────────────

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email    = db.Column(db.String(120), unique=True, nullable=False)


    # Store HASHED password, never plain text!
    password_hash = db.Column(db.String(256))
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# ── TABLE 2: products ───────────────────────────────────
class Product(db.Model):
    __tablename__ = 'products'
    
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))
    price    = db.Column(db.Numeric(10, 2))   # 10 digits, 2 decimal
    stock    = db.Column(db.Integer, default=0)
    
    # One product → many sales (relationship)
    sales = db.relationship('Sale', backref='product', lazy=True)


# ── TABLE 3: sales ──────────────────────────────────────
class Sale(db.Model):
    __tablename__ = 'sales'
    
    id         = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity   = db.Column(db.Integer)
    total      = db.Column(db.Numeric(10, 2))
    sale_date  = db.Column(db.DateTime, default=datetime.utcnow)
    region     = db.Column(db.String(50))

# Add index for fast queries on date range filters
# This makes WHERE sale_date BETWEEN x AND y very fast
db.Index('idx_sale_date', Sale.sale_date)
db.Index('idx_product_id', Sale.product_id)
db.Index('idx_region', Sale.region)
db.Index('idx_product_category', Product.category)

print("Models loaded with indexes")




