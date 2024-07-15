from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import pandas as pd
import datetime
import os
import base64
import cv2
import numpy as np
from main1 import detect_and_register
from generate_insights import generate_insights

app = Flask(__name__)

# Load the existing data
excel_file_path = "car_plate_data.xlsx"
analysis_dir = "graphs"

def load_data():
    try:
        df = pd.read_excel(excel_file_path)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["NumberPlate", "Date", "Time"])
    return df

def save_data(df):
    temp_excel_file_path = "temp_car_plate_data.xlsx"
    df.to_excel(temp_excel_file_path, index=False)
    os.replace(temp_excel_file_path, excel_file_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        number_plate = request.form['number_plate']
        current_datetime = datetime.datetime.now()
        current_date = current_datetime.strftime("%Y-%m-%d")
        current_time = current_datetime.strftime("%H:%M:%S")

        df = load_data()
        new_entry = pd.DataFrame({"NumberPlate": [number_plate], "Date": [current_date], "Time": [current_time]})
        df = pd.concat([df, new_entry], ignore_index=True)
        save_data(df)

        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/detect', methods=['POST'])
def detect():
    image_data = request.form['image_data']
    image_data = base64.b64decode(image_data.split(',')[1])
    nparr = np.frombuffer(image_data, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    detected_plates = detect_and_register(frame)
    
    if not detected_plates:
        return jsonify({"status": "error", "message": "No valid number plates detected"})

    detected_number_plate = detected_plates[0]  # Use the first detected plate for this example
    
    df = load_data()
    current_datetime = datetime.datetime.now()
    current_date = current_datetime.strftime("%Y-%m-%d")
    current_time = current_datetime.strftime("%H:%M:%S")

    if detected_number_plate in df['NumberPlate'].values:
        # Number plate already registered
        return jsonify({"status": "existing", "message": "Number plate already registered"})
    else:
        # Register the new vehicle
        new_entry = pd.DataFrame({"NumberPlate": [detected_number_plate], "Date": [current_date], "Time": [current_time]})
        df = pd.concat([df, new_entry], ignore_index=True)
        save_data(df)
        
        # Generate insights after registering a new vehicle
        generate_insights(excel_file_path, analysis_dir)

        return jsonify({"status": "new", "message": "Number plate registered successfully"})

@app.route('/parking')
def parking():
    return render_template('parking.html')

@app.route('/graph', methods=['GET', 'POST'])
def graph():
    if request.method == 'POST':
        date = request.form['date']
        return redirect(url_for('show_graph', date=date))
    return render_template('graph.html')

@app.route('/analysis/<date>.png')
def show_graph(date):
    file_path = os.path.join(analysis_dir, f'{date}.png')
    if os.path.exists(file_path):
        return send_from_directory(analysis_dir, f'{date}.png')
    else:
        return f"No graph available for {date}", 404

@app.route('/aboutus')
def about_us():
    return render_template('aboutus.html')

if __name__ == "__main__":
    app.run(debug=True)
