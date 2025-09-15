from db_config import get_connection

def browse_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    print("\n📦 Available Products:")
    for p in products:
        print(f"ID:{p[0]} | {p[1]} | Price: {p[2]} | Stock: {p[3]}")

def place_order(customer_id, cart):
    conn = get_connection()
    cursor = conn.cursor()
    
    total = sum(item['price'] * item['quantity'] for item in cart)
    cursor.execute("INSERT INTO orders (customer_id, total) VALUES (%s, %s)", (customer_id, total))
    order_id = cursor.lastrowid

    for item in cart:
        cursor.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)",
                       (order_id, item['id'], item['quantity']))
        cursor.execute("UPDATE products SET stock=stock-%s WHERE id=%s", (item['quantity'], item['id']))
    
    conn.commit()
    conn.close()
    print("✅ Order placed successfully!")
