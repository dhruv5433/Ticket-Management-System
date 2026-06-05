from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3

app = Flask(__name__)

app.secret_key = 'ticket_management_system'

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():

    email = request.form['email']
    password = request.form['password']

    conn = sqlite3.connect('ticketing.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users")
    print(cursor.fetchall())

    cursor.execute(
    "SELECT * FROM users WHERE email=? AND password=?",
    (email, password))

    user = cursor.fetchone()
    print(user)

    conn.close()

    if user:

        session['user_id'] = user[0]
        session['username'] = user[1]

        role = user[4]

        if role == 'USER':
            return redirect('/dashboard')

        elif role == 'L1':
            return redirect('/l1-dashboard')

        elif role == 'L2':
            return redirect('/l2-dashboard')

        elif role == 'L3':
            return redirect('/l3-dashboard')

    return "Invalid Email or Password"

@app.route('/create-ticket')
def create_ticket():
    return render_template('create_ticket.html')

    
@app.route('/submit_ticket', methods=['POST'])
def submit_ticket():

    title = request.form['title']
    description = request.form['description']

    conn = sqlite3.connect('ticketing.db')
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO tickets
    (title, description, status, assigned_level, created_by)
    VALUES (?, ?, ?, ?, ?)
    """,
    (title, description, 'Open', 'L1', session['user_id']))

    conn.commit()
    conn.close()

    return redirect('/dashboard')
   
    conn.commit()
    conn.close()

@app.route('/register', methods=['POST'])
def register():

    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password != confirm_password:
        return "Passwords do not match"

    conn = sqlite3.connect('ticketing.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        return "Email already registered"

    cursor.execute("""
    INSERT INTO users
    (name, email, password, role)
    VALUES (?, ?, ?, ?)
    """,
    (name, email, password, 'USER'))

    conn.commit()
    conn.close()

    return render_template('signup_success.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():

    conn = sqlite3.connect('ticketing.db')
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM tickets WHERE created_by=?",
        (session['user_id'],)
    )

    tickets = cursor.fetchall()

    conn.close()

    return render_template(
        'dashboard_u.html',
        username=session['username'],
        tickets=tickets
    )

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/l1-dashboard')
def l1_dashboard():

    conn = sqlite3.connect('ticketing.db')
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM tickets WHERE assigned_level='L1'"
    )

    tickets = cursor.fetchall()

    conn.close()

    return render_template(
        'l1_dashboard.html',
        username=session['username'],
        tickets=tickets
    )

@app.route('/update-ticket', methods=['POST'])
def update_ticket():

    ticket_id = request.form['ticket_id']
    action = request.form['action']

    conn = sqlite3.connect('ticketing.db')
    cursor = conn.cursor()

    if action == "In Progress":

        cursor.execute(
            """
            UPDATE tickets
            SET status='In Progress'
            WHERE ticket_id=?
            """,
            (ticket_id,)
        )

    elif action == "Resolved":

        cursor.execute(
            """
            UPDATE tickets
            SET status='Resolved'
            WHERE ticket_id=?
            """,
            (ticket_id,)
        )

    elif action == "Escalate":

        cursor.execute(
            """
            UPDATE tickets
            SET assigned_level='L2',
                status='Escalated'
            WHERE ticket_id=?
            """,
            (ticket_id,)
        )

    conn.commit()
    conn.close()

    return redirect('/l1-dashboard')

@app.route('/l2-dashboard')
def l2_dashboard():
    return "L2 Dashboard"

@app.route('/l3-dashboard')
def l3_dashboard():
    return "L3 Dashboard"

if __name__ == '__main__':
    app.run(debug=True)
