import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv('POSTGRES_URL')
DATABASE_NAME = 'return_wo_receipt'

def create_database_and_table():
    try:
        # Connect to PostgreSQL server (without specifying database)
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        try:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(DATABASE_NAME)
            ))
            print(f"Database '{DATABASE_NAME}' created successfully!")
        except psycopg2.errors.DuplicateDatabase:
            print(f"Database '{DATABASE_NAME}' already exists.")
        
        cursor.close()
        conn.close()
        
        # Connect to the specific database
        db_url = DATABASE_URL.replace(DATABASE_URL.split('/')[-1], DATABASE_NAME)
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Create products table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            price DECIMAL(10, 2) NOT NULL
        );
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        print("Products table created successfully!")
        
        # Sample data (40 items)
        products_data = [
            ("Apple iPhone 14", 999.99),
            ("Samsung Galaxy S23", 899.99),
            ("MacBook Pro", 1299.99),
            ("Dell XPS 13", 1099.99),
            ("AirPods Pro", 249.99),
            ("Sony WH-1000XM4", 349.99),
            ("iPad Air", 599.99),
            ("Surface Pro 9", 999.99),
            ("Nintendo Switch", 299.99),
            ("PlayStation 5", 499.99),
            ("Xbox Series X", 499.99),
            ("Apple Watch Series 8", 399.99),
            ("Samsung Galaxy Watch", 329.99),
            ("Google Pixel 7", 599.99),
            ("OnePlus 11", 699.99),
            ("Kindle Paperwhite", 139.99),
            ("Echo Dot", 49.99),
            ("Google Nest Hub", 99.99),
            ("Fitbit Charge 5", 179.99),
            ("Garmin Forerunner", 249.99),
            ("Canon EOS R5", 3899.99),
            ("Sony A7 IV", 2499.99),
            ("GoPro Hero 11", 399.99),
            ("DJI Mini 3", 759.99),
            ("Bose QuietComfort", 329.99),
            ("JBL Flip 6", 129.99),
            ("Anker PowerCore", 49.99),
            ("Logitech MX Master 3", 99.99),
            ("Razer DeathAdder V3", 89.99),
            ("Mechanical Keyboard", 149.99),
            ("4K Monitor", 399.99),
            ("Webcam HD", 79.99),
            ("USB-C Hub", 59.99),
            ("Wireless Charger", 39.99),
            ("Bluetooth Speaker", 89.99),
            ("Gaming Headset", 199.99),
            ("VR Headset", 399.99),
            ("Smart TV 55\"", 799.99),
            ("Streaming Device", 99.99),
            ("Coffee Maker", 149.99)
        ]
        
        # Insert sample data
        insert_query = "INSERT INTO products (name, price) VALUES (%s, %s)"
        cursor.executemany(insert_query, products_data)
        conn.commit()
        print(f"Inserted {len(products_data)} products successfully!")
        
        # Verify data insertion
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        print(f"Total products in database: {count}")
        
        # Display first 5 products
        cursor.execute("SELECT * FROM products LIMIT 5")
        products = cursor.fetchall()
        print("\nFirst 5 products:")
        for product in products:
            print(f"ID: {product[0]}, Name: {product[1]}, Price: ${product[2]}")
        
        cursor.close()
        conn.close()
        print("\nDatabase setup completed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")

def view_all_products():
    """Function to view all products in the database"""
    try:
        db_url = DATABASE_URL.replace(DATABASE_URL.split('/')[-1], DATABASE_NAME)
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM products ORDER BY id")
        products = cursor.fetchall()
        
        print(f"\nAll Products ({len(products)} items):")
        print("-" * 50)
        for product in products:
            print(f"ID: {product[0]:<3} | Name: {product[1]:<25} | Price: ${product[2]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error viewing products: {e}")

if __name__ == "__main__":
    # Create database and populate with data
    create_database_and_table()
    
    # Uncomment the line below if you want to view all products
    # view_all_products()