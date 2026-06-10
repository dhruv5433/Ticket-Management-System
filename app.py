from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.secret_key = 'ticket_management_system'


@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():

    employee_id = request.form['employee_id']
    password = request.form['password']

    conn = sqlite3.connect('ticketing.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users")
    print(cursor.fetchall())

    cursor.execute(
    "SELECT * FROM users WHERE employee_id=? AND password=?",
    (employee_id, password))

    user = cursor.fetchone()
    print(user)

    conn.close()

    if user:

        session['user_id'] = user[0]
        session['username'] = user[5] + " " + user[6]
        session['role'] = user[4]

        role = user[4]

        if role == 'USER':
            return redirect('/dashboard')

        elif role == 'L1':
            return redirect('/l1-dashboard')

        elif role == 'L2':
            return redirect('/l2-dashboard')

        elif role == 'L3':
            return redirect('/l3-dashboard')

    return "Invalid Employee ID or Password"

@app.route('/create-ticket')
def create_ticket():
    return render_template('create_ticket.html')

@app.route('/submit_ticket', methods=['POST'])
def submit_ticket():

    title = request.form['title']
    description = request.form['description']

    attachment = request.files.get('attachment')

    filename = None

    if attachment and attachment.filename != "":

        filename = secure_filename(
            attachment.filename
        )

        attachment.save(
            os.path.join(
                "uploads",
                filename
            )
        )

    conn = sqlite3.connect('ticketing.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM tickets"
    )

    ticket_count = cursor.fetchone()[0]

    l1_engineers = [6, 7, 8]

    assigned_to = l1_engineers[
        ticket_count % len(l1_engineers)
    ]

    cursor.execute("""
    INSERT INTO tickets
    (
        title,
        description,
        status,
        assigned_level,
        assigned_to,
        created_by,
        ticket_code,
        attachment
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        title,
        description,
        'Open',
        'L1',
        assigned_to,
        session['user_id'],
        f"TKT-{ticket_count + 1:04d}",
        filename
    ))

    conn.commit()
    conn.close()

    return redirect('/dashboard')


from datetime import datetime

@app.route('/register', methods=['POST'])
def register():

    first_name = request.form['first_name']
    last_name = request.form['last_name']
    employee_id = request.form['employee_id']
    email = request.form['email']
    phone_number = request.form['phone_number']
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

    existing_email = cursor.fetchone()

    if existing_email:
        conn.close()
        return "Email already registered"

    cursor.execute(
        "SELECT * FROM users WHERE employee_id=?",
        (employee_id,)
    )

    existing_employee = cursor.fetchone()

    if existing_employee:
        conn.close()
        return "Employee ID already exists"

    create_date = datetime.now().strftime("%d-%m-%Y %H:%M")

    name = first_name + " " + last_name

    cursor.execute("""
    INSERT INTO users
    (
        name,
        first_name,
        last_name,
        employee_id,
        email,
        phone_number,
        password,
        role,
        create_date
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        name,
        first_name,
        last_name,
        employee_id,
        email,
        phone_number,
        password,
        'USER',
        create_date
    ))

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

    my_tickets_count = len(tickets)

    open_count = 0
    resolved_count = 0

    for ticket in tickets:

        if ticket['status'] not in ['Resolved', 'Closed']:
            open_count += 1

        if ticket['status'] == 'Resolved':
            resolved_count += 1

    conn.close()

    return render_template(
        'dashboard_u.html',
        username=session['username'],
        tickets=tickets,
        my_tickets_count=my_tickets_count,
        open_count=open_count,
        resolved_count=resolved_count
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
    """
    SELECT * FROM tickets
    WHERE assigned_to=?
    """,
    (session['user_id'],)
    )

    tickets = cursor.fetchall()

    assigned_count = len(tickets)

    pending_count = 0
    resolved_count = 0

    for ticket in tickets:
        if ticket['status'] in ['Open', 'In Progress', 'Pending User Response', 'Escalated to L2']:
            pending_count += 1

        if ticket['status'] == 'Resolved':
            resolved_count += 1

    conn.close()

    return render_template(
        'l1_dashboard.html',
        username=session['username'],
        tickets=tickets,
        assigned_count=assigned_count,
        pending_count=pending_count,
        resolved_count=resolved_count
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

    elif action == "Pending User Response":

        cursor.execute(
            """
            UPDATE tickets
            SET status='Pending User Response'
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

    elif action == "Closed":

        cursor.execute(
            """
            UPDATE tickets
            SET status='Closed'
            WHERE ticket_id=?
            """,
            (ticket_id,)
        )

    elif action == "Escalated to L2":

        cursor.execute(
            """
            UPDATE tickets
            SET assigned_level='L2',
                status='Escalated to L2'
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

@app.route('/view-ticket', methods=['POST'])
def view_ticket():

    ticket_id = request.form['ticket_id']

    conn = sqlite3.connect('ticketing.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

   
    cursor.execute(
        "SELECT * FROM tickets WHERE ticket_id=?",
        (ticket_id,)
    )

    selected_ticket = cursor.fetchone()

    cursor.execute(
    """
    SELECT
    comments.*,
    users.first_name,
    users.last_name

    FROM comments

    JOIN users
    ON comments.user_id = users.id

    WHERE comments.ticket_id=?

    ORDER BY comments.comment_id
    """,
    (ticket_id,)
)

    comments = cursor.fetchall()

    cursor.execute(
        """
        SELECT * FROM tickets
        WHERE assigned_to=?
        """,
        (session['user_id'],)
    )

    tickets = cursor.fetchall()

    
    cursor.execute(
        """
        SELECT * FROM users WHERE id=?
        """,
        (selected_ticket['created_by'],)
    )

    ticket_user = cursor.fetchone()

    assigned_count = len(tickets)

    pending_count = 0
    resolved_count = 0

    for ticket in tickets:
        if ticket['status'] in ['Open', 'In Progress', 'Pending User Response', 'Escalated to L2']:
            pending_count += 1

        if ticket['status'] == 'Resolved':
            resolved_count += 1

    conn.close()

    return render_template(
        'l1_dashboard.html',
        username=session['username'],
        tickets=tickets,
        selected_ticket=selected_ticket,
        comments=comments,
        ticket_user=ticket_user,
        assigned_count=assigned_count,
        pending_count=pending_count,
        resolved_count=resolved_count
    )

@app.route('/add-comment', methods=['POST'])
def add_comment():

    ticket_id = request.form['ticket_id']
    comment = request.form['comment']

    conn = sqlite3.connect('ticketing.db')
    cursor = conn.cursor()

    ticket_code = f"TKT-{int(ticket_id):04d}"
    comment_date = datetime.now().strftime("%d-%m-%y %H:%M")
    
    cursor.execute(
        """
        INSERT INTO comments
        (ticket_id, user_id, comment_by_role, comment, comment_date, ticket_code)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            ticket_id,
            session['user_id'],
            session['role'],
            comment,
            comment_date,
            ticket_code
            
        )
    )

    conn.commit()
    conn.close()

    if session['role'] == 'USER':
        return redirect('/dashboard')
    elif session['role'] == 'L1':
        return redirect('/l1-dashboard')
    elif session['role'] == 'L2':
        return redirect('/l2-dashboard')
    elif session['role'] == 'L3':
        return redirect('/l3-dashboard')

@app.route('/view-user-ticket', methods=['POST'])
def view_user_ticket():

    ticket_id = request.form['ticket_id']

    conn = sqlite3.connect('ticketing.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM tickets WHERE ticket_id=?",
        (ticket_id,)
    )

    selected_ticket = cursor.fetchone()

    cursor.execute(
        """
        SELECT
            comments.*,
            users.first_name,
            users.last_name

        FROM comments

        JOIN users
        ON comments.user_id = users.id

        WHERE comments.ticket_id=?

        ORDER BY comments.comment_id
        """,
        (ticket_id,)
    )

    comments = cursor.fetchall()

    cursor.execute(
        """
        SELECT * FROM tickets
        WHERE created_by=?
        """,
        (session['user_id'],)
    )

    tickets = cursor.fetchall()

    my_tickets_count = len(tickets)

    open_count = 0
    resolved_count = 0

    for ticket in tickets:

        if ticket['status'] not in ['Resolved', 'Closed']:
            open_count += 1

        if ticket['status'] == 'Resolved':
            resolved_count += 1


    conn.close()

    return render_template(
        'dashboard_u.html',
        username=session['username'],
        tickets=tickets,
        selected_ticket=selected_ticket,
        comments=comments,
        my_tickets_count=my_tickets_count,
        open_count=open_count,
        resolved_count=resolved_count
    )

if __name__ == '__main__':
    app.run(debug=True)
