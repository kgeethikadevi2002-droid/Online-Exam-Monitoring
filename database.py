import sqlite3
import uuid
from datetime import datetime

DATABASE = "exam.db"

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def add_candidate(candidate_id, name, email, age, subject, password, photo_path):
    try:
        conn = get_connection()
        conn.execute("INSERT INTO Candidate(candidate_id, name, email, age, exam_subject, password, photo_path) VALUES (?,?,?,?,?,?,?)",
                     (candidate_id, name, email, int(age), subject, password, photo_path))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError as e:
        print("DB ERROR:", e) # This will show in terminal
        return False

def get_candidate_by_email(email):
    conn = get_connection()
    candidate = conn.execute("SELECT * FROM Candidate WHERE email =?", (email,)).fetchone()
    conn.close()
    return candidate

def create_session(candidate_id):
    session_id = str(uuid.uuid4())
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    conn.execute("INSERT INTO Session(session_id, candidate_id, start_time, end_time, status) VALUES (?,?,?,?,?)",
                 (session_id, candidate_id, start_time, None, "Started"))
    conn.commit()
    conn.close()
    return session_id

def update_session_status(session_id, status):
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if status == "Ended" else None
    conn = get_connection()
    if status == "Ended":
        conn.execute("UPDATE Session SET status=?, end_time=? WHERE session_id=?",
                     (status, end_time, session_id))
    else:
        conn.execute("UPDATE Session SET status=? WHERE session_id=?", (status, session_id))
    conn.commit()
    conn.close()

def log_event(candidate_id, event_type, remarks=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    conn.execute("INSERT INTO EventLog(candidate_id, event_type, timestamp, remarks) VALUES (?,?,?,?)",
                 (candidate_id, event_type, timestamp, remarks))
    conn.commit()
    conn.close()
    print(f"Logged: {event_type} for {candidate_id}")