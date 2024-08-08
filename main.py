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

import webbrowser
from flask import Flask
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import graph
import colorsChart as bar_graph
import general_pie_chart
import graphPerAge as line_chart

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

# @app.route('/view_charts')
# def view_charts():
#     return redirect("http://127.0.0.1:8050/")


def load_data(file_path):
    return pd.read_excel(file_path, engine='openpyxl')

def calculate_metrics(df):
    total_people = df.iloc[0, 0]
    avg_people = df.iloc[0, 1]
    max_people_hour = df.iloc[0, 2]
    return total_people, avg_people, max_people_hour

# ודא שכל הנתיבים לקבצים נכונים
df = load_data('static/excelsFiles/excelLoadsPerHours.xlsx')
column_names = df.columns[1:]
bar_df = load_data('static/excelsFiles/excelLoadsColors.xlsx')
count_people_df = load_data('static/excelsFiles/excelCountPeople.xlsx')
general_pie_df = load_data('static/excelsFiles/excelCountGenerally.xlsx')

# בדיקה אם כל קובץ נטען בהצלחה
print(df.head())
print(bar_df.head())
print(count_people_df.head())
print(general_pie_df.head())

total_people, avg_people, max_people_hour = calculate_metrics(count_people_df)

def create_layout():
    return html.Div(
        className='main-container',
        children=[
            html.Div(
                className='header-container',
                children=[
                    html.Div(
                        className='metric-container',
                        children=[
                            html.Div('# of Visitors', className='metric-title'),
                            html.Div(f'{total_people:.1f}k', className='metric-value')
                        ]
                    ),
                    html.Div(
                        className='metric-container',
                        children=[
                            html.Div('Avg Duration People', className='metric-title'),
                            html.Div(f'{avg_people:.2f}', className='metric-value')
                        ]
                    ),
                    html.Div(
                        className='metric-container',
                        children=[
                            html.Div('Max Visitors/Hour', className='metric-title'),
                            html.Div(f'{max_people_hour:.1f}k', className='metric-value')
                        ]
                    ),
                ]
            ),
            html.Div(
                className='charts-container',
                children=[
                    dcc.Graph(id='pie-selection', className='pie-chart'),
                    dcc.Graph(id='bar-chart', className='bar-chart'),
                    dcc.Graph(id='general-pie-chart', className='general-pie-chart'),
                ]
            ),
            html.Div(
                className='bottom-charts-container',
                children=[
                    dcc.Graph(id='line-chart', figure=line_chart.create_line_chart(), className='line-chart'),
                    html.Div(html.Img(src='/assets/defaultImage.jpg', className='image'), className='image-container'),
                ]
            )
        ]
    )

server = Flask(__name__)
app = dash.Dash(__name__, server=server, url_base_pathname='/')

app.layout = create_layout()

@app.callback(
    [Output('pie-selection', 'figure'),
     Output('bar-chart', 'figure'),
     Output('general-pie-chart', 'figure')],
    [Input('pie-selection', 'clickData')]
)
def update_graphs(clickData):
    selected_categories = column_names.tolist()
    if clickData:
        selected_categories = [clickData['points'][0]['label']]

    pie_fig = graph.create_graph(selected_categories)
    bar_fig = bar_graph.create_bar_chart(bar_df)
    general_pie_fig = general_pie_chart.create_general_pie_chart(general_pie_df)
    return pie_fig, bar_fig, general_pie_fig

@app.route('/view_charts')
def view_charts():
    return redirect('/dash/')

if __name__ == '__main__':
    print("Starting Flask application")
    app.run(debug=True)

if __name__ == '__main__':
    print("Starting Flask application")
    app.run(debug=True)
