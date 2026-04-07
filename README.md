# SalesPulse - Advanced-Full-Stack-Data-Dashboard
 Advanced Full-Stack Data Dashboard With Use Of Python + Flask + SQLAlchemy + PostgreSQL

## ✨ Features

- **Secure User Authentication** (Login + Registration)
- **Real-time Data Filters** (Date range, Category, Region)
- **Key Performance Indicators (KPIs)**
- **Interactive Charts** (Monthly Revenue, Category Donut, Regional Bar)
- **Advanced SQL Analytics**
  - Window Functions (Ranking)
  - CTEs with Month-over-Month Growth
- **CRUD Operations** (View, Add, Delete Products)
- **Fully Responsive Dark Theme**
- **Live Deployment** on Streamlit Cloud

## 🛠️ Technologies & Tools Used

| Technology              | Purpose                              | Website |
|------------------------|--------------------------------------|--------|
| **Streamlit**          | Frontend & Dashboard Framework      | [streamlit.io](https://streamlit.io) |
| **SQLAlchemy**         | ORM & Database Toolkit              | [sqlalchemy.org](https://www.sqlalchemy.org) |
| **PostgreSQL**         | Database                            | [postgresql.org](https://www.postgresql.org) |
| **Supabase**           | Hosted PostgreSQL Database          | [supabase.com](https://supabase.com) |
| **Pandas**             | Data Manipulation                   | [pandas.pydata.org](https://pandas.pydata.org) |
| **Plotly**             | Interactive Charts                  | [plotly.com](https://plotly.com/python/) |
| **Werkzeug**           | Password Hashing                    | Part of Flask ecosystem |
| **psycopg2**           | PostgreSQL Adapter                  | - |
| **Streamlit Cloud**    | Free Hosting & Deployment           | [share.streamlit.io](https://share.streamlit.io) |


## 🚀 Live Demo

**[View Live Dashboard](https://advanced-full-stack-data-dashboard-n5jrorajjmwewnq2nav8qc.streamlit.app/)** 

## 📸 Screenshots

 ### Login and Registration
  ![Login Page] (https://github.com/yashraj022381/Advanced-Full-Stack-Data-Dashboard/commit/f62ab6f9fab952e7ddb8359fef142ae5cd5300fd#diff-18719e7b510d599d72804f20f808324a35ea250ac0a08a7a1e83f339ed8d9ac7)
  
  ![Register Page] (screenshots/20260407_165848.jpg)

 ### Main Dashboard
  ![Analytics Dashboard] (screenshots/20260407_170053.jpg)

 ### Charts
  ![Monthly Revenue & Sales by Category] (screenshots/20260407_170455.jpg)

 ### Advanced Features
  ![Advanced Analytics] (screenshots/20260407_171118.jpg)
  
  ![Recent Sales] (screenshots/20260407_170913.jpg)
                  (screenshots/20260407_171011.jpg)

  ![Manage Products] (screenshots/20260407_171427.jpg)
                     (screenshots/20260407_171519.jpg)
                     (screenshots/20260407_171614.jpg)
                     (screenshots/20260407_171706.jpg)
                     
## 🗄️ Database

- Hosted on **Supabase** (PostgreSQL)
- Two main tables: `products` & `sales`
- Complex queries using JOINs, Window Functions, and CTEs

## 🛠️ How to Run Locally

 ### 1. Clone the Repository
   git clone https://github.com/yourusername/salespulse-dashboard.git
   cd salespulse-dashboard

 ### 2. Create Virtual Environment
   python -m venv venv
   venv\Scripts\activate    # Windows
   # source venv/bin/activate  # Mac/Linux

 ### 3. Install Dependencies
   pip install -r requirements.txt

 ### 4. Setup Secrets
   Create folder .streamlit/ and file secrets.toml:
    DATABASE_URL = "postgresql://your_user:your_password@your_host:6543/your_db"

 ### 5. Run the App
   streamlit run streamlit_app.py

🌐 Deployment
   Deployed using Streamlit Community Cloud + Supabase (Session Pooler - Port 6543).

📂 Project Structure
    ├── streamlit_app.py          # Main Dashboard
    ├── models.py                 # SQLAlchemy Models
    ├── requirements.txt
    ├── .streamlit/
    │   └── secrets.toml          # Database credentials (git ignored)
    ├── reset_users.py            # Utility to clear users table
    └── README.md

🔮 Future Enhancements (Planned)

  - User Profile Management
  - Export to CSV/Excel
  - Dark/Light Mode Toggle
  - Advanced Search & Pagination
  - Email Notifications

📄 License
  This project is open-source and free to use.
