import signal
import threading
from flask import Flask, request, redirect, url_for, render_template
import os
import cv2
import pathlib
from pymongo import MongoClient
import sys
import webbrowser
import pandas as pd
import openpyxl
import threading

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
    print("Home page loaded")
    return render_template("welcome.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    print("Entering register function")
    if request.method == 'POST':
        print("POST request received")
        firstname = request.form.get('register_firstname')
        lastname = request.form.get('register_lastname')
        password = request.form.get('register_password')
        gender = request.form.get('register_gender')
        print(f"Received data - Firstname: {firstname}, Lastname: {lastname}, Password: {password}, Gender: {gender}")

        # בדוק אם כל הערכים קיימים
        if not firstname or not lastname or not password:
            print("Missing fields")
            return 'Missing fields', 400

        print("Adding user to database")
        user = {"firstname": firstname, "lastname": lastname, "password": password,"gender":gender}
        collection.insert_one(user)

        # עדכון קובץ ה-Excel
        file_path = 'static/excelsFiles/excelCountGenerally.xlsx'
        df = pd.read_excel(file_path)
        if gender == 'male':
            df.iloc[0, 1]=df.iloc[0, 1]+1
        elif gender == 'female':
            df.iloc[0, 2]=df.iloc[0, 2]+1
        elif gender == 'child':
            df.iloc[0, 3]=df.iloc[0, 3]+1
        df.to_excel(file_path, index=False)
        print("Excel file updated")

        return redirect(url_for('login'))

    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Login page loaded")
    if request.method == 'POST':
        firstname = request.form.get('login_firstname')
        password = request.form.get('login_password')
        print(f"Login attempt - Firstname: {firstname}, Password: {password}")

        user = collection.find_one({"firstname": firstname, "password": password})
        if user:
            print("Login successful")
            return redirect(url_for('analyzeImage'))
        else:
            print("Login failed")
            return render_template("login.html", error="Login failed: Invalid credentials")

    return render_template("login.html")


@app.route('/logout')
def logout():
    print("User logged out")
    return render_template("logout.html")


    # הפנייה לדף logout שמבצע סגירה של הדפדפן
    return render_template('logout.html')
@app.route('/analyzeImage', methods=['GET', 'POST'])
def analyzeImage():
    print("Analyze Image page loaded")
    if request.method == 'POST':
        print("POST request received for image upload")
        if 'file' not in request.files:
            print("No file part in request")
            return render_template('analyzeImage.html', message="No file part")
        file = request.files['file']
        if file.filename == '':
            print("No selected file")
            return render_template('analyzeImage.html', message="No selected file")
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            print(f"File saved at: {filepath}")

            num_faces, processed_image_path = process_image(filepath)
            return render_template('analyzeImage.html', filename=filename, num_faces=num_faces,
                                   processed_image_path=processed_image_path)

    return render_template('analyzeImage.html', filename=None, num_faces=None, processed_image_path=None)


def process_image(image_path):
    print(f"Processing image at path: {image_path}")
    cascader_file = str(pathlib.Path(__file__).parent / "haarcascade_frontalface_default.xml")
    if not os.path.exists(cascader_file):
        raise FileNotFoundError(f"The cascade file {cascader_file} does not exist.")

    faceCascade = cv2.CascadeClassifier(cascader_file)
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Image at path {image_path} could not be loaded.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30),
                                         flags=cv2.CASCADE_SCALE_IMAGE)
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    processed_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'processed_' + os.path.basename(image_path))
    cv2.imwrite(processed_image_path, image)
    print(f"Processed image saved at: {processed_image_path}")
    return len(faces), processed_image_path

@app.route('/view_charts')
def view_charts():
    return redirect("http://127.0.0.1:8050/")

if __name__ == '__main__':
    print("Starting Flask application")
    app.run(debug=True)
