# import os

# db_config = {
#    "user": os.environ["DB_USER"],
#    "password": os.environ["DB_PASS"],
#    "database": os.environ["DB_NAME"],
#    "unix_socket": f"/cloudsql/{os.environ['INSTANCE_CONNECTION_NAME']}"
# }

from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error
import csv
import io
from werkzeug.security import generate_password_hash, check_password_hash

from Category_Mapping import category_mapping_bp
from bank_transaction import bank_bp
from fd_transactions import fd_bp
from Equity import equity_bp
from mf_transactions import mf_bp
from pf_transactions import pf_bp
from gold import gold_bp
from real_estate import real_estate_bp
from cash import cash_bp
from private_equity import private_equity_bp

app = Flask(__name__)
app.secret_key = 'supersecretkey'


# db_config = {
#     'user': 'root',
#     'password': 'Anshika',
#     'host': '127.0.0.1',
#     'port': '3306',
#     'database': 'portfolioManagement'
# }

# --- NEW AIVEN CLOUD DB CONFIG --- #
db_config = {
    'user': 'avnadmin',
    'password': 'AVNS_SRtc5d4cDCrezjU_70x',
    'host': 'portfolio-db-bindraanshika-32d.i.aivencloud.com',
    'port': '26174',
    'database': 'defaultdb',
    'ssl_disabled': False  # Aiven requires SSL connection
}


# ---------------- DATABASE INITIALIZATION ---------------- #
# This function creates your tables in the new cloud database if they don't exist
def init_db():
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 1. Users Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)

        # 2. Bank Transactions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bank_transaction (
                id INT AUTO_INCREMENT PRIMARY KEY,
                DT DATE,
                Narration TEXT,
                CHq_Ref_No VARCHAR(100),
                Value_Dt DATE,
                Withdrawal_Amt DECIMAL(15, 2),
                Deposit_Amt DECIMAL(15, 2),
                Closing_Balance DECIMAL(15, 2),
                bank_name VARCHAR(100),
                user_id INT
            )
        """)

        # 3. FD Transactions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fd_transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                Portfolio_name VARCHAR(100),
                FD_number VARCHAR(100),
                Principal_amt DECIMAL(15, 2),
                Start_date DATE,
                Rate DECIMAL(5, 2),
                Opening_Balance DECIMAL(15, 2),
                Current_value DECIMAL(15, 2),
                Maturity_date DATE,
                user_id INT
            )
        """)

        # 4. Equity Transactions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equity_transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                Company_name VARCHAR(255),
                ISIN_number VARCHAR(100),
                Transaction_date DATE,
                Transaction_rate DECIMAL(15, 2),
                Quantity INT,
                Transaction_type VARCHAR(50),
                user_id INT
            )
        """)

        # 5. Mutual Fund Transactions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Mutual_Fund_transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                Company_name VARCHAR(255),
                ISIN_number VARCHAR(100),
                Transaction_date DATE,
                Transaction_rate DECIMAL(15, 2),
                Quantity INT,
                Transaction_type VARCHAR(50),
                user_id INT
            )
        """)

        # 6. PF Transactions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pf (
                id INT AUTO_INCREMENT PRIMARY KEY,
                DT DATE,
                Narration TEXT,
                CHq_Ref_No VARCHAR(100),
                Value_Dt DATE,
                Withdrawal_Amt DECIMAL(15, 2),
                Deposit_Amt DECIMAL(15, 2),
                Closing_Balance DECIMAL(15, 2),
                user_id INT
            )
        """)

        # 7. Gold Investments
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gold_investments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                investment_name VARCHAR(255),
                value_per_gram DECIMAL(15, 2),
                quantity DECIMAL(15, 2),
                investment_date DATE,
                user_id INT
            )
        """)

        # 8. Real Estate
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS real_estate (
                id INT AUTO_INCREMENT PRIMARY KEY,
                Investment_name VARCHAR(255),
                Invested_value DECIMAL(15, 2),
                Date_of_investment DATE,
                Current_value DECIMAL(15, 2),
                user_id INT
            )
        """)

        # 9. Cash Investments
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cash_investments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                Investment_name VARCHAR(255),
                Invested_value_per_share DECIMAL(15, 2),
                No_of_units INT,
                Date_of_investment DATE,
                Current_value_per_share DECIMAL(15, 2),
                user_id INT
            )
        """)

        # 10. Private Equity
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS private_equity (
                id INT AUTO_INCREMENT PRIMARY KEY,
                Investment_name VARCHAR(255),
                Invested_value_per_share DECIMAL(15, 2),
                No_of_shares_issued INT,
                Date_of_investment DATE,
                Current_value_per_share DECIMAL(15, 2),
                user_id INT
            )
        """)

        # 11. Category Mapping
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Category_Mapping (
                id INT AUTO_INCREMENT PRIMARY KEY,
                Category VARCHAR(100),
                Description TEXT,
                Sub_Category VARCHAR(100),
                user_id INT
            )
        """)

        conn.commit()
        cursor.close()
        print("Database tables initialized successfully!")
    except Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if conn: conn.close()


