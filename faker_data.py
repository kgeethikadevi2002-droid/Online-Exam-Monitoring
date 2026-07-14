from faker import Faker
import csv
import sqlite3

fake = Faker()
DATABASE = "exam.db"

def generate_data(num=20):
    subjects = ["Python", "Java", "DBMS", "Aptitude","AI","Machine Learning"]
    data = []
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    for i in range(num):
        cid = f"CAND{1000+i}"
        row = [cid, fake.name(), fake.unique.email(), fake.random_int(18,30), fake.random_element(subjects), "1234", ""]
        data.append(row)
        try:
            c.execute("INSERT INTO Candidate VALUES (?,?,?,?,?,?,?)", row)
        except: pass
    
    conn.commit()
    conn.close()
    
    with open('sample_candidates.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['candidate_id','name','email','age','exam_subject','password','photo_path'])
        writer.writerows(data)
    print(f"{num} candidates generated")

if __name__ == "__main__":
    generate_data()