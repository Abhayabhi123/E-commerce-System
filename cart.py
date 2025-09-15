from db_config import get_connection

cart = []

def add_to_cart(product_id, quantity):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products WHERE id=%s", (product_id,))
    product = cursor.fetchone()
    conn.close()
    
    if product and product['stock'] >= quantity:
        cart.append({
            "id": product['id'],
            "name": product['name'],
            "price": product['price'],
            "quantity": quantity
        })
        print(f"🛒 Added {quantity} x {product['name']} to cart.")
    else:
        print("❌ Product not available or insufficient stock.")

def view_cart():
    print("\n🛍️ Your Cart:")
    for item in cart:
        print(f"{item['quantity']} x {item['name']} = ₹{item['price']*item['quantity']}")
