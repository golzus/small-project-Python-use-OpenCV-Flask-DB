from flask import Flask, request, redirect, url_for, render_template
import os
import cv2
import pathlib
from pymongo import MongoClient

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# חיבור ל-MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['mydatabase']
collection = db['users']

# בדוק אם התיקייה 'static/uploads' קיימת, ואם לא, צור אותה
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


@app.route("/")
def home():
    # מציג את הדף הראשי
    return render_template("welcome.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = request.form.get('register_firstname')
        lastname = request.form.get('register_lastname')
        password = request.form.get('register_password')

        # בדוק אם כל הערכים קיימים
        if not firstname or not lastname or not password:
            return 'Missing fields', 400

        # הוספת המשתמש למסד הנתונים
        user = {"firstname": firstname, "lastname": lastname, "password": password}
        collection.insert_one(user)
        # הפניה לדף הכניסה
        return redirect(url_for('login'))
    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        firstname = request.form.get('login_firstname')
        password = request.form.get('login_password')

        # בדיקת פרטי המשתמש במסד הנתונים
        user = collection.find_one({"firstname": firstname, "password": password})

        if user:
            return redirect(url_for('analyzeImage'))
        else:
            return 'Login failed: Invalid credentials', 401
    return render_template("login.html")


@app.route('/analyzeImage', methods=['GET', 'POST'])
def analyzeImage():
    if request.method == 'POST':
        # בדוק אם קובץ הועלה
        if 'file' not in request.files:
            return render_template('analyzeImage.html', message="No file part")
        file = request.files['file']
        # בדוק אם יש שם לקובץ
        if file.filename == '':
            return render_template('analyzeImage.html', message="No selected file")
        if file:
            # שמור את הקובץ בתיקייה המתאימה
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            print(f"File saved at: {filepath}")  # הדפסת נתיב הקובץ שנשמר

            # עיבוד התמונה לזיהוי פרצופים
            num_faces, processed_image_path = process_image(filepath)

            # הצג את התמונה המעובדת ומספר הפנים שנמצאו
            return render_template('analyzeImage.html',
                                   filename=filename,
                                   num_faces=num_faces,
                                   processed_image_path=processed_image_path)
    # אם השיטה היא GET או אם אין קובץ, הצג את הטופס להעלאת קובץ
    return render_template('analyzeImage.html', filename=None, num_faces=None, processed_image_path=None)


def process_image(image_path):
    # וודא שהנתיב לקובץ ה-cascade נכון
    cascader_file = str(pathlib.Path(__file__).parent / "haarcascade_frontalface_default.xml")

    # בדוק אם קובץ ה-cascade נטען כראוי
    if not os.path.exists(cascader_file):
        raise FileNotFoundError(f"The cascade file {cascader_file} does not exist.")

    faceCascade = cv2.CascadeClassifier(cascader_file)

    # טען את התמונה
    print(f"Loading image from path: {image_path}")  # הדפסת נתיב התמונה לטעינה
    image = cv2.imread(image_path)

    # בדוק אם התמונה נטענה כראוי
    if image is None:
        raise ValueError(f"Image at path {image_path} could not be loaded.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    # צייר ריבוע סביב הפנים שנמצאו
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # שמור את התמונה המעובדת
    processed_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'processed_' + os.path.basename(image_path))
    cv2.imwrite(processed_image_path, image)

    return len(faces), processed_image_path


if __name__ == '__main__':
    app.run(debug=True)