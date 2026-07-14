from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask import jsonify
from database import log_event
import uuid
import sqlite3
from database import add_candidate, get_candidate_by_email, create_session, update_session_status, get_connection
from capture_photo import capture_photo

app = Flask(__name__)
app.secret_key = "exam_secret_key"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        candidate_id = request.form['candidate_id']  # you had typo: 'candiade_id'
        name = request.form['name']
        email = request.form['email']
        age = request.form['age']
        subject = request.form['subject']
        password = request.form['password']
        
        # 1. Capture photo first
        photo_path, msg = capture_photo(candidate_id)
        
        if not photo_path:
            flash(f"Registration Failed! {msg}", "danger")
            return render_template('register.html')
        
        # 2. SAVE TO DATABASE - THIS WAS MISSING
        success = add_candidate(candidate_id, name, email, age, subject, password, photo_path)
        
        if success:
            flash(f"Registration Successful! ID: {candidate_id}", "success")
            return redirect(url_for('login'))
        else:
            flash("Candidate ID or Email already exists", "danger")
            return render_template('register.html')
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        candidate = get_candidate_by_email(email)
        if candidate and candidate['password'] == password:
            session['candidate_id'] = candidate['candidate_id']
            session['name'] = candidate['name']
            session['email'] = candidate['email']
            return redirect(url_for('dashboard'))
        flash("Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'candidate_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', name=session['name'], email=session['email'])

@app.route('/session/<action>')
def session_action(action):
    if 'candidate_id' not in session:
        return redirect(url_for('login'))
    
    cid = session['candidate_id']
    status_msg = ""
    if action == 'start':
        session['session_id'] = create_session(cid)
        log_event(cid, "Exam Started", "Candidate started exam")
        status_msg = "Exam Started"
    elif action == 'pause':
        update_session_status(session['session_id'], "Paused")
        log_event(cid, "Exam Paused", "Candidate paused exam")
        status_msg = "Exam Paused"
    elif action == 'resume':
        update_session_status(session['session_id'], "Resumed")
        log_event(cid, "Exam Resumed", "Candidate resumed exam")
        status_msg = "Exam Resumed"
    elif action == 'end':
        update_session_status(session['session_id'], "Ended")
        log_event(cid, "Exam Submitted", "Candidate submitted exam")
        status_msg = "Exam Completed Successfully!"
        session.pop('session_id', None)
    
    return render_template('session.html', status=status_msg, candidate_id=cid)

@app.route('/log_event', methods=['POST'])
def log_event_route():
    data = request.get_json()
    log_event(data['candidate_id'], data['event_type'], data['remarks'])
    return jsonify({"status": "success"})

@app.route('/session')
def session_page():
    if 'candidate_id' not in session:
        return redirect(url_for('login'))
    return render_template('session.html', status="Exam Started")
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__=="__main__":
    app.run(debug=True)