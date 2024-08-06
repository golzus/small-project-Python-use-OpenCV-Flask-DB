import cv2
import mediapipe as mp
import numpy as np
import pymongo
from pymongo import MongoClient

# הגדרת היכולות של Mediapipe לזיהוי פנים
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# חיבור ל-MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['face_recognition']
collection = db['users']

def save_user_to_db(user_id, user_name, face_encoding):
    """
    שמור את המידע של המשתמש במסד הנתונים.
    :param user_id: מזהה המשתמש.
    :param user_name: שם המשתמש.
    :param face_encoding: קידוד הפנים של המשתמש.
    """
    collection.insert_one({"user_id": user_id, "user_name": user_name, "face_encoding": face_encoding.tolist()})

def get_user_from_db(user_id):
    """
    קבל את פרטי המשתמש לפי מזהה המשתמש.
    :param user_id: מזהה המשתמש.
    :return: מידע על המשתמש אם נמצא, אחרת None.
    """
    return collection.find_one({"user_id": user_id})

def capture_face():
    """
    תפוס תמונה מהמצלמה ונתח אותה לזיהוי פנים.
    :return: קידוד הפנים אם זוהתה פנים, אחרת None.
    """
    # אתחול של זיהוי הפנים
    with mp_face_detection.FaceDetection(min_detection_confidence=0.7) as face_detection:
        while True:
            # קריאת פריים מהמצלמה
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame.")
                break

            # עיבוד התמונה
            frame = cv2.flip(frame, 1)  # היפוך התמונה אופקית
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # המרת התמונה ל-RGB
            results = face_detection.process(frame_rgb)  # עיבוד התמונה לזיהוי פנים

            if results.detections:
                for detection in results.detections:
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = frame.shape  # קבלת גובה ורוחב התמונה
                    bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
                    cv2.rectangle(frame, bbox, (0, 255, 0), 2)  # ציור מלבן סביב הפנים

                    # קטע הפנים מתוך התמונה
                    face_image = frame[bbox[1]:bbox[1] + bbox[3], bbox[0]:bbox[0] + bbox[2]]

                    # ודא שהתמונה לא ריקה
                    if face_image.size == 0:
                        print("Captured face image is empty.")
                        continue

                    # שינוי גודל התמונה לקידוד
                    face_image_resized = cv2.resize(face_image, (100, 100))
                    face_encoding = np.array(face_image_resized).flatten()  # קידוד הפנים

                    # הצגת התמונה
                    cv2.imshow('Camera Preview', frame)

                    return face_encoding

            # הצגת התמונה
            cv2.imshow('Camera Preview', frame)

            # יציאה מהתוכנית אם נלחץ מקש ESC
            key = cv2.waitKey(1)
            if key == 27:  # ESC key to exit
                break
            elif key == ord('q'):  # 'q' key to quit
                break

    return None

def register_user():
    """
    רישום משתמש חדש עם שם, מזהה ותמונה.
    """
    user_name = input("Enter your name: ")  # קלט שם המשתמש
    user_id = input("Enter your ID: ")  # קלט מזהה המשתמש
    face_encoding = capture_face()  # קלט את תמונת הפנים

    if face_encoding is not None:
        save_user_to_db(user_id, user_name, face_encoding)  # שמור את המידע במסד הנתונים
        print(f"User {user_name} with ID {user_id} registered successfully.")
    else:
        print("Failed to capture face.")

def login_user():
    """
    התחברות למערכת לפי צילום פנים.
    """
    user_data = None
    face_encoding = capture_face()  # קלט את תמונת הפנים

    if face_encoding is not None:
        # השווה את הפנים עם כל הפנים המאוחסנות
        for user in collection.find():
            saved_encoding = np.array(user['face_encoding'])
            if np.linalg.norm(face_encoding - saved_encoding) < 10000:  # השווה את הקידודים
                user_data = user
                break

    if user_data is not None:
        print(f"Welcome back, {user_data['user_name']}!")  # ברוך הבא למשתמש
    else:
        print("Face not recognized.")
        manual_login()  # אם הפנים לא מזוהות, עבור לכניסה ידנית

def manual_login():
    """
    אפשרות כניסה ידנית עם מזהה בלבד.
    """
    user_id = input("Enter your ID: ")  # קלט מזהה המשתמש
    user_data = get_user_from_db(user_id)  # קבל את פרטי המשתמש לפי מזהה

    if user_data is None:
        print("User not found.")  # המשתמש לא נמצא במסד הנתונים
    else:
        print(f"Welcome back, {user_data['user_name']}!")  # ברוך הבא למשתמש

# אתחול מצלמה
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    cap.release()
    cv2.destroyAllWindows()
    client.close()
    exit()

# הגדרות המצלמה
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# תפריט ראשי
while True:
    print("1. Register")
    print("2. Login")
    print("3. Exit")
    choice = input("Choose an option: ")

    if choice == '1':
        register_user()  # קריאה לפונקציה לרישום משתמש
    elif choice == '2':
        login_user()  # קריאה לפונקציה לכניסה
    elif choice == '3':
        break  # יציאה מהתוכנית
    else:
        print("Invalid choice. Please try again.")  # בחירה לא חוקית

# שחרור המצלמה וסגירת כל החלונות
cap.release()
cv2.destroyAllWindows()
client.close()
