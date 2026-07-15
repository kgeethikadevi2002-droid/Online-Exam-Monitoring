import cv2
import os
import time
from datetime import datetime
from database import log_event

# CONFIG
CANDIDATE_ID = input("Enter Candidate ID to start monitoring: ") # e.g. C101
PHOTO_FOLDER = "photos"
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
FACE_CASCADE = cv2.CascadeClassifier(CASCADE_PATH)

if not os.path.exists(PHOTO_FOLDER):
    os.makedirs(PHOTO_FOLDER)

cam = cv2.VideoCapture(0)

if not cam.isOpened():
    print("ERROR: Cannot open webcam")
    exit()

print("Monitoring Started. Press 'q' to Quit")

# VARIABLES FOR TRACKING
face_absent_start_time = None
total_absence_duration = 0.0
last_status = "Face Detected" # To avoid duplicate logs

while True:
    ret, frame = cam.read()
    if not ret:
        break

    current_time_str = datetime.now().strftime("%H:%M:%S")
    
    # 1. DETECT FACE
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    # 2. CHECK STATUS AND TIMER LOGIC
    if len(faces) > 0:
        # FACE IS PRESENT
        status = "Face Detected"
        color = (0, 255, 0)
        
        # Draw box
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
        # If face returns, stop timer and reset
        if face_absent_start_time is not None:
            print("Face Returned. Timer Reset.")
            face_absent_start_time = None # Reset timer

    else:
        # FACE IS NOT PRESENT
        status = "Face Not Detected"
        color = (0, 0, 255)

        # Start timer if it's the first time
        if face_absent_start_time is None:
            face_absent_start_time = time.time()
            # LOG EVENT ONLY ONCE WHEN IT STARTS
            if last_status != status:
                log_event(CANDIDATE_ID, "Face Not Detected", "Candidate face not visible in frame")

        # Calculate current absence duration
        current_absence = time.time() - face_absent_start_time
        total_absence_duration += 1/30 # Approx add frame time. Better: calculate diff

    last_status = status
    
    # 3. DISPLAY REAL-TIME INFO ON SCREEN
    cv2.putText(frame, f"Status: {status}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    cv2.putText(frame, f"Time: {current_time_str}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Show current absence time
    display_absence = 0
    if face_absent_start_time is not None:
        display_absence = time.time() - face_absent_start_time
    
    cv2.putText(frame, f"Current Absence: {display_absence:.1f} sec", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
    cv2.putText(frame, f"Total Absence: {total_absence_duration:.1f} sec", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    cv2.putText(frame, "Press 'q' to Quit", (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    cv2.imshow(f"Monitoring - {CANDIDATE_ID}", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        # Log final end event
        log_event(CANDIDATE_ID, "Session Ended", f"Total Absence: {total_absence_duration:.1f} sec")
        break

cam.release()
cv2.destroyAllWindows()
print(f"Session Ended. Total Face Absence: {total_absence_duration:.1f} seconds")