from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from flask_bootstrap import Bootstrap
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
Bootstrap(app)

# Database configuration
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="srm2024",
    database="blood_bank"
)
cursor = db.cursor()

# Login Route
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM Users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            flash('Login Successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Credentials!', 'error')
    return render_template('login.html')

# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        try:
            cursor.execute("INSERT INTO Users (username, password, role) VALUES (%s, %s, %s)", (username, password, role))
            db.commit()
            flash('Signup Successful!', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'error')
    return render_template('signup.html')

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login to access the dashboard.', 'error')
        return redirect(url_for('login'))
    
    # Fetch dashboard stats
    cursor.execute("SELECT COUNT(*) FROM Donors")
    total_donors = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Patients")
    total_patients = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM BloodRequests WHERE status = 'Pending'")
    pending_requests = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(quantity) FROM BloodInventory")
    total_blood = cursor.fetchone()[0] or 0

    return render_template('dashboard.html', total_donors=total_donors, total_patients=total_patients, pending_requests=pending_requests, total_blood=total_blood)
# Approve Blood Request Route
@app.route('/approve_request/<int:request_id>')
def approve_request(request_id):
    if 'user_id' not in session:
        flash('Please login to access this page.', 'error')
        return redirect(url_for('login'))
    try:
        cursor.execute("UPDATE BloodRequests SET status = 'Approved' WHERE request_id = %s", (request_id,))
        db.commit()
        flash('Request Approved Successfully!', 'success')
    except mysql.connector.Error as err:
        flash(f'Error: {err}', 'error')
    return redirect(url_for('view_blood_requests'))

