from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
from dotenv import load_dotenv
import base64
import uuid
import json
import face_recognition
from datetime import datetime
from flask import send_from_directory

app = Flask(__name__)
CORS(app)
load_dotenv()

LAST_RETURN_RESULT = {}

DATABASE_URL = os.getenv('POSTGRES_URL')
DATABASE_NAME = 'return_wo_receipt'
PHOTOS_FOLDER = 'PHOTOS'

def get_connection():
    db_url = DATABASE_URL.replace(DATABASE_URL.split('/')[-1], DATABASE_NAME)
    return psycopg2.connect(db_url)

def load_known_faces():
    known_encodings = []
    known_names = []
    for filename in os.listdir(PHOTOS_FOLDER):
        path = os.path.join(PHOTOS_FOLDER, filename)
        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_encodings.append(encodings[0])
            known_names.append(os.path.splitext(filename)[0])
        else:
            print(f"⚠️ No face in {filename}, skipping.")
    return known_encodings, known_names

# Load face encodings once when the server starts
KNOWN_ENCODINGS, KNOWN_NAMES = load_known_faces()

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price FROM products ORDER BY id")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        products = [{"id": r[0], "name": r[1], "price": float(r[2])} for r in rows]
        return jsonify(products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/purchase", methods=["POST"])
def handle_purchase():
    data = request.get_json()
    image_base64 = data.get("image")
    items = data.get("items")
    total = data.get("total")
    timestamp = data.get("timestamp", datetime.now().isoformat())

    if not image_base64 or not items or not total:
        return jsonify(success=False, message="Missing data"), 400

    try:
        header, encoded = image_base64.split(",", 1)
        image_bytes = base64.b64decode(encoded)
        temp_path = "temp.jpg"
        with open(temp_path, "wb") as f:
            f.write(image_bytes)

        test_img = face_recognition.load_image_file(temp_path)
        test_encodings = face_recognition.face_encodings(test_img)

        if not test_encodings:
            return jsonify(success=False, message="No face found."), 400

        test_encoding = test_encodings[0]
        results = face_recognition.compare_faces(KNOWN_ENCODINGS, test_encoding)

        photo_id = None
        for i, match in enumerate(results):
            if match:
                photo_id = f"{KNOWN_NAMES[i]}.jpg"
                break

        if not photo_id:
            photo_id = str(uuid.uuid4())[:8]
            new_path = os.path.join(PHOTOS_FOLDER, f"{photo_id}.jpg")
            with open(new_path, "wb") as f:
                f.write(image_bytes)

        conn = get_connection()
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO purchases (photo_id, items, total, timestamp)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            photo_id,
            json.dumps(items),
            total,
            timestamp
        ))
        conn.commit()
        cursor.close()
        conn.close()

        os.remove(temp_path)
        return jsonify(success=True, photo_id=photo_id)

    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

@app.route("/api/return", methods=["POST"])
def handle_return():
    data = request.get_json()
    image_base64 = data.get("image")

    if not image_base64:
        return jsonify(success=False, message="Missing image"), 400

    try:
        header, encoded = image_base64.split(",", 1)
        image_bytes = base64.b64decode(encoded)
        temp_path = "temp_return.jpg"
        with open(temp_path, "wb") as f:
            f.write(image_bytes)

        test_img = face_recognition.load_image_file(temp_path)
        test_encodings = face_recognition.face_encodings(test_img)

        if not test_encodings:
            return jsonify(success=False, message="No face found."), 400

        test_encoding = test_encodings[0]
        results = face_recognition.compare_faces(KNOWN_ENCODINGS, test_encoding)

        photo_id = None
        for i, match in enumerate(results):
            if match:
                photo_id = f"{KNOWN_NAMES[i]}.jpg"
                break

        os.remove(temp_path)

        if not photo_id:
            return jsonify(success=False, message="No match found")

        # Fetch user's purchases
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, items, total, timestamp FROM purchases WHERE photo_id = %s ORDER BY timestamp DESC", (photo_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        purchases = [{
            "id": r[0],
            "items": r[1] if isinstance(r[1], list) else json.loads(r[1]),
            "total": float(r[2]),
            "timestamp": r[3].isoformat()
        } for r in rows]
        print(purchases)
        global LAST_RETURN_RESULT
        LAST_RETURN_RESULT = {
            "photo_id": photo_id,
            "purchases": purchases
        }
        return jsonify(success=True)


    except Exception as e:
        print(e)
        return jsonify(success=False, message=str(e)), 500

@app.route("/api/return_result", methods=["GET"])
def get_last_return_result():
    if not LAST_RETURN_RESULT:
        return jsonify(success=False, message="No result found"), 404

    return jsonify(
        success=True,
        photo_id=LAST_RETURN_RESULT["photo_id"],
        photo_url=f"http://localhost:5000/photos/{LAST_RETURN_RESULT['photo_id']}",
        purchases=LAST_RETURN_RESULT["purchases"]
    )
@app.route('/photos/<filename>')
def get_photo(filename):
    return send_from_directory(PHOTOS_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
