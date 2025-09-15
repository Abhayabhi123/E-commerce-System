"""
Streamlit E-Commerce Management System
Features:
- MySQL-backed products, orders, customers
- Firebase Authentication (pyrebase) for customer login/registration
- Admin area (MySQL admins table)
- Shopping cart stored in st.session_state

Files: single-file Streamlit app. Update DB and Firebase configs before running.

Requirements:
pip install streamlit mysql-connector-python pyrebase4

Firebase setup notes (brief):
- Create a Firebase project at https://console.firebase.google.com
- Enable Email/Password sign-in (Authentication > Sign-in method)
- Copy Firebase web config (apiKey, authDomain, databaseURL, projectId, storageBucket, messagingSenderId, appId)
- Optionally, create a service account JSON if you want admin SDK (not required for pyrebase usage below)

MySQL setup:
- Run the SQL in `setup_db_sql()` helper or execute provided setup_db.sql in MySQL to create tables.

"""

import streamlit as st
import mysql.connector
import hashlib
import json
from typing import List, Dict

# third-party: pyrebase for Firebase Auth + Realtime DB
try:
    import pyrebase
except Exception as e:
    st.warning("pyrebase not installed. Install with: pip install pyrebase4")
    raise

# ---------------------- Configuration (UPDATE THESE) ----------------------
# MySQL connection config
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "ecommerce_db"
}

# Firebase web config (replace with your project's config)
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyCMkf_IevjfwHE9JiLG3qknt56g-Y8zS_E",
    "authDomain": "streamlitecommerce.firebaseapp.com",
     "databaseURL": "https://streamlitecommerce-default-rtdb.asia-southeast1.firebasedatabase.app/",
    "projectId": "streamlitecommerce",
    "storageBucket": "streamlitecommerce.firebasestorage.app",
    "messagingSenderId": "702149505114",
    "appId": "1:702149505114:web:98cfbd6b97faac20902863",
    "measurementId": "G-8P2QMQL67F"
}
# --------------------------------------------------------------------------

# ---------------------- Helpers: MySQL Connection -------------------------
def get_connection():
    return mysql.connector.connect(**MYSQL_CONFIG)

# simple hashing for admin password storage/check in MySQL (customers use Firebase Auth)
def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

# Setup DB helper: runs CREATE TABLE statements if needed
def setup_db_sql():
    sql = """
    CREATE DATABASE IF NOT EXISTS ecommerce_db;
    USE ecommerce_db;

    CREATE TABLE IF NOT EXISTS admins (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100) UNIQUE,
        password VARCHAR(255)
    );

    CREATE TABLE IF NOT EXISTS products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(200),
        description TEXT,
        price DECIMAL(10,2),
        stock INT
    );

    CREATE TABLE IF NOT EXISTS orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        customer_email VARCHAR(200),
        total DECIMAL(10,2),
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS order_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        order_id INT,
        product_id INT,
        quantity INT,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    );
    """

    conn = mysql.connector.connect(host=MYSQL_CONFIG['host'], user=MYSQL_CONFIG['user'], password=MYSQL_CONFIG['password'])
    cursor = conn.cursor()
    for stmt in sql.split(';'):
        stmt = stmt.strip()
        if stmt:
            cursor.execute(stmt)
    conn.commit()
    cursor.close()
    conn.close()

# ---------------------- Firebase Init -----------------------------------
firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
fb_auth = firebase.auth()
fb_db = firebase.database()

# ---------------------- Streamlit UI & Logic -----------------------------
st.set_page_config(page_title="E-Commerce System ", layout="wide")

if 'cart' not in st.session_state:
    st.session_state.cart = []  # list of dicts: {id,name,price,quantity}

if 'user' not in st.session_state:
    st.session_state.user = None  # Firebase user dict

# Utility functions

def fetch_products() -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return items


def add_product_mysql(name, description, price, stock):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, description, price, stock) VALUES (%s,%s,%s,%s)",
                   (name, description, price, stock))
    conn.commit()
    cursor.close()
    conn.close()


def update_product_mysql(pid, name, description, price, stock):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET name=%s, description=%s, price=%s, stock=%s WHERE id=%s",
                   (name, description, price, stock, pid))
    conn.commit()
    cursor.close()
    conn.close()


