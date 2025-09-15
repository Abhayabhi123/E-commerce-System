from db_config import get_connection

def add_product(name, price, stock):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, price, stock) VALUES (%s, %s, %s)", (name, price, stock))
    conn.commit()
    conn.close()
    print("✅ Product added successfully!")

def update_product(pid, price, stock):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET price=%s, stock=%s WHERE id=%s", (price, stock, pid))
    conn.commit()
    conn.close()
    print("✅ Product updated successfully!")

def delete_product(pid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=%s", (pid,))
    conn.commit()
    conn.close()
    print("✅ Product deleted!")

def view_sales():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    conn.close()
    print("\n📊 Sales Records:")
    for o in orders:
        print(o)
