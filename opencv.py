import cv2
import mediapipe

# טען את המודל לזיהוי פנים של OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# פתח את המצלמה
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# הגדרות המצלמה
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    # עיבוד התמונה
    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, 'Detected Face', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # הצג את התמונה
    cv2.imshow('Camera Preview', frame)

    # הוסף תנאי יציאה מהתוכנית אם לא קיבלת תמונה
    key = cv2.waitKey(1)
    if key == 27:  # ESC key to exit
        break
    elif key == ord('q'):  # 'q' key to quit
        break

cap.release()
cv2.destroyAllWindows()
