from flask import Flask, render_template, request, redirect, url_for, session
import hashlib
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',  # Replace with your MySQL username
        password='ADMIN1234',  # Replace with your MySQL password
        database='creditcardvault'  # Ensure this matches your actual database name
    )
    return connection

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("INSERT INTO Users (Username, PasswordHash, Role) VALUES (%s, %s, %s)",
                           (username, hashed_password, role))
            connection.commit()
            return "User registered successfully! You can now log in."
        except mysql.connector.Error as err:
            return f"Error: {err}"
        finally:
            cursor.close()
            connection.close()

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        predefined_credentials = {
            'admin': 'admin123',
            'merchant': 'merchant123',
            'customer': 'customer123'
        }

        if username in predefined_credentials and password == predefined_credentials[username]:
            session['username'] = username
            session['role'] = 'Admin' if username == 'admin' else ('Merchant' if username == 'merchant' else 'Customer')
            return redirect(url_for('dashboard'))

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT Role FROM Users WHERE Username=%s AND PasswordHash=%s",
                       (username, hashed_password))
        result = cursor.fetchone()

        if result:
            session['username'] = username
            session['role'] = result[0]
            return redirect(url_for('dashboard'))
        else:
            error = "Access denied. Invalid username or password."

    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    role = session['role']

    if role == 'Admin':
        return redirect(url_for('view_customers'))  # Ensure this route exists
    elif role == 'Merchant':
        return redirect(url_for('merchant_dashboard'))  # Ensure this route exists
    elif role == 'Customer':
        return redirect(url_for('customer_dashboard'))  # Ensure this route exists

    return "Access denied."

@app.route('/customer_dashboard')
def customer_dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('customer_dashboard.html')  # Ensure you have this template

@app.route('/view_transactions')
def view_transactions():
    if 'username' not in session:
        return redirect(url_for('login'))
    # Fetch transactions from the database and render them
    return render_template('view_transactions.html')  # Ensure you have this template

@app.route('/account_settings')
def account_settings():
    if 'username' not in session:
        return redirect(url_for('login'))
    # Render account settings template
    return render_template('account_settings.html')  # Ensure you have this template

if __name__ == "__main__":
    app.run(debug=True)