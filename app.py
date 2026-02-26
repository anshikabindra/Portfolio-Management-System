from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error
import csv
import io
import os
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

# MySQL configuration
#db_config = {
 #   'user': 'root',
  #  'password': 'Anshika',
   # 'host': '127.0.0.1',
  #  'port': '3306',
   # 'database': 'portfolioManagement'
#}

db_config = {
    "user": os.environ["root"],
    "password": os.environ["Anshika"],
    "database": os.environ["portfolio_management"],
    "unix_socket": f"/cloudsql/{os.environ['centering-star-482005-p8:asia-south2:portfolio-db']}"
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
                session['user_id'] = user['id']
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
    return render_template(
        'dashboard.html',
        transactions=None,
        title=None
    )

# Route: Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.context_processor
def inject_gold():
    gold_investments = []

    if 'user_id' in session:
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM gold_investments WHERE user_id = %s",
                (session['user_id'],)
            )
            gold_investments = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception:
            gold_investments = []

    return dict(
        gold_exists=(len(gold_investments) > 0),
        gold_investments=gold_investments
    )
@app.context_processor
def inject_other_assets():
    real_estate = []
    cash = []
    private_equity = []

    if 'user_id' in session:
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
            cash_investments = cursor.fetchall()

            cursor.execute(
                "SELECT * FROM private_equity WHERE user_id = %s",
                (session['user_id'],)
            )
            pe_investments = cursor.fetchall()

        except Exception:
            pass
        finally:
            cursor.close()
            conn.close()

    return dict(
        real_estate_exists=len(real_estate) > 0,
        cash_exists=len(cash) > 0,
        private_equity_exists=len(private_equity) > 0,
        real_estate=real_estate,
        cash=cash,
        private_equity= private_equity
    )


# Route: Upload CSV
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
        'cash investments': 'cash'
    }

    table_name = table_map.get(table_name_raw.lower())

    if not file or not table_name:
        flash('Error uploading CSV file', 'error')
        return redirect(request.referrer)

    try:
        stream = io.StringIO(file.stream.read().decode("utf-8-sig"))
        reader = csv.DictReader(stream)

        if not reader.fieldnames:
            flash('Error uploading CSV file', 'error')
            return redirect(request.referrer)

        # Normalize CSV headers
        csv_headers = [h.strip().lower() for h in reader.fieldnames]

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns_info = cursor.fetchall()

        # Normalize DB columns
        db_columns = [col['Field'].lower() for col in columns_info]

        ignored_columns = {'id', 'user_id'}

        # Required = non-null + no default + not ignored
        required_columns = [
            col['Field'].lower()
            for col in columns_info
            if col['Field'].lower() not in ignored_columns
            and col['Null'] == 'NO'
            and col['Default'] is None
        ]

        # Validation
        if (
            not set(required_columns).issubset(csv_headers)
            or not set(csv_headers).issubset(set(db_columns) | ignored_columns)
        ):
            flash('Error uploading CSV file. Columns do not match.', 'error')
            return redirect(request.referrer)

        # Build insert columns
        insert_columns = [h for h in reader.fieldnames if h.strip().lower() in db_columns]

        if 'user_id' in db_columns:
            insert_columns.append('user_id')

        placeholders = ", ".join(["%s"] * len(insert_columns))
        column_names = ", ".join(insert_columns)

        query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"

        for row in reader:
            values = []
            for col in insert_columns:
                if col == 'user_id':
                    values.append(session.get('user_id'))
                else:
                    values.append(row.get(col))

            cursor.execute(query, values)

        conn.commit()
        flash('CSV file successfully uploaded', 'success')

    except Exception as e:
        print(e)
        flash('Error uploading CSV file', 'error')

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(request.referrer)

# Register Blueprints
app.register_blueprint(bank_bp)
app.register_blueprint(fd_bp)
app.register_blueprint(equity_bp)
app.register_blueprint(mf_bp)
app.register_blueprint(pf_bp)
app.register_blueprint(category_mapping_bp)
app.register_blueprint(gold_bp)
app.register_blueprint(real_estate_bp)
app.register_blueprint(cash_bp)
app.register_blueprint(private_equity_bp)

#if __name__ == '__main__':
 #  app.run(host="0.0.0.0",port=8080)
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
