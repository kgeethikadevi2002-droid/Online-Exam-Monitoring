import cv2
import sqlite3
from datetime import datetime
import time

DATABASE = "exam.db"
CANDIDATE_ID = "C101" 

def log_event(candidate_id, event_type, remarks):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO EventLog(candidate_id, event_type, timestamp, remarks) VALUES (?,?,?,?)",
              (candidate_id, event_type, timestamp, remarks))
    conn.commit()
    conn.close()
    print(f"[DB LOG] {event_type} | {timestamp} | {remarks}") # Shows in terminal too

CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
FACE_CASCADE = cv2.CascadeClassifier(CASCADE_PATH)
cam = cv2.VideoCapture(0)

face_absent_start_time = None  
total_absence_duration = 0.0   
last_status = "Face Detected"  

print(f"Testing Started for {CANDIDATE_ID}. Press 'q' to Quit")

while True:
    ret, frame = cam.read()
    if not ret: break

    current_time = time.time()
    time_str = datetime.now().strftime("%H:%M:%S")

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = FACE_CASCADE.detectMultiScale(gray, 1.3, 5)

    if len(faces) > 0:
        status = "Face Detected"
        color = (0, 255, 0)
        for (x, y, w, h) in faces: cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        
        # SCENARIO 3: FACE RETURNS
        if face_absent_start_time is not None:
            absence_time = current_time - face_absent_start_time
            total_absence_duration += absence_time
            log_event(CANDIDATE_ID, "Face Returned", f"Was absent for {absence_time:.1f} sec")
            face_absent_start_time = None

    else:
        status = "Face Not Detected"
        color = (0, 0, 255)

        # SCENARIO 2: FACE REMOVED
        if face_absent_start_time is None:
            face_absent_start_time = current_time
            if last_status == "Face Detected": # SCENARIO 4: LOG EACH NEW ABSENCE
                log_event(CANDIDATE_ID, "Face Not Detected", "Absence started")

    last_status = status
    current_absence = 0.0
    if face_absent_start_time is not None: current_absence = current_time - face_absent_start_time

    # DISPLAY
    cv2.rectangle(frame, (0, 0), (500, 150), (0, 0, 0), -1)
    cv2.putText(frame, f"Status: {status}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    cv2.putText(frame, f"Time: {time_str}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"Current Absence: {current_absence:.1f} sec", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
    cv2.putText(frame, f"Total Absence: {total_absence_duration:.1f} sec", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    cv2.putText(frame, "Press 'q' to Quit", (10, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.imshow("Test Scenarios", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'): break

cam.release()
cv2.destroyAllWindows()