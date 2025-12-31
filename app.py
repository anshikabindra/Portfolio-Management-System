from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error
import csv
import io

from Category_Mapping import category_mapping_bp
from bank_transaction import bank_bp
from fd_transactions import fd_bp
from Equity import equity_bp
from mf_transactions import mf_bp
from pf_transactions import pf_bp

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# MySQL configuration
db_config = {
    'user': 'root',
    'password': 'Anshika',
    'host': '127.0.0.1',
    'port': '3306',
    'database': 'portfolioManagement'
}

# Route: Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email'].lower()
        password = request.form['password']
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
            conn.commit()
            flash('Registration successful. Please login.')
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash('Email already exists.')
            return redirect(url_for('register'))
        except Error as e:
            flash(f"Database error during registration: {e}")
            return redirect(url_for('register'))
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    return render_template('register.html')

# Route: Login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].lower()
        password = request.form['password']
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
            user = cursor.fetchone()
            if user:
                session['user'] = email
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password.')
        except Error as e:
            flash(f"Database error during login: {e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    return render_template('login.html')

# Route: Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# Route: Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# Route: Upload CSV
@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'user' not in session:
        return redirect(url_for('login'))

    file = request.files.get('csv_file')
    table_name_raw = request.form.get('table_name', '')
    table_map = {
        'Bank Transactions': 'bank_transaction',
        'FD Transactions': 'FD_transactions',
        'Equity Transactions': 'equity_transactions',
        'Mutual Fund Transactions': 'Mutual_Fund_transactions',
        'PF Transactions': 'pf_transaction',
        'Category_Mapping': 'Category_Mapping'
    }
    table_name = table_map.get(table_name_raw)

    if not file or not table_name:
        flash('Missing file or table selection.')
        return redirect(request.referrer)

    try:
        stream = io.StringIO(file.stream.read().decode("utf-8-sig"), newline=None)
        reader = csv.reader(stream)
        headers = next(reader)

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        placeholders = ", ".join(["%s"] * len(headers))
        column_names = ", ".join(headers)
        query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"

        for row in reader:
            # --- New Cleaning Logic (preserving your existing line) ---
            cleaned_row = []
            for val in row:
                val = val.strip()
                if val == '':
                    cleaned_row.append(None)
                elif val.replace(',', '').replace('.', '', 1).isdigit():
                    cleaned_row.append(val.replace(',', ''))  # Clean numeric strings like "1,000.50"
                else:
                    cleaned_row.append(val)
            row = cleaned_row  # Replace with cleaned row

            # Convert empty strings to None (your existing logic preserved)
            row = [col if col is not None and col != '' else None for col in row]
            cursor.execute(query, row)

        conn.commit()
        flash('CSV uploaded successfully.')
    except Error as e:
        flash(f"Error uploading CSV: {e}")
    except Exception as ex:
        flash(f"Unexpected error: {ex}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

    return redirect(request.referrer)

# Register Blueprints
app.register_blueprint(bank_bp)
app.register_blueprint(fd_bp)
app.register_blueprint(equity_bp)
app.register_blueprint(mf_bp)
app.register_blueprint(pf_bp)
app.register_blueprint(category_mapping_bp)

if __name__ == '__main__':
   # app.run(debug=True)
   app.run(host="0.0.0.0",port=8080)

