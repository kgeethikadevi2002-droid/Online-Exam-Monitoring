import cv2
import os
import time
import numpy as np
from datetime import datetime
from database import log_event, log_violation_with_screenshot

# ========== CONFIG ==========
CANDIDATE_ID = input("Enter Candidate ID: ") # e.g. C101
PHOTO_FOLDER = "violations"
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
FACE_CASCADE = cv2.CascadeClassifier(CASCADE_PATH)

if not os.path.exists(PHOTO_FOLDER):
    os.makedirs(PHOTO_FOLDER)

cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cam.isOpened():
    print("ERROR: Cannot open webcam")
    exit()

# ========== VARIABLES FOR ALL 5 POINTS ==========
face_absent_start_time = None  # 3. Track when absence started
total_absence_duration = 0.0   # 3. Total absence duration
last_status = "Face Detected"  # 2. To log event only once
screenshot_taken = False       # Take 1 screenshot per absence

print(f"Monitoring Started for {CANDIDATE_ID}. Press 'q' to Quit")

while True:
    ret, frame = cam.read()
    if not ret:
        print("Webcam disconnected")
        break

    current_time = time.time()
    time_str = datetime.now().strftime("%H:%M:%S")

    # ========== 1. CONTINUOUS FACE PRESENCE MONITORING ==========
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = FACE_CASCADE.detectMultiScale(gray, 1.3, 5)

    # Default: Not Detected = RED
    status = "Face Not Detected"
    status_color = (0, 0, 255)
    box_color = (0, 0, 255)

    if len(faces) > 0:
        # FACE DETECTED = GREEN
        status = "Face Detected"
        status_color = (0, 255, 0)
        box_color = (0, 255, 0)

        # Draw box around face
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 3)

        # ========== 3. RESET TIMER WHEN FACE RETURNS ==========
        if face_absent_start_time is not None:
            absence_time = current_time - face_absent_start_time
            total_absence_duration += absence_time
            log_event(CANDIDATE_ID, "Face Returned", f"Was absent for {absence_time:.1f} sec")
            print(f"Face Returned. Added {absence_time:.1f}s to total.")
            face_absent_start_time = None
            screenshot_taken = False # reset so we can take screenshot next time

    else:
        # ========== 2. LOG FACE NOT DETECTED EVENT ==========
        if face_absent_start_time is None:
            face_absent_start_time = current_time
            if last_status == "Face Detected": # log only once per absence
                log_event(CANDIDATE_ID, "Face Not Detected", "Candidate face not visible in frame")

        # ========== 3. CALCULATE CURRENT ABSENCE ==========
        current_absence = current_time - face_absent_start_time

        # Take screenshot after 2 seconds of absence
        if current_absence >= 2.0 and screenshot_taken == False:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(PHOTO_FOLDER, f"{CANDIDATE_ID}_ABSENCE_{timestamp}.jpg")
            cv2.imwrite(screenshot_path, frame)
            log_violation_with_screenshot(CANDIDATE_ID, "Absence > 2sec", screenshot_path)
            screenshot_taken = True

    last_status = status

    # ========== 4. DISPLAY REAL-TIME MONITORING INFORMATION ==========
    # Black background bar
    cv2.rectangle(frame, (0, 0), (640, 150), (0, 0, 0), -1)

    # 1. Face Detection Status
    cv2.putText(frame, f"Status: {status}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, status_color, 2)
    # 2. Current Time  
    cv2.putText(frame, f"Time: {time_str}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    # 3. Total Face Absence Duration
    cv2.putText(frame, f"Total Absence: {total_absence_duration:.1f} sec", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    # Extra info
    cv2.putText(frame, f"Candidate: {CANDIDATE_ID}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
    cv2.putText(frame, "Press 'q' to Quit", (450, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    # 1. SHOW LIVE WEBCAM FEED
    cv2.imshow(f"Exam Monitoring - {CANDIDATE_ID}", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        # If quitting while absent, add that last duration
        if face_absent_start_time is not None:
            total_absence_duration += current_time - face_absent_start_time
        log_event(CANDIDATE_ID, "Session Ended", f"Total Absence: {total_absence_duration:.1f} sec")
        break

cam.release()
cv2.destroyAllWindows()
print(f"Session Ended. Final Total Absence: {total_absence_duration:.1f} seconds")