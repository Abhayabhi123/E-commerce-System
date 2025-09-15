import hashlib
from db_config import get_connection

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_customer(name, email, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO customers (name, email, password) VALUES (%s, %s, %s)",
                       (name, email, hash_password(password)))
        conn.commit()
        print("✅ Registration successful!")
    except Exception as e:
        print("❌ Error:", e)
    finally:
        conn.close()

def login_customer(email, password):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customers WHERE email=%s AND password=%s",
                   (email, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user

def login_admin(username, password):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM admins WHERE username=%s AND password=%s", (username, password))
    admin = cursor.fetchone()
    conn.close()
    return admin
