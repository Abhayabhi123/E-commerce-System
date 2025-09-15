import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",      # your MySQL username
        password="",      # your MySQL password
        database="ecommerce_db"
    )
