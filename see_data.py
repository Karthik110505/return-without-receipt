import psycopg2
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("POSTGRES_URL")
DATABASE_NAME = "return_wo_receipt"

def get_connection():
    db_url = DATABASE_URL.replace(DATABASE_URL.split('/')[-1], DATABASE_NAME)
    return psycopg2.connect(db_url)

def view_products():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products ORDER BY id;")
        rows = cursor.fetchall()

        print("\n📦 PRODUCTS TABLE:")
        print("-" * 50)
        for row in rows:
            print(f"ID: {row[0]:<2} | Name: {row[1]:<30} | Price: ${row[2]:.2f}")

        cursor.close()
        conn.close()
    except Exception as e:
        print("❌ Error reading products:", e)

def view_purchases():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM purchases ORDER BY id;")
        rows = cursor.fetchall()

        print("\n🧾 PURCHASES TABLE:")
        print("-" * 50)
        for row in rows:
            print(f"ID: {row[0]:<2} | Photo ID: {row[1]:<12} | Total: ${row[3]:.2f} | Time: {row[4]}")
            print("Items:")
            items = row[2]
            if isinstance(items, str):
                items = json.loads(items)
            for item in items:
                print(f"  - {item['name']} (${item['price']})")
            print("-" * 50)

        cursor.close()
        conn.close()
    except Exception as e:
        print("❌ Error reading purchases:", e)

if __name__ == "__main__":
    #view_products()
    view_purchases()
