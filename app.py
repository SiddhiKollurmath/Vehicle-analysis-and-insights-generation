from flask import Flask, render_template, jsonify, request, redirect, url_for, send_from_directory
import pandas as pd
import os
from subprocess import call

app = Flask(__name__)

UPLOAD_FOLDER = 'static/upload'
excel_file_path = 'car_plate_data.xlsx'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
graph_dir = 'graphs'

PARKING_CAPACITY = 30

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def load_data():
    try:
        df = pd.read_excel(excel_file_path, engine='openpyxl')
    except FileNotFoundError:
        df = pd.DataFrame(columns=["NumberPlate", "Date", "Time", "IN", "OUT", "Match"])
    return df

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['video']
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        try:
            file.save(file_path)
            # Run the main1.py script with the uploaded video
            call(["python", "main1.py", file_path])
            return jsonify({"status": "success", "message": "Video uploaded and processed successfully"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    else:
        return jsonify({"status": "error", "message": "No file provided"})

@app.route('/results')
def results():
    df = load_data()
    plates_data = df[['NumberPlate', 'Date', 'Time', 'IN', 'OUT', 'Match']].to_dict(orient='records')
    return render_template('results.html', plates=plates_data)

@app.route('/graphs/<date>.png')
def show_graph(date):
    file_path = os.path.join(graph_dir, f'{date}.png')
    if os.path.exists(file_path):
        return send_from_directory(graph_dir, f'{date}.png')
    else:
        return f"No graph available for {date}", 404

@app.route('/registration')
def registration():
    return render_template('registration.html')

@app.route('/parking_status')
def parking_status():
    df = load_data()
    df = df.sort_values(by=['NumberPlate', 'Date', 'Time']).drop_duplicates(subset='NumberPlate', keep='last')
    cars_inside = df[df['IN'] == True].shape[0]
    available_slots = max(0, PARKING_CAPACITY - cars_inside)
    return render_template('parking_status.html', available_slots=available_slots, total_capacity=PARKING_CAPACITY)

@app.route('/analysis')
def vehicleanalysis():
    return render_template('vehicleanalysis.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/graph', methods=['GET', 'POST'])
def graph():
    if request.method == 'POST':
        date = request.form.get('date')
        return redirect(url_for('show_graph', date=date))
    return render_template('graph.html')

if __name__ == '__main__':
    app.run(debug=True)
