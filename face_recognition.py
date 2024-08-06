import cv2
import mediapipe as mp
import numpy as np
import pymongo
from pymongo import MongoClient

# Define Mediapipe face detection capabilities
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['face_recognition']
collection = db['users']


def save_user_to_db(user_id, user_name, face_encoding):
    collection.insert_one({"user_id": user_id, "user_name": user_name, "face_encoding": face_encoding.tolist()})


def get_user_from_db(user_id):
    return collection.find_one({"user_id": user_id})


def capture_face():
    with mp_face_detection.FaceDetection(min_detection_confidence=0.7) as face_detection:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame.")
                break

            # Process the image
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_detection.process(frame_rgb)

            if results.detections:
                for detection in results.detections:
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = frame.shape
                    bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
                    cv2.rectangle(frame, bbox, (0, 255, 0), 2)

                    # Extract face from image
                    face_image = frame[bbox[1]:bbox[1] + bbox[3], bbox[0]:bbox[0] + bbox[2]]

                    # Ensure face_image is not empty
                    if face_image.size == 0:
                        print("Captured face image is empty.")
                        continue

                    # Resize face for encoding
                    face_image_resized = cv2.resize(face_image, (100, 100))
                    face_encoding = np.array(face_image_resized).flatten()

                    # Display the image
                    cv2.imshow('Camera Preview', frame)

                    return face_encoding

            # Display the image
            cv2.imshow('Camera Preview', frame)

            # Exit if 'ESC' key is pressed
            key = cv2.waitKey(1)
            if key == 27:  # ESC key to exit
                break
            elif key == ord('q'):  # 'q' key to quit
                break

    return None


def register_user():
    user_name = input("Enter your name: ")
    user_id = input("Enter your ID: ")
    face_encoding = capture_face()

    if face_encoding is not None:
        save_user_to_db(user_id, user_name, face_encoding)
        print(f"User {user_name} with ID {user_id} registered successfully.")
    else:
        print("Failed to capture face.")


def login_user():
    user_data = None
    face_encoding = capture_face()

    if face_encoding is not None:
        # Compare captured face with all stored faces
        for user in collection.find():
            saved_encoding = np.array(user['face_encoding'])
            if np.linalg.norm(face_encoding - saved_encoding) < 10000:  # Threshold can be adjusted
                user_data = user
                break

    if user_data is not None:
        print(f"Welcome back, {user_data['user_name']}!")
    else:
        print("Face not recognized.")
        manual_login()


def manual_login():
    user_id = input("Enter your ID: ")
    user_data = get_user_from_db(user_id)

    if user_data is None:
        print("User not found.")
    else:
        print(f"Welcome back, {user_data['user_name']}!")


# Initialize camera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    cap.release()
    cv2.destroyAllWindows()
    client.close()
    exit()

# Camera settings
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Main menu
while True:
    print("1. Register")
    print("2. Login")
    print("3. Exit")
    choice = input("Choose an option: ")

    if choice == '1':
        register_user()
    elif choice == '2':
        login_user()
    elif choice == '3':
        break
    else:
        print("Invalid choice. Please try again.")

cap.release()
cv2.destroyAllWindows()
client.close()