# ---------------- AUTH ---------------- #

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email'].lower()
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        conn = cursor = None
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO users (email, password) VALUES (%s, %s)",
                (email, hashed_password)
            )
            conn.commit()
            return redirect(url_for('login'))

        except mysql.connector.IntegrityError:
            flash('Email already exists.')
        except Error as e:
            flash(f"Database error: {e}")

        finally:
            if cursor: cursor.close()
            if conn: conn.close()

        return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        email = request.form['email'].lower()
        password = request.form['password']

        conn = cursor = None
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cursor.fetchone()

            if user:
                stored_password = user['password']
                valid = False

                if stored_password and stored_password.startswith(("scrypt:", "pbkdf2:")):
                    valid = check_password_hash(stored_password, password)

                elif stored_password == password:
                    valid = True

                    # Upgrade to hashed password
                    new_hash = generate_password_hash(password)
                    cursor.execute(
                        "UPDATE users SET password=%s WHERE id=%s",
                        (new_hash, user['id'])
                    )
                    conn.commit()

                if valid:
                    session['user'] = email
                    session['user_id'] = user['id']
                    return redirect(url_for('dashboard'))

            flash('Invalid email or password')

        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    return render_template('dashboard.html', transactions=None, title=None)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ---------------- CONTEXT PROCESSORS ---------------- #

@app.context_processor
def inject_gold():
    gold_investments = []

    if 'user_id' in session:
        conn = cursor = None
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT * FROM gold_investments WHERE user_id = %s",
                (session['user_id'],)
            )
            gold_investments = cursor.fetchall()

        except Exception:
            gold_investments = []

        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    return dict(
        gold_exists=len(gold_investments) > 0,
        gold_investments=gold_investments
    )


@app.context_processor
def inject_other_assets():
    real_estate = []
    cash = []
    private_equity = []

    if 'user_id' in session:
        conn = cursor = None
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT * FROM real_estate WHERE user_id = %s",
                (session['user_id'],)
            )
            real_estate = cursor.fetchall()

            cursor.execute(
                "SELECT * FROM cash_investments WHERE user_id = %s",
                (session['user_id'],)
            )
            cash = cursor.fetchall()

            cursor.execute(
                "SELECT * FROM private_equity WHERE user_id = %s",
                (session['user_id'],)
            )
            private_equity = cursor.fetchall()

        except Exception:
            pass

        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    return dict(
        real_estate_exists=len(real_estate) > 0,
        cash_exists=len(cash) > 0,
        private_equity_exists=len(private_equity) > 0,
        real_estate=real_estate,
        cash=cash,
        private_equity=private_equity
    )


# ---------------- CSV UPLOAD ---------------- #

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'user' not in session:
        return redirect(url_for('login'))

    file = request.files.get('csv_file')
    table_name_raw = request.form.get('table_name', '').strip()

    table_map = {
        'bank transactions': 'bank_transaction',
        'fd transactions': 'fd_transactions',
        'equity transactions': 'equity_transactions',
        'mutual fund transactions': 'mutual_fund_transactions',
        'pf transactions': 'pf',
        'category mapping': 'Category_Mapping',
        'gold investments': 'gold_investments',
        'real estate': 'real_estate',
        'private equity': 'private_equity',
        'cash investments': 'cash_investments'
    }

    table_name = table_map.get(table_name_raw.lower())

    if not file or not table_name:
        flash('Error uploading CSV file', 'error')
        return redirect(request.referrer)

    conn = cursor = None

    try:
        stream = io.StringIO(file.stream.read().decode("utf-8-sig"))
        reader = csv.DictReader(stream)

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns_info = cursor.fetchall()

        db_columns = [col['Field'].lower() for col in columns_info]
        insert_columns = [h for h in reader.fieldnames if h.strip().lower() in db_columns]

        if 'user_id' in db_columns:
            insert_columns.append('user_id')

        placeholders = ", ".join(["%s"] * len(insert_columns))
        column_names = ", ".join(insert_columns)

        query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"

        for row in reader:
            values = [
                session.get('user_id') if col == 'user_id' else row.get(col)
                for col in insert_columns
            ]
            cursor.execute(query, values)

        conn.commit()
        flash('CSV file successfully uploaded', 'success')

    except Exception as e:
        print(e)
        flash('Error uploading CSV file', 'error')

    finally:
        if cursor: cursor.close()
        if conn: conn.close()

    return redirect(request.referrer)


# ---------------- BLUEPRINTS ---------------- #

app.register_blueprint(bank_bp, url_prefix="/bank")
app.register_blueprint(fd_bp, url_prefix="/fd")
app.register_blueprint(equity_bp, url_prefix="/equity")
app.register_blueprint(mf_bp, url_prefix="/mf")
app.register_blueprint(pf_bp, url_prefix="/pf")
app.register_blueprint(category_mapping_bp, url_prefix="/category_mapping")
app.register_blueprint(gold_bp, url_prefix="/gold")
app.register_blueprint(real_estate_bp, url_prefix="/real_estate")
app.register_blueprint(cash_bp, url_prefix="/cash")
app.register_blueprint(private_equity_bp, url_prefix="/private_equity")

# ---------------- RUN ---------------- #

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", port=8080)

# if __name__ == '__main__':
#    import os
#    port = int(os.environ.get("PORT", 8080))
#    app.run(host="0.0.0.0", port=port)