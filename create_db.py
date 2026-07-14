import sqlite3
import os

if os.path.exists("exam.db"):
    os.remove("exam.db")

conn = sqlite3.connect("exam.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Candidate(
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Auto number 1,2,3...
    candidate_id TEXT UNIQUE NOT NULL, -- We will save C101, C102
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    age INTEGER,
    exam_subject TEXT,
    password TEXT NOT NULL,
    photo_path TEXT
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS Session(
    session_id TEXT PRIMARY KEY,
    candidate_id TEXT,
    start_time TEXT,
    end_time TEXT,
    status TEXT,
    FOREIGN KEY(candidate_id) REFERENCES Candidate(candidate_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS EventLog(
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id TEXT,
    event_type TEXT,
    timestamp TEXT,
    remarks TEXT,
    FOREIGN KEY(candidate_id) REFERENCES Candidate(candidate_id)
)
""")

conn.commit()
conn.close()
print("Database Created Successfully")