# Add Donor Route
@app.route('/add_donor', methods=['GET', 'POST'])
def add_donor():
    if 'user_id' not in session:
        flash('Please login to access this page.', 'error')
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        blood_group = request.form['blood_group']
        contact = request.form['contact']
        address = request.form['address']
        try:
            cursor.execute("INSERT INTO Donors (name, age, gender, blood_group, contact, address) VALUES (%s, %s, %s, %s, %s, %s)",
                           (name, age, gender, blood_group, contact, address))
            db.commit()
            flash('Donor Added Successfully!', 'success')
            return redirect(url_for('view_donors'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'error')
    return render_template('add_donor.html')

# View Donors Route
@app.route('/view_donors')
def view_donors():
    if 'user_id' not in session:
        flash('Please login to access this page.', 'error')
        return redirect(url_for('login'))
    cursor.execute("SELECT * FROM Donors")
    donors = cursor.fetchall()
    return render_template('view_donors.html', donors=donors)

# Add Patient Route
@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if 'user_id' not in session:
        flash('Please login to access this page.', 'error')
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        blood_group = request.form['blood_group']
        contact = request.form['contact']
        hospital_id = request.form['hospital_id']
        try:
            cursor.execute("INSERT INTO Patients (name, age, gender, blood_group, contact, hospital_id) VALUES (%s, %s, %s, %s, %s, %s)",
                           (name, age, gender, blood_group, contact, hospital_id))
            db.commit()
            flash('Patient Added Successfully!', 'success')
            return redirect(url_for('view_patients'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'error')
    cursor.execute("SELECT * FROM Hospitals")
    hospitals = cursor.fetchall()
    return render_template('add_patient.html', hospitals=hospitals)

# View Patients Route
@app.route('/view_patients')
def view_patients():
    if 'user_id' not in session:
        flash('Please login to access this page.', 'error')
        return redirect(url_for('login'))
    cursor.execute("""
        SELECT p.*, h.name as hospital_name 
        FROM Patients p 
        LEFT JOIN Hospitals h ON p.hospital_id = h.hospital_id
    """)
    patients = cursor.fetchall()
    return render_template('view_patients.html', patients=patients)

# Add Hospital Route
@app.route('/add_hospital', methods=['GET', 'POST'])
def add_hospital():
    if 'user_id' not in session:
        flash('Please login to access this page.', 'error')
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        contact = request.form['contact']
        try:
            cursor.execute("INSERT INTO Hospitals (name, address, contact) VALUES (%s, %s, %s)", (name, address, contact))
            db.commit()
            flash('Hospital Added Successfully!', 'success')
            return redirect(url_for('view_hospitals'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'error')
    return render_template('add_hospital.html')

# View Hospitals Route
@app.route('/view_hospitals')
def view_hospitals():
    if 'user_id' not in session:
        flash('Please login to access this page.', 'error')
        return redirect(url_for('login'))
    cursor.execute("SELECT * FROM Hospitals")
    hospitals = cursor.fetchall()
    return render_template('view_hospitals.html', hospitals=hospitals)

# Add Blood Inventory Route
@app.route('/add_blood_inventory', methods=['GET', 'POST'])
def add_blood_inventory():
    if 'user_id' not in session:
        flash('Please login to access this page.', 'error')
        return redirect(url_for('login'))
    if request.method == 'POST':
        blood_group = request.form['blood_group']
        quantity = request.form['quantity']
        try:
            cursor.execute("INSERT INTO BloodInventory (blood_group, quantity) VALUES (%s, %s)",
                           (blood_group, quantity))
            db.commit()
            flash('Blood Inventory Added Successfully!', 'success')
            return redirect(url_for('view_blood_inventory'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'error')
    return render_template('add_blood_inventory.html')

# View Blood Inventory Route
@app.route('/view_blood_inventory')
def view_blood_inventory():
    if 'user_id' not in session:
        flash('Please login to access this page.', 'error')
        return redirect(url_for('login'))
    cursor.execute("SELECT * FROM BloodInventory")
    blood_inventory = cursor.fetchall()
    return render_template('view_blood_inventory.html', blood_inventory=blood_inventory)

# Add Blood Request Route
@app.route('/add_blood_request', methods=['GET', 'POST'])
def add_blood_request():
    if 'user_id' not in session:
        flash('Please login to access this page.', 'error')
        return redirect(url_for('login'))
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        blood_group = request.form['blood_group']
        quantity = request.form['quantity']
        hospital_id = request.form['hospital_id']
        try:
            cursor.execute("INSERT INTO BloodRequests (patient_id, blood_group, quantity, status, hospital_id) VALUES (%s, %s, %s, 'Pending', %s)",
                           (patient_id, blood_group, quantity, hospital_id))
            db.commit()
            flash('Blood Request Added Successfully!', 'success')
            return redirect(url_for('view_blood_requests'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'error')
    cursor.execute("SELECT * FROM Patients")
    patients = cursor.fetchall()
    cursor.execute("SELECT * FROM Hospitals")
    hospitals = cursor.fetchall()
    return render_template('add_blood_request.html', patients=patients, hospitals=hospitals)

# View Blood Requests Route
@app.route('/view_blood_requests')
def view_blood_requests():
    if 'user_id' not in session:
        flash('Please login to access this page.', 'error')
        return redirect(url_for('login'))
    cursor.execute("SELECT * FROM BloodRequests")
    blood_requests = cursor.fetchall()
    return render_template('view_blood_requests.html', blood_requests=blood_requests)

# Update Request Status Route
@app.route('/update_request_status/<int:request_id>/<string:status>')
def update_request_status(request_id, status):
    if 'user_id' not in session:
        flash('Please login to access this page.', 'error')
        return redirect(url_for('login'))
    try:
        cursor.execute("UPDATE BloodRequests SET status = %s WHERE request_id = %s", (status, request_id))
        db.commit()
        flash('Request status updated successfully!', 'success')
    except mysql.connector.Error as err:
        flash(f'Error: {err}', 'error')
    return redirect(url_for('view_blood_requests'))
# Replace the existing approve_request route with this combined route
@app.route('/update_request/<int:request_id>/<string:action>')
def update_request(request_id, action):
    if 'user_id' not in session:
        flash('Please login to access this page.', 'error')
        return redirect(url_for('login'))
    try:
        status = 'Approved' if action == 'approve' else 'Rejected'
        cursor.execute("UPDATE BloodRequests SET status = %s WHERE request_id = %s", (status, request_id))
        db.commit()
        flash(f'Request {status} Successfully!', 'success')
    except mysql.connector.Error as err:
        flash(f'Error: {err}', 'error')
    return redirect(url_for('view_blood_requests'))
# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged Out Successfully!', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)