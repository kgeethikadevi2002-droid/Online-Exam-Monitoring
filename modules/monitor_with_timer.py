import cv2
import sqlite3
from datetime import datetime
import time

# ========== 1. DATABASE SETUP ==========
DATABASE = "exam.db"
CANDIDATE_ID = "C101" # Change this to logged-in candidate

def create_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS EventLog(
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id TEXT,
        event_type TEXT,
        timestamp TEXT,
        remarks TEXT
    )''')
    conn.commit()
    conn.close()

def log_event(candidate_id, event_type, remarks):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO EventLog(candidate_id, event_type, timestamp, remarks) VALUES (?,?,?,?)",
              (candidate_id, event_type, timestamp, remarks))
    conn.commit()
    conn.close()
    print(f"[LOGGED] {event_type} at {timestamp} | {remarks}")

create_db()

# ========== 2. FACE DETECTION SETUP ==========
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
FACE_CASCADE = cv2.CascadeClassifier(CASCADE_PATH)
cam = cv2.VideoCapture(0)

if not cam.isOpened():
    print("ERROR: Cannot open webcam")
    exit()

print(f"Monitoring Started for {CANDIDATE_ID}... Press 'q' to Quit")

# ========== 3. VARIABLES FOR TIMER ==========
face_absent_start_time = None  # When did absence start
total_absence_duration = 0.0   # Total time absent in whole session
last_status = "Face Detected"  # To log only once

while True:
    ret, frame = cam.read()
    if not ret:
        break

    current_time = time.time()
    time_str = datetime.now().strftime("%H:%M:%S")

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    # ========== 4. FACE CHECK + TIMER LOGIC ==========
    if len(faces) > 0:
        # FACE DETECTED
        status = "Face Detected"
        color = (0, 255, 0) # Green
        
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        
        # If face returns, add the last absence time to total and reset
        if face_absent_start_time is not None:
            absence_time = current_time - face_absent_start_time
            total_absence_duration += absence_time
            print(f"Face Returned. Added {absence_time:.1f}s to total.")
            face_absent_start_time = None # RESET TIMER

    else:
        # FACE NOT DETECTED
        status = "Face Not Detected"
        color = (0, 0, 255) # Red

        # Start timer if it's the first frame of absence
        if face_absent_start_time is None:
            face_absent_start_time = current_time
            # LOG EVENT ONLY ONCE
            if last_status == "Face Detected":
                remarks = "Candidate face not visible"
                log_event(CANDIDATE_ID, "Face Not Detected", remarks)

    last_status = status

    # Calculate current absence for display
    current_absence = 0.0
    if face_absent_start_time is not None:
        current_absence = current_time - face_absent_start_time

    # ========== 5. DISPLAY INFO ON SCREEN ==========
    cv2.putText(frame, f"Candidate: {CANDIDATE_ID}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
    cv2.putText(frame, f"Status: {status}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    cv2.putText(frame, f"Time: {time_str}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
    cv2.putText(frame, f"Current Absence: {current_absence:.1f} sec", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,165,255), 2)
    cv2.putText(frame, f"Total Absence: {total_absence_duration:.1f} sec", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)
    cv2.putText(frame, "Press 'q' to Quit", (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    cv2.imshow("Exam Monitoring", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        # If quitting while absent, add that last duration
        if face_absent_start_time is not None:
            total_absence_duration += current_time - face_absent_start_time
        log_event(CANDIDATE_ID, "Session Ended", f"Total Absence: {total_absence_duration:.1f} sec")
        break

cam.release()
cv2.destroyAllWindows()
print(f"\nSession Ended. Final Total Absence: {total_absence_duration:.1f} seconds")