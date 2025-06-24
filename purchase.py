import os
import json
import random
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load env
load_dotenv()
DATABASE_URL = os.getenv('POSTGRES_URL')
DATABASE_NAME = 'return_wo_receipt'

def get_connection():
    db_url = DATABASE_URL.replace(DATABASE_URL.split('/')[-1], DATABASE_NAME)
    return psycopg2.connect(db_url)

def create_purchases_table():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS purchases (
            id SERIAL PRIMARY KEY,
            photo_id VARCHAR(255),
            items JSONB NOT NULL,
            total DECIMAL(10, 2) NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        print("✅ Purchases table created successfully.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print("❌ Error creating purchases table:", e)

def generate_random_timestamp():
    now = datetime.now()
    three_months_ago = now - timedelta(days=90)
    random_offset = timedelta(days=random.randint(0, 90), hours=random.randint(0, 23), minutes=random.randint(0, 59))
    return three_months_ago + random_offset

def insert_dummy_purchases():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        purchases = [
            # Karthik (4)
            ("face1.jpg", [{"name": "Apple iPhone 14", "price": 999.99}], 999.99),
            ("face1.jpg", [{"name": "AirPods Pro", "price": 249.99}, {"name": "Apple Watch Series 8", "price": 399.99}], 649.98),
            ("face1.jpg", [{"name": "Google Pixel 7", "price": 599.99}], 599.99),
            ("face1.jpg", [{"name": "Bluetooth Speaker", "price": 89.99}, {"name": "VR Headset", "price": 399.99}], 489.98),

            # Arjun (3)
            ("face2.jpg", [{"name": "Dell XPS 13", "price": 1099.99}], 1099.99),
            ("face2.jpg", [{"name": "JBL Flip 6", "price": 129.99}, {"name": "Logitech MX Master 3", "price": 99.99}], 229.98),
            ("face2.jpg", [{"name": "Streaming Device", "price": 99.99}], 99.99),

            # Priya (3)
            ("face3.jpg", [{"name": "Smart TV 55\"", "price": 799.99}], 799.99),
            ("face3.jpg", [{"name": "Kindle Paperwhite", "price": 139.99}, {"name": "Echo Dot", "price": 49.99}], 189.98),
            ("face3.jpg", [{"name": "Fitbit Charge 5", "price": 179.99}], 179.99)
        ]

        insert_query = """
            INSERT INTO purchases (photo_id, items, total, timestamp)
            VALUES (%s, %s, %s, %s)
        """

        for photo_id, items, total in purchases:
            timestamp = generate_random_timestamp()
            cursor.execute(insert_query, (
                photo_id,
                json.dumps(items),
                total,
                timestamp
            ))

        conn.commit()
        print(f"✅ Inserted {len(purchases)} dummy purchases with random timestamps.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print("❌ Error inserting dummy purchases:", e)

if __name__ == "__main__":
    create_purchases_table()
    insert_dummy_purchases()
