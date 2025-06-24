import face_recognition
import os
import sys

def load_known_faces(photos_folder):
    known_encodings = []
    known_names = []

    for filename in os.listdir(photos_folder):
        filepath = os.path.join(photos_folder, filename)
        image = face_recognition.load_image_file(filepath)
        encodings = face_recognition.face_encodings(image)

        if encodings:
            known_encodings.append(encodings[0])
            known_names.append(os.path.splitext(filename)[0])  # remove .jpg/.png
        else:
            print(f"⚠️ Warning: No face found in {filename}, skipping.")

    return known_encodings, known_names


def recognize_face(test_image_path, known_encodings, known_names):
    image = face_recognition.load_image_file(test_image_path)
    test_encodings = face_recognition.face_encodings(image)

    if not test_encodings:
        print("❌ No face found in the input image.")
        return

    test_encoding = test_encodings[0]

    # Compare with known faces
    results = face_recognition.compare_faces(known_encodings, test_encoding)

    for i, match in enumerate(results):
        if match:
            print(f"✅ Match Found: {known_names[i]}")
            return

    print("❌ No Match Found")


if __name__ == "__main__":
    # Take input as a command line argument
    if len(sys.argv) < 2:
        print("Usage: python app.py <test_image_path>")
        sys.exit(1)

    test_image_path = sys.argv[1]
    photos_folder = "PHOTOS"

    if not os.path.exists(test_image_path):
        print(f"❌ Error: File '{test_image_path}' does not exist.")
        sys.exit(1)

    known_encodings, known_names = load_known_faces(photos_folder)
    recognize_face(test_image_path, known_encodings, known_names)

