# Part 1: imports, DB connection, data loading
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
from datetime import datetime
from models import db, User, Product, Sale   # reuse your existing models!
from werkzeug.security import generate_password_hash, check_password_hash

st.set_page_config(
    page_title="Sales dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= DATABASE CONNECTION =====================
# ── Connect to PostgreSQL using your existing config ──
# Reads DATABASE_URL from .streamlit/secrets.toml
# @st.cache_resource = create connection ONCE, reuse forever
@st.cache_resource(show_spinner="Connecting to database...")
def get_engine():
    db_url = st.secrets["DATABASE_URL"]
    # Add timeout and keepalive to help with proxy issues
    if "?" not in db_url:
        db_url += "?connect_timeout=20&keepalives=1&keepalives_idle=30"
    else:
        db_url += "&connect_timeout=20&keepalives=1&keepalives_idle=30"
        
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=5,
        max_overflow=10
    )
    return engine

engine = get_engine()

with engine.connect() as conn:
    db.metadata.create_all(engine)
    print("Tables checked/created")

# ====================== SESSION STATE ======================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""

# ====================== LOGIN & REGISTRATION ======================
def login_page():
    st.title("🔐 Login to SalesPulse")
    username = st.text_input("Username", value="admin")
    password = st.text_input("Password", type="password", value="admin123")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Login", type="primary", use_container_width=True):
            with engine.connect() as conn:
                user_row = conn.execute(text("""
                    SELECT id, username, password_hash
                    FROM users
                    WHERE username = :username
                """), {"username": username}).fetchone()
                
                if user_row:
                    user = User()
                    user.password_hash = user_row.password_hash
                    if user.check_password(password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.rerun()

             # Fallback for defauld admin           
            if username == "admin" and password == "admin123":
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
                
            st.error("Invalid username or password / try using admin | admin123")

            
    with col2:
        if st.button("Register New User", use_container_width=True):
            st.session_state.show_register = True
            st.rerun()
            
    # Registration Form
    if st.session_state.get("show_register"):
        st.subheader("Create New Account")
        reg_username = st.text_input("New Username")
        reg_email = st.text_input("Email")
        reg_password = st.text_input("New Password", type="password")
        
        if st.button("Create Account"):
            if reg_username and reg_email and reg_password:
                try:
                    with engine.begin() as conn:
                        hashed = generate_password_hash(reg_password)
                        conn.execute(text("""
                            INSERT INTO users (username, email, password_hash, created_at)
                            VALUES (:username, :email, :password_hash, :created_at)
                        """), {
                            "username": reg_username,
                            "email": reg_email,
                            "password_hash": hashed,
                            "created_at":datetime.utcnow()
                        })
                    st.success("✅ Account created successfully! for **{reg_username}**! You can now login.")
                    st.session_state.show_register = False
                    st.rerun()
                except Exception as e:
                    error_str = str(e).lower()
                    if "unique" in error_str or "duplicate" in error_str:
                        st.error("❌ Username or email already exists. Please choose a different one.")
                    else:
                        st.error(f"❌ Registration failed: {str(e)}")
            else:
                st.error("Please fill all fields")

if not st.session_state.authenticated:
    login_page()
    st.stop()

# ==================== DATA LOADING =======================
# ── Load sales data (reuse your SQL from analytics_routes) ──
# @st.cache_data(ttl=600) = cache for 10 mins, then refresh
@st.cache_data(ttl=300)
def load_sales():
    with engine.connect() as conn:
        df = pd.read_sql(text("""
            SELECT
                s.id,
                s.quantity,
                s.total,
                s.sale_date,
                s.region,
                p.name     AS product_name,
                p.category,
                p.price
            FROM sales s
            JOIN products p ON s.product_id = p.id
            ORDER BY s.sale_date DESC
        """), conn)
        df["sale_date"] = pd.to_datetime(df["sale_date"], errors='coerce')
        df = df.dropna(subset=["sale_date"])
    return df


@st.cache_data(ttl=300)
def load_products():
    with engine.connect() as conn:
        df = pd.read_sql(text(
            "SELECT * FROM products ORDER BY name"
        ), conn)
    return df

# Load raw data once
df_raw = load_sales()

if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.rerun()

# =========================== SIDEBAR FILTERS =====================
with st.sidebar:
    st.title("⚡ SalesPulse")
    st.success(f"Logged in as: {st.session_state.username}** | 2,000 records loaded")
    # st.markdown(f"**Logged in as:** {st.session_state.username}")
    st.markdown("---")

    # ── Date range picker ────────────────────────────────
    st.subheader("Date Range")
    # Safe code - handles missing NaT dates
    valid_dates = df_raw["sale_date"].dropna()

    if len(valid_dates) == 0:
        st.error("No valid dates found in the data!")
        st.stop()
        
    min_d = valid_dates.min().date()
    max_d = valid_dates.max().date()
    
    date_range = st.date_input(
        "Select period",
        value=(min_d, max_d),
        min_value=min_d,
        max_value=max_d
    )

    # ── Category dropdown ────────────────────────────────
    st.subheader("Category")
    cats = ["All"] + sorted(df_raw["category"].unique().tolist())
    sel_cat = st.selectbox("Filter category", cats)

    # ── Region dropdown ──────────────────────────────────
    st.subheader("Region")
    regs = ["All"] + sorted(
        df_raw["region"].dropna().unique().tolist()
    )
    sel_reg = st.selectbox("Filter region", regs)
    st.markdown("---")

# ================= APPLY FILTERS to dataframe ======================
df = df_raw.copy()
if len(date_range) == 2:
    s, e = date_range
    df = df[(df["sale_date"].dt.date >= s) &
            (df["sale_date"].dt.date <= e)]
if sel_cat != "All":
    df = df[df["category"] == sel_cat]
if sel_reg != "All":
    df = df[df["region"] == sel_reg]

st.sidebar.metric("Matching records", f"{len(df):,}")

# ==================== DASHBOARD ==========================
st.title("📊 Analytics Dashboard")
st.caption(f"Logged in as: **{st.session_state.username}** | Showing {len(df):,} records loaded")
st.markdown("---")


# ================= Calculate KPI numbers =========================
total_rev  = df["total"].sum()
total_ord  = len(df)
avg_order  = df["total"].mean() if len(df) > 0 else "$0"
num_prods  = df["product_name"].nunique()

# =============== KPI CARDS side by side ========================
st.subheader("Key Metrics")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        label="Total Revenue",
        value=f"${total_rev:,.0f}",
        delta="vs last period"
    )
