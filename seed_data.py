from sqlalchemy import create_engine, text
import pandas as pd
import streamlit as st
from datetime import datetime

print("Connecting to database...")

engine = create_engine(st.secrets["DATABASE_URL"], pool_pre_ping=True)

# Create tables
from models import db
db.metadata.create_all(engine)
print("✅ Tables are ready")

# Load only first 500 rows to make it faster and safer
print("Loading sales data...")
df = pd.read_csv('sales_data_sample.csv', encoding='latin1', nrows=2000)   # ← Only 500 rows

print(f"Inserting {len(df)} sales records...")

with engine.begin() as conn:
    # Clear old data
    conn.execute(text("DELETE FROM sales"))
    conn.execute(text("DELETE FROM products"))

    products_map = {}

    for _, row in df.iterrows():
        product_name = row['PRODUCTLINE']

        if product_name not in products_map:
            result = conn.execute(text("""
                INSERT INTO products (name, category, price, stock)
                VALUES (:name, :category, :price, 1000)
                RETURNING id
            """), {
                "name": product_name,
                "category": product_name,
                "price": float(row['PRICEEACH'])
            })
            product_id = result.scalar()
            products_map[product_name] = product_id

        try:
            sale_date = pd.to_datetime(row['ORDERDATE'])
        except:
            sale_date = datetime.utcnow()

        conn.execute(text("""
            INSERT INTO sales (product_id, quantity, total, sale_date, region)
            VALUES (:product_id, :quantity, :total, :sale_date, :region)
        """), {
            "product_id": products_map[product_name],
            "quantity": int(row['QUANTITYORDERED']),
            "total": float(row['SALES']),
            "sale_date": sale_date,
            "region": row.get('COUNTRY', 'Unknown')
        })

print(f"✅ Seeding completed successfully! {len(products_map)} products and {len(df)} sales inserted.")
print("Now run: streamlit run streamlit_app.py")
