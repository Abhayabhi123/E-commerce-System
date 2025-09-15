from auth import register_customer, login_customer, login_admin
from user import browse_products, place_order
from cart import add_to_cart, view_cart, cart
from admin import add_product, update_product, delete_product, view_sales

def customer_menu(customer):
    while True:
        print("\n--- Customer Menu ---")
        print("1. Browse Products")
        print("2. Add to Cart")
        print("3. View Cart")
        print("4. Place Order")
        print("5. Logout")
        choice = input("Enter choice: ")

        if choice == "1":
            browse_products()
        elif choice == "2":
            pid = int(input("Enter Product ID: "))
            qty = int(input("Enter Quantity: "))
            add_to_cart(pid, qty)
        elif choice == "3":
            view_cart()
        elif choice == "4":
            place_order(customer['id'], cart)
        elif choice == "5":
            break

def admin_menu():
    while True:
        print("\n--- Admin Menu ---")
        print("1. Add Product")
        print("2. Update Product")
        print("3. Delete Product")
        print("4. View Sales")
        print("5. Logout")
        choice = input("Enter choice: ")

        if choice == "1":
            n = input("Product Name: ")
            p = float(input("Price: "))
            s = int(input("Stock: "))
            add_product(n, p, s)
        elif choice == "2":
            pid = int(input("Product ID: "))
            p = float(input("New Price: "))
            s = int(input("New Stock: "))
            update_product(pid, p, s)
        elif choice == "3":
            pid = int(input("Product ID: "))
            delete_product(pid)
        elif choice == "4":
            view_sales()
        elif choice == "5":
            break

if __name__ == "__main__":
    while True:
        print("\n=== E-Commerce System ===")
        print("1. Register")
        print("2. Customer Login")
        print("3. Admin Login")
        print("4. Exit")
        ch = input("Enter choice: ")

        if ch == "1":
            n = input("Name: ")
            e = input("Email: ")
            p = input("Password: ")
            register_customer(n, e, p)
        elif ch == "2":
            e = input("Email: ")
            p = input("Password: ")
            user = login_customer(e, p)
            if user:
                print(f"✅ Welcome {user['name']}!")
                customer_menu(user)
            else:
                print("❌ Invalid credentials.")
        elif ch == "3":
            u = input("Admin Username: ")
            p = input("Password: ")
            admin = login_admin(u, p)
            if admin:
                print("✅ Admin login successful!")
                admin_menu()
            else:
                print("❌ Invalid admin credentials.")
        elif ch == "4":
            break
