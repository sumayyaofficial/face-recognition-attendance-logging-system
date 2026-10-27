import cv2
import face_recognition
import os
import numpy as np
from datetime import datetime
import csv  # ADDED: To handle Excel/CSV exporting
from Mainapp.models import Employee,Attendance
from django.utils import timezone
# 1. Map your known faces to their designations
employees = Employee.objects.all()
employee_data = {}

for employee in employees:
    employee_data[employee.name.lower()] = {
        "id": employee.id,
        "name": employee.name,
        "designation": employee.designation
    }

KNOWN_FACES_DIR = "known_faces"
known_face_encodings = []
known_face_names = []

# Keep track of who we have already logged so we don't spam the list
logged_faces = set()

print("Loading known faces...")
for filename in os.listdir(KNOWN_FACES_DIR):
    if filename.endswith(('.jpg', '.jpeg', '.png')):
        image_path = os.path.join(KNOWN_FACES_DIR, filename)
        image = face_recognition.load_image_file(image_path)
        
        try:
            encoding = face_recognition.face_encodings(image)[0]
            known_face_encodings.append(encoding)
            name = os.path.splitext(filename)[0]
            known_face_names.append(name)
        except IndexError:
            print(f"Warning: No face found in {filename}")

print(f"Loaded {len(known_face_names)} known faces.")
print("\n" + "="*65)
print(f"{'NAME':<20} | {'DESIGNATION':<20} | {'TIME DETECTED'}")
print("="*65)

# --- EXCEL / CSV EXPORT SETUP ---
# Create a filename with today's date
today_date = datetime.now().strftime("%Y-%m-%d")
csv_filename = f"detection_log_{today_date}.csv"

# Open the file in 'append' mode so we don't overwrite previous sessions today
csv_file = open(csv_filename, mode='a', newline='')
csv_writer = csv.writer(csv_file)

# If the file is brand new/empty, write the column headers at the top
if os.stat(csv_filename).st_size == 0:
    csv_writer.writerow(["Name", "Designation", "Time Detected"])
# --------------------------------

# Start webcam
video_capture = cv2.VideoCapture(0)

while True:
    ret, frame = video_capture.read()
    
    # Shrink frame for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    
    # Find faces
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
    
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Scale box back up
        top *= 4; right *= 4; bottom *= 4; left *= 4
        
        # Stricter tolerance for better accuracy
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.45)
        
        # Set strict defaults for unknown faces
        employee = Employee.objects.filter(
            name__iexact=name
        ).first()

        if employee:
            designation = employee.designation
        else:
            designation = "Visitor"

        # LOGGING TO THE TERMINAL AND EXCEL FILE
        
        today = timezone.localdate()

        already_marked = Attendance.objects.filter(
            employee=employee,
            detected_at__date=today
        ).exists()

        # Dynamic colors: Green for known, Red for unknown
        box_color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
        text_color = (0, 0, 0) if name != "Unknown" else (255, 255, 255)

        # DISPLAY ON THE VIDEO FEED
        display_text = f"{name.title()} - {designation}"
        
        # Draw box and label
        cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
        cv2.rectangle(frame, (left, bottom - 35), (right + 120, bottom), box_color, cv2.FILLED)
        cv2.putText(frame, display_text, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, text_color, 1)

    cv2.imshow('Face Recognition', frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up resources when the script ends
video_capture.release()
cv2.destroyAllWindows()
csv_file.close() # Safely close the Excel log file
