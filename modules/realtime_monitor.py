import cv2
import sqlite3
from datetime import datetime
import time

# ========== CONFIG ==========
DB_NAME = "exam.db"
CANDIDATE_ID = "C101" # Change this to logged-in candidate

# ========== DATABASE ==========
def log_event(candidate_id, event_type, remarks):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO EventLog(candidate_id, event_type, timestamp, remarks) VALUES (?,?,?,?)",
              (candidate_id, event_type, timestamp, remarks))
    conn.commit()
    conn.close()

# ========== FACE DETECTION ==========
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
FACE_CASCADE = cv2.CascadeClassifier(CASCADE_PATH)
cam = cv2.VideoCapture(0)

if not cam.isOpened():
    print("ERROR: Cannot open webcam")
    exit()

# ========== TIMER VARIABLES ==========
face_absent_start_time = None  
total_absence_duration = 0.0   
last_status = "Face Detected"  

print("Real-Time Monitoring Started... Press 'q' to Quit")

while True:
    ret, frame = cam.read()
    if not ret:
        break

    current_time = time.time()
    current_time_str = datetime.now().strftime("%H:%M:%S") # For display

    # 1. DETECT FACE
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    # 2. CHECK STATUS + TIMER LOGIC
    if len(faces) > 0:
        status = "Face Detected"
        status_color = (0, 255, 0) # Green
        box_color = (0, 255, 0)
        
        # Draw box
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)
        
        # Reset timer when face returns
        if face_absent_start_time is not None:
            absence_time = current_time - face_absent_start_time
            total_absence_duration += absence_time
            face_absent_start_time = None

    else:
        status = "Face Not Detected"
        status_color = (0, 0, 255) # Red
        box_color = (0, 0, 255)

        # Start timer when face goes missing
        if face_absent_start_time is None:
            face_absent_start_time = current_time
            if last_status == "Face Detected": # Log only once
                log_event(CANDIDATE_ID, "Face Not Detected", "Face not in frame")

    last_status = status

    # 3. CALCULATE CURRENT ABSENCE FOR DISPLAY
    current_absence = 0.0
    if face_absent_start_time is not None:
        current_absence = current_time - face_absent_start_time

    # ========== 4. DISPLAY REAL-TIME INFO ON WEBCAM FEED ==========
    
    # Create a black background bar for text
    cv2.rectangle(frame, (0, 0), (450, 140), (0, 0, 0), -1)
    
    # INFO 1: Face Detection Status
    cv2.putText(frame, f"Status: {status}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
    
    # INFO 2: Current Time
    cv2.putText(frame, f"Time: {current_time_str}", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # INFO 3: Total Face Absence Duration
    cv2.putText(frame, f"Total Absence: {total_absence_duration:.1f} sec", (10, 90), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)

    # EXTRA INFO
    cv2.putText(frame, f"Candidate: {CANDIDATE_ID}", (10, 120), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
    cv2.putText(frame, "Press 'q' to Quit", (10, 470), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    # 5. SHOW VIDEO
    cv2.imshow("Real-Time Exam Monitoring", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()