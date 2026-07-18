import cv2
import os
import time
import numpy as np
from datetime import datetime
from database import log_event, log_violation_with_screenshot

PHOTO_FOLDER = "photos"
VIOLATION_FOLDER = "violations"
FACE_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
FACE_CASCADE = cv2.CascadeClassifier(FACE_CASCADE_PATH)

def capture_photo(candidate_id):
    if FACE_CASCADE.empty():
        return None, f"ERROR: Cascade not found"

    if not os.path.exists(PHOTO_FOLDER):
        os.makedirs(PHOTO_FOLDER)
    if not os.path.exists(VIOLATION_FOLDER):
        os.makedirs(VIOLATION_FOLDER)

    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cam.isOpened():
        return None, "ERROR: Webcam not found"

    photo_taken = False
    photo_path = ""

    print("Step 1: Press 's' to save photo when face is detected")
    while True:
        ret, frame = cam.read()
        if not ret: continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = FACE_CASCADE.detectMultiScale(gray, 1.3, 5)

        status = "Face Not Detected"
        color = (0,0,255)
        for (x,y,w,h) in faces:
            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
            status = "Face Detected"
            color = (0,255,0)

        cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(frame, "Press 's' to Capture Photo", (10, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        cv2.imshow(f"Registration - {candidate_id}", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s') and len(faces) > 0:
            photo_path = os.path.join(PHOTO_FOLDER, f"{candidate_id}.jpg")
            cv2.imwrite(photo_path, frame)
            photo_taken = True
            break
        elif key == ord('q'):
            cam.release()
            cv2.destroyAllWindows()
            return None, "Capture cancelled by user"

    cam.release()
    cv2.destroyAllWindows()

    if photo_taken:
        # Step 2: Start Continuous Monitoring
        start_monitoring(candidate_id)
        return photo_path, "Photo captured and Monitoring Started"

def start_monitoring(candidate_id):
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    # VARIABLES
    session_start_time = time.time() # For total session timing
    face_absent_start_time = None
    total_absence_duration = 0.0
    absent_count = 0 # NEW: How many times face was absent
    last_status = "Face Detected"
    screenshot_taken = False

    print(f"Monitoring Started for {candidate_id}. Press 'q' to Quit")

    while True:
        ret, frame = cam.read()
        if not ret: break

        current_time = time.time()
        session_duration = current_time - session_start_time # 5. Session Timing
        time_str = datetime.now().strftime("%H:%M:%S")

        # 1. CONTINUOUS FACE PRESENCE MONITORING
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = FACE_CASCADE.detectMultiScale(gray, 1.3, 5)

        status = "Face Not Detected"
        status_color = (0, 0, 255) # RED

        if len(faces) > 0:
            status = "Face Detected"
            status_color = (0, 255, 0) # GREEN
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), status_color, 3)

            # 3. RESET TIMER WHEN FACE RETURNS
            if face_absent_start_time is not None:
                absence_time = current_time - face_absent_start_time
                total_absence_duration += absence_time
                log_event(candidate_id, "Face Returned", f"Was absent for {absence_time:.1f} sec")
                face_absent_start_time = None
                screenshot_taken = False

        else:
            # 2. LOG EVENT + COUNT
            if face_absent_start_time is None:
                face_absent_start_time = current_time
                absent_count += 1 # NEW: Increase count each time absence starts
                if last_status == "Face Detected":
                    log_event(candidate_id, "Face Not Detected", f"Absence #{absent_count} started")

            current_absence = current_time - face_absent_start_time

            # Take screenshot after 2 sec absence
            if current_absence >= 2.0 and screenshot_taken == False:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = os.path.join("violations", f"{candidate_id}_ABSENCE_{timestamp}.jpg")
                cv2.imwrite(screenshot_path, frame)
                log_violation_with_screenshot(candidate_id, "Absence > 2sec", screenshot_path)
                screenshot_taken = True

        last_status = status

        # 4. DISPLAY REAL-TIME INFO ON WEBCAM SCREEN
        cv2.rectangle(frame, (0, 0), (640, 190), (0, 0, 0), -1) # Bigger black bar

        cv2.putText(frame, f"Status: {status}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, status_color, 2)
        cv2.putText(frame, f"Time: {time_str}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # NEW LINES ADDED HERE
        cv2.putText(frame, f"Session Time: {int(session_duration//60)}m {int(session_duration%60)}s", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, f"Total Absence: {total_absence_duration:.1f} sec", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.putText(frame, f"Absent Count: {absent_count} times", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2) # ORANGE

        cv2.putText(frame, f"Candidate: {candidate_id}", (400, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(frame, "Press 'q' to End", (480, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        cv2.imshow(f"Exam Monitoring - {candidate_id}", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            if face_absent_start_time is not None:
                total_absence_duration += current_time - face_absent_start_time
            log_event(candidate_id, "Session Ended", f"Total Absence: {total_absence_duration:.1f} sec, Count: {absent_count}")
            break

    cam.release()
    cv2.destroyAllWindows()
    print(f"Session Ended. Total Time: {int(session_duration//60)}m | Total Absence: {total_absence_duration:.1f}s | Count: {absent_count}")