def delete_product_mysql(pid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=%s", (pid,))
    conn.commit()
    cursor.close()
    conn.close()


def place_order_mysql(customer_email, cart_items):
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (customer_email, total) VALUES (%s,%s)", (customer_email, total))
    order_id = cursor.lastrowid
    for it in cart_items:
        cursor.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s,%s,%s)",
                       (order_id, it['id'], it['quantity']))
        cursor.execute("UPDATE products SET stock = stock - %s WHERE id=%s", (it['quantity'], it['id']))
    conn.commit()
    cursor.close()
    conn.close()
    return order_id, float(total)

# ---------------------- Layout -------------------------------------------
st.title(" E-Commerce Management System ")

menu = st.sidebar.selectbox("Go to", ["Home", "Shop", "Cart", "Orders", "Admin", "Setup DB"])

if menu == "Setup DB":
    st.header("Database Setup")
    st.write("This will create necessary MySQL tables if they do not exist.")
    if st.button("Run DB Setup"):
        try:
            setup_db_sql()
            st.success("✅ Database setup completed.\nTip: insert an admin account using the Admin panel or SQL.")
        except Exception as e:
            st.error(f"Error: {e}")

# ---------------------- Authentication ----------------------------------
with st.sidebar.expander("Customer Authentication", expanded=True):
    if st.session_state.user:
        st.write(f"Signed in as: {st.session_state.user.get('email')}")
        if st.button("Sign out"):
            st.session_state.user = None
            st.success("Signed out")
    else:
        auth_mode = st.radio("Action", ["Login", "Register"], index=0)
        email = st.text_input("Email", key="email_input")
        password = st.text_input("Password", type="password", key="pw_input")
        if auth_mode == "Register":
            if st.button("Register"):
                try:
                    user = fb_auth.create_user_with_email_and_password(email, password)
                    # optionally store profile in Realtime DB
                    fb_db.child("users").child(user['localId']).set({"email": email})
                    st.success("Registration successful. You can now log in.")
                except Exception as e:
                    st.error(f"Registration failed: {e}")
        else:
            if st.button("Login"):
                try:
                    user = fb_auth.sign_in_with_email_and_password(email, password)
                    info = fb_auth.get_account_info(user['idToken'])
                    st.session_state.user = {"email": email, "id": user['localId'], "idToken": user['idToken']}
                    st.success(f"Logged in as {email}")
                except Exception as e:
                    st.error(f"Login failed: {e}")

# ---------------------- Home --------------------------------------------
if menu == "Home":
    st.header("Welcome")


# ---------------------- Shop --------------------------------------------
if menu == "Shop":
    st.header("Shop — Products")
    products = fetch_products()
    cols = st.columns(3)
    for i, p in enumerate(products):
        with cols[i % 3]:
            st.subheader(p['name'])
            st.write(p.get('description',''))
            st.write(f"Price: ₹{p['price']} | Stock: {p['stock']}")
            qty = st.number_input(f"Qty - {p['id']}", min_value=1, max_value=int(p['stock']) if p['stock']>0 else 1, value=1, key=f"qty_{p['id']}")
            if st.button(f"Add to cart - {p['id']}", key=f"add_{p['id']}"):
                if p['stock']>=qty:
                    st.session_state.cart.append({
                        'id': p['id'], 'name': p['name'], 'price': float(p['price']), 'quantity': int(qty)
                    })
                    st.success(f"Added {qty} x {p['name']} to cart")
                else:
                    st.error("Insufficient stock")

# ---------------------- Cart --------------------------------------------
if menu == "Cart":
    st.header("Your Cart")
    cart = st.session_state.cart
    if not cart:
        st.info("Cart is empty — go to Shop to add items.")
    else:
        total = 0.0
        for idx, it in enumerate(cart):
            st.write(f"{it['quantity']} x {it['name']} — ₹{it['price']} each = ₹{it['quantity']*it['price']}")
            if st.button(f"Remove {it['id']}", key=f"rem_{it['id']}"):
                st.session_state.cart.pop(idx)
                st.experimental_rerun()
            total += it['quantity']*it['price']
        st.write(f"**Total: ₹{total}**")

        if st.button("Place Order"):
            if not st.session_state.user:
                st.error("You must be logged in (customer) to place an order.")
            else:
                try:
                    order_id, order_total = place_order_mysql(st.session_state.user['email'], cart)
                    # push order backup to Firebase Realtime DB
                    fb_db.child('orders').child(str(order_id)).set({
                        'customer_email': st.session_state.user['email'],
                        'total': order_total,
                        'items': cart
                    })
                    st.success(f"Order placed! Order ID: {order_id}")
                    st.session_state.cart = []
                except Exception as e:
                    st.error(f"Failed to place order: {e}")

