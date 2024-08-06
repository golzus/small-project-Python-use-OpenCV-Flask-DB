import cv2
import mediapipe as mp
import numpy as np
import pymongo
from pymongo import MongoClient

# הגדרת היכולות של Mediapipe
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# חיבור ל-MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['face_recognition']
collection = db['users']

def save_user_to_db(user_id, user_name, face_encoding):
    collection.insert_one({"user_id": user_id, "user_name": user_name, "face_encoding": face_encoding.tolist()})

def get_user_from_db(user_id):
    return collection.find_one({"user_id": user_id})

# פתח את המצלמה
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# הגדרות המצלמה
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

def capture_face():
    with mp_face_detection.FaceDetection(min_detection_confidence=0.7) as face_detection:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame.")
                break

            # עיבוד התמונה
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_detection.process(frame_rgb)

            if results.detections:
                for detection in results.detections:
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = frame.shape
                    bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
                    cv2.rectangle(frame, bbox, (0, 255, 0), 2)

                    # קטע הפנים מתוך התמונה
                    face_image = frame[bbox[1]:bbox[1] + bbox[3], bbox[0]:bbox[0] + bbox[2]]

                    # הוסף טקסט על התמונה
                    cv2.putText(frame, 'Detected Face', (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                    # המרת הפנים לקידוד בגודל קבוע
                    face_image_resized = cv2.resize(face_image, (100, 100))
                    face_encoding = np.array(face_image_resized).flatten()

                    # הצג את התמונה
                    cv2.imshow('Camera Preview', frame)

                    return face_encoding

            # הצג את התמונה
            cv2.imshow('Camera Preview', frame)

            # הוסף תנאי יציאה מהתוכנית אם לא קיבלת תמונה
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
    user_id = input("Enter your ID: ")
    user_data = get_user_from_db(user_id)

    if user_data is None:
        print("User not found.")
        return

    face_encoding = capture_face()
    if face_encoding is not None:
        saved_encoding = np.array(user_data['face_encoding'])
        if np.linalg.norm(face_encoding - saved_encoding) < 10000:  # Threshold can be adjusted
            print(f"Welcome back, {user_data['user_name']}!")
        else:
            print("Face does not match.")
    else:
        print("Failed to capture face.")

# תפריט ראשי
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
