import cv2
import pandas as pd
from ultralytics import YOLO
import numpy as np
import pytesseract
from datetime import datetime
import re
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

model = YOLO('best.pt')

def RGB(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        point = [x, y]
        print(point)

cv2.namedWindow('RGB')
cv2.setMouseCallback('RGB', RGB)

cap = cv2.VideoCapture("test_videos\license_plate.mp4")

my_file = open("coco1.txt", "r")
data = my_file.read()
class_list = data.split("\n")

area = [(50,276), (36,387), (985,382), (938,267)]
#area = [(35, 375), (16, 456), (1015, 451), (965, 378)]
count = 0
processed_numbers = set()

excel_file_path = "car_plate_data.xlsx"
temp_excel_file_path = "temp_car_plate_data.xlsx"

try:
    df = pd.read_excel(excel_file_path, engine='openpyxl')
except FileNotFoundError:
    df = pd.DataFrame(columns=["NumberPlate", "Date", "Time", "IN", "OUT", "Match"])

def clean_number_plate(text):
    cleaned_text = re.sub(r'[^A-Za-z0-9]', '', text)
    if 7 <= len(cleaned_text) <= 10:
        return cleaned_text
    return None

def is_valid_plate(text):
    if len(text) > 3 and any(char.isdigit() for char in text):
        return True
    return False

while True:
    ret, frame = cap.read()
    count += 1
    if count % 3 != 0:
        continue
    if not ret:
        break

    frame = cv2.resize(frame, (1020, 500))
    results = model.predict(frame)
    a = results[0].boxes.data
    px = pd.DataFrame(a).astype("float")

    for index, row in px.iterrows():
        x1 = int(row[0])
        y1 = int(row[1])
        x2 = int(row[2])
        y2 = int(row[3])

        d = int(row[5])
        c = class_list[d]
        cx = int(x1 + x2) // 2
        cy = int(y1 + y2) // 2
        result = cv2.pointPolygonTest(np.array(area, np.int32), ((cx, cy)), False)
        if result >= 0:
            crop = frame[y1:y2, x1:x2]
            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            gray = cv2.bilateralFilter(gray, 15, 17, 17)

            text = pytesseract.image_to_string(gray).strip()
            text = text.replace('(', '').replace(')', '').replace(',', '').replace(']', '').replace('!', '').replace('"', '')
            cleaned_text = clean_number_plate(text)
            print(cleaned_text)
            if cleaned_text and cleaned_text not in processed_numbers and is_valid_plate(cleaned_text):
                processed_numbers.add(cleaned_text)
                current_datetime = datetime.now()
                current_date = current_datetime.strftime("%Y-%m-%d")
                current_time = current_datetime.strftime("%H:%M:%S")

                plate_entries = df[df["NumberPlate"] == cleaned_text]
                in_count = plate_entries["IN"].sum()
                out_count = plate_entries["OUT"].sum()
                is_in = in_count <= out_count

                match = cleaned_text in df['NumberPlate'].values

                new_entry = pd.DataFrame({
                    "NumberPlate": [cleaned_text],
                    "Date": [current_date],
                    "Time": [current_time],
                    "IN": [is_in],
                    "OUT": [not is_in],
                    "Match": [match]
                })

                df = pd.concat([df, new_entry], ignore_index=True)
                df.to_excel(temp_excel_file_path, index=False, engine='openpyxl')
                os.replace(temp_excel_file_path, excel_file_path)

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.imshow('crop', crop)

    cv2.polylines(frame, [np.array(area, np.int32)], True, (255, 0, 0), 2)
    cv2.imshow("RGB", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
