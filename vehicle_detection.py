import cv2
import pandas as pd
from ultralytics import YOLO
import numpy as np
import pytesseract
from datetime import datetime
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

model = YOLO('best.pt')

def clean_number_plate(text):
    # Use a regular expression to keep only alphanumeric characters
    return re.sub(r'[^A-Za-z0-9]', '', text)

def is_valid_number_plate(text):
    # Define your criteria for a valid number plate
    if len(text) > 3 and any(char.isdigit() for char in text):
        return True
    return False

def detect_and_register(frame):
    results = model.predict(frame)
    a = results[0].boxes.data
    px = pd.DataFrame(a).astype("float")

    detected_plates = []

    for index, row in px.iterrows():
        x1 = int(row[0])
        y1 = int(row[1])
        x2 = int(row[2])
        y2 = int(row[3])

        crop = frame[y1:y2, x1:x2]
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 15, 17, 17)

        text = pytesseract.image_to_string(gray).strip()
        cleaned_text = clean_number_plate(text)
        if is_valid_number_plate(cleaned_text):
            detected_plates.append(cleaned_text)

    return detected_plates

#Example of how to use this function
if __name__ == "__main__":
    cap = cv2.VideoCapture("mycarplate.mp4")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        detected_plates = detect_and_register(frame)
        print(detected_plates)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    cap.release()
    cv2.destroyAllWindows()