# ---------------------- Orders (Customer view) --------------------------
if menu == "Orders":
    st.header("Your Orders")
    if not st.session_state.user:
        st.info("Log in to view your orders.")
    else:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM orders WHERE customer_email=%s ORDER BY order_date DESC", (st.session_state.user['email'],))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        if not rows:
            st.info("No orders found")
        else:
            for r in rows:
                st.write(f"Order #{r['id']} — ₹{r['total']} — {r['order_date']}")
                # fetch items
                conn = get_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT oi.quantity, p.name FROM order_items oi JOIN products p ON oi.product_id=p.id WHERE oi.order_id=%s", (r['id'],))
                items = cursor.fetchall()
                cursor.close()
                conn.close()
                for it in items:
                    st.write(f"- {it['quantity']} x {it['name']}")

# ---------------------- Admin -------------------------------------------
if menu == "Admin":
    st.header("Admin Dashboard")

    admin_login = st.expander("Admin Login / Create", expanded=True)
    with admin_login:
        a_user = st.text_input("Admin username", key="admin_user")
        a_pw = st.text_input("Admin password", type="password", key="admin_pw")
        if st.button("Admin Login"):
            try:
                conn = get_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM admins WHERE username=%s AND password=%s", (a_user, hash_pw(a_pw)))
                ad = cursor.fetchone()
                cursor.close()
                conn.close()
                if ad:
                    st.session_state.admin = ad
                    st.success("Admin logged in")
                else:
                    st.error("Invalid admin credentials")
            except Exception as e:
                st.error(f"Error: {e}")
        if st.button("Create Admin (danger)"):
            # cautionary: create an admin with hashed password
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO admins (username, password) VALUES (%s,%s)", (a_user, hash_pw(a_pw)))
                conn.commit()
                cursor.close()
                conn.close()
                st.success("Admin account created")
            except Exception as e:
                st.error(f"Failed to create admin: {e}")

    if 'admin' in st.session_state:
        st.subheader("Inventory — Manage Products")
        # Add product
        with st.form("add_prod"):
            name = st.text_input("Name")
            desc = st.text_area("Description")
            price = st.number_input("Price", min_value=0.0, format="%.2f")
            stock = st.number_input("Stock", min_value=0, step=1)
            submitted = st.form_submit_button("Add Product")
            if submitted:
                try:
                    add_product_mysql(name, desc, price, stock)
                    st.success("Product added")
                except Exception as e:
                    st.error(f"Error: {e}")

        # List and update/delete
        prods = fetch_products()
        for p in prods:
            with st.expander(f"{p['name']} — Stock: {p['stock']}"):
                st.write(p.get('description',''))
                new_name = st.text_input("Name", value=p['name'], key=f"name_{p['id']}")
                new_desc = st.text_area("Desc", value=p.get('description',''), key=f"desc_{p['id']}")
                new_price = st.number_input("Price", value=float(p['price']), key=f"price_{p['id']}")
                new_stock = st.number_input("Stock", value=int(p['stock']), key=f"stock_{p['id']}")
                if st.button("Update", key=f"up_{p['id']}"):
                    try:
                        update_product_mysql(p['id'], new_name, new_desc, new_price, new_stock)
                        st.success("Updated")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                if st.button("Delete", key=f"del_{p['id']}"):
                    try:
                        delete_product_mysql(p['id'])
                        st.success("Deleted")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

        st.subheader("Sales — Recent Orders")
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM orders ORDER BY order_date DESC LIMIT 50")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        for r in rows:
            st.write(f"Order #{r['id']} — {r['customer_email']} — ₹{r['total']} — {r['order_date']}")