with c2:
    st.metric(
        label="Total Orders",
        value=f"{total_ord:,}"
    )
with c3:
    st.metric(
        label="Avg Order Value",
        value=f"${avg_order:,.0f}" 
    )
with c4:
    st.metric(
        label="Products",
        value=f"{num_prods:,}"
    )


# ==================== CHARTS ==============================
st.markdown("---")
col_a, col_b = st.columns([2, 1])   # line gets 2x width

with col_a:
    st.subheader("Monthly Revenue")
    df["month"] = df["sale_date"].dt.to_period("M").astype(str)
    monthly = (df.groupby("month")["total"]
                 .sum().reset_index()
                 .rename(columns={"total": "revenue"}))

    if len(monthly) > 0:
        fig_line = px.line(
            monthly, x="month", y="total",
            markers=True,
            line_shape="spline",          # smooth curves
            title="Monthly Revenue Trend",
            color_discrete_sequence=["#00d4ff"]
        )
        fig_line.update_layout(
            height=400,
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis_tickformat="$,.0f",
            xaxis_title="Month",
            yaxis_title="Revenue"
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")
        

with col_b:
    st.subheader("Sales by Category")
    cat_rev = (df.groupby("category")["total"]
                 .sum().reset_index()
                 .sort_values("total", ascending=False))
    if len(cat_rev) > 0:
        fig_donut = px.pie(
            cat_rev, values="total", names="category",
            hole=0.65,                      # 70% hole = donut
            color_discrete_sequence=[
                "#00d4ff","#a855f7","#10b981",
                "#f59e0b","#f43f5e","#6366f1"
            ]
        )
        fig_donut.update_traces(
            textinfo="percent+label",
            textposition="inside"
        )
        fig_donut.update_layout(
            height=400,
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False
        )
        st.plotly_chart(fig_donut, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")
# ===================== RECENT SALES ========================
# data table + advanced SQL tabs
st.markdown("---")
st.subheader("Recent Sales")

search = st.text_input("Search product name",
                        placeholder="Type to filter...")
disp = df.copy()
if search:
    disp = disp[disp["product_name"]
                .str.contains(search, case=False, na=False)]

st.dataframe(
    disp[["product_name","category",
          "quantity","total",
          "sale_date","region"]].head(100),
    use_container_width=True, hide_index=True
)
st.download_button("Export CSV",
    disp.to_csv(index=False), "sales.csv", "text/csv")

# ================ ADVANCED ANALYTICS ===========================
st.markdown("---")
st.subheader("Advanced Analytics")
tab1, tab2, tab3 = st.tabs(["Window Functions",
                             "Monthly Growth CTE",
                             "Regional Bar"])

with tab1:    # RANK() window function
    with engine.connect() as conn:
        ranked = pd.read_sql(text("""
            SELECT p.name, p.category,
                   SUM(s.total) AS revenue,
                   RANK() OVER (
                     PARTITION BY p.category
                     ORDER BY SUM(s.total) DESC
                   ) AS rank_in_category
            FROM products p
            JOIN sales s ON p.id = s.product_id
            GROUP BY p.name, p.category
            ORDER BY p.category, rank_in_category
        """), conn)
    st.dataframe(ranked, use_container_width=True,
                 hide_index=True)

with tab2:    # CTE with LAG() for month-over-month growth
    with engine.connect() as conn:
        growth = pd.read_sql(text("""
            WITH monthly AS (
              SELECT DATE_TRUNC('month', sale_date) AS month,
                     SUM(total) AS revenue
              FROM sales GROUP BY month
            )
            SELECT month, revenue,
              ROUND((revenue
                - LAG(revenue) OVER (ORDER BY month))
                / LAG(revenue) OVER (ORDER BY month)*100,2
              ) AS growth_pct
            FROM monthly ORDER BY month
        """), conn)
    st.dataframe(growth,use_container_width=True,
                 hide_index=True)

with tab3:    # bar chart by region
    rdata = (df.groupby("region")["total"]
               .sum().reset_index()
               .sort_values("total", ascending=False))
    if len(rdata) > 0:
        fig_bar = px.bar(rdata, x="region", y="total", title="Revenue by Region"
        color_discrete_sequence=["#a855f7"])
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

if len(df)==0:
    st.warning("⚠️ No data found for the selected filters. Please change the date range or filters.")
    st.stop()
# ================== MANAGE PRODUCTS =======================
# product CRUD (Create + Delete)
st.markdown("---")
st.subheader("Manage Products")

tab_view, tab_add, tab_del = st.tabs([
    "View Products", "Add Product", "Delete Product"
])

with tab_view:
    prods = pd.read_sql(text("SELECT * FROM products ORDER BY name"), engine)
    st.dataframe(prods, use_container_width=True,
                 hide_index=True)

with tab_add:
    st.write("Add a new product to the database")
    name  = st.text_input("Product name")
    cat   = st.text_input("Category")
    price = st.number_input("Price ($)", min_value=0.0, step=0.01)
    stock = st.number_input("Stock quantity",
                             min_value=0, step=1)

    if st.button("Add Product"):
        if name and cat:
            with engine.begin() as conn:
                conn.execute(text("""
                    INSERT INTO products (name, category, price, stock)
                    VALUES (:name, :cat, :price, :stock)
                """), {"name": name, "cat": cat,
                           "price": price, "stock": stock})
                conn.commit()
            st.success(f"✅ Added '{name}' successfully!")
            st.cache_data.clear()  # refresh cached data
            st.rerun()             # reload the page
        else:
            st.error("Please fill in name and category")

with tab_del:
    prods2 = load_products()
    prod_names = prods2["name"].tolist()
    to_delete = st.selectbox("Select product to delete",
                              prod_names)
    if st.button("Delete Product", type="primary"):
        with engine.connect() as conn:
            conn.execute(text(
                "DELETE FROM products WHERE name = :name"
            ), {"name": to_delete})
            conn.commit()
        st.success(f"Deleted '{to_delete}'")
        st.cache_data.clear()
        st.rerun()
