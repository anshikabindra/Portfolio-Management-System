import os

# db_config = {
#    "user": os.environ["DB_USER"],
#    "password": os.environ["DB_PASS"],
#    "database": os.environ["DB_NAME"],
#    "unix_socket": f"/cloudsql/{os.environ['INSTANCE_CONNECTION_NAME']}"
# }

# Added jsonify to the Flask import line to support chatbot responses
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
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

            # This triggers the green "Successfully Registered" message on the login page
            flash('Successfully Registered! Please login.', 'success')
            return redirect(url_for('login'))

        except mysql.connector.IntegrityError:
            # Added 'error' category for red styling
            flash('Email already exists.', 'error')
        except Error as e:
            # Added 'error' category for red styling
            flash(f"Database error: {e}", 'error')

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


# ---------------- UNIFIED CONTEXT PROCESSOR ---------------- #

@app.context_processor
def inject_active_assets():
    active_assets = []
    gold_investments = []
    real_estate = []
    cash = []
    private_equity = []

    if 'user_id' in session:
        conn = cursor = None
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            user_id = session['user_id']

            # Check Gold
            cursor.execute("SELECT * FROM gold_investments WHERE user_id = %s", (user_id,))
            gold_investments = cursor.fetchall()
            if gold_investments: active_assets.append('Gold')

            # Check Real Estate
            cursor.execute("SELECT * FROM real_estate WHERE user_id = %s", (user_id,))
            real_estate = cursor.fetchall()
            if real_estate: active_assets.append('Real Estate')

            # Check Cash
            cursor.execute("SELECT * FROM cash_investments WHERE user_id = %s", (user_id,))
            cash = cursor.fetchall()
            if cash: active_assets.append('Cash')

            # Check Private Equity
            cursor.execute("SELECT * FROM private_equity WHERE user_id = %s", (user_id,))
            private_equity = cursor.fetchall()
            if private_equity: active_assets.append('Private Equity')

        except Exception:
            pass
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    return dict(
        active_assets=active_assets,
        gold_investments=gold_investments,
        gold_exists=len(gold_investments) > 0,
        real_estate=real_estate,
        real_estate_exists=len(real_estate) > 0,
        cash=cash,
        cash_exists=len(cash) > 0,
        private_equity=private_equity,
        private_equity_exists=len(private_equity) > 0
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
        'mutual fund transactions': 'Mutual_Fund_transactions',
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
        csv_headers = [h.strip().lower() for h in reader.fieldnames] if reader.fieldnames else []

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Get Database columns
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns_info = cursor.fetchall()
        db_columns = [col['Field'].lower() for col in columns_info]

        # Columns that MUST be in the CSV (excluding auto-managed fields)
        required_db_columns = [col for col in db_columns if col not in ['id', 'user_id']]

        # VALIDATION: Ensure CSV headers match the required DB columns exactly
        is_match = True
        if len(csv_headers) != len(required_db_columns):
            is_match = False
        else:
            for header in csv_headers:
                if header not in required_db_columns:
                    is_match = False
                    break

        if not is_match:
            flash("File doesn't match columns", "error")
            return redirect(request.referrer)

        # Process insertion if columns match
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
        flash('File uploaded successfully', 'success')

    except Exception as e:
        print(f"CSV Upload Error: {e}")
        flash('Error uploading CSV file', 'error')

    finally:
        if cursor: cursor.close()
        if conn: conn.close()

    return redirect(request.referrer)


# ---------------- CHATBOT TRANSACTION TERMINAL ---------------- #

@app.route('/chatbot', methods=['POST'])
def chatbot():
    if 'user_id' not in session:
        return jsonify({"reply": "Please log in to your account first so I can access your secure ledger."})

    data = request.get_json() or {}
    user_message = data.get('message', '').strip()
    user_message_lower = user_message.lower()
    user_id = session['user_id']

    # Blueprint table structure mapping reference
    table_map = {
        'bank': 'bank_transaction',
        'fd': 'fd_transactions',
        'equity': 'equity_transactions',
        'mutual fund': 'Mutual_Fund_transactions',
        'mf': 'Mutual_Fund_transactions',
        'pf': 'pf',
        'gold': 'gold_investments',
        'real estate': 'real_estate',
        'cash': 'cash_investments',
        'private equity': 'private_equity'
    }

    # 1. HANDLE DELETE COMMAND BY NARRATION/NAME (e.g., delete bank | Salary)
    if user_message_lower.startswith('delete '):
        if '|' in user_message:
            parts = [p.strip() for p in user_message.split('|')]
            cmd_header = parts[0].split()
            if len(cmd_header) >= 2:
                asset_key = " ".join(cmd_header[1:]).lower()
                target_identifier = parts[1]
                table_name = table_map.get(asset_key)

                if table_name:
                    # Dynamically match identifier column name based on asset type
                    ident_column = 'investment_name' if asset_key in ['gold', 'real estate', 'cash', 'private equity'] else 'Narration'
                    if asset_key in ['equity', 'mutual fund', 'mf']:
                        ident_column = 'Company_name'
                    elif asset_key == 'fd':
                        ident_column = 'Portfolio_name'

                    try:
                        conn = mysql.connector.connect(**db_config)
                        cursor = conn.cursor()
                        # Secures action via user_id, targets rows via Narration/Name
                        query = f"DELETE FROM {table_name} WHERE {ident_column} = %s AND user_id = %s"
                        cursor.execute(query, (target_identifier, user_id))
                        conn.commit()
                        affected = cursor.rowcount
                        cursor.close()
                        conn.close()

                        if affected > 0:
                            return jsonify({"reply": f"✅ Successfully deleted records matching '{target_identifier}' from your {asset_key.upper()} ledger."})
                        else:
                            return jsonify({"reply": f"❌ No records found matching '{target_identifier}' under your profile."})
                    except Exception as e:
                        return jsonify({"reply": f"❌ Error deleting row: {str(e)}"})

        return jsonify({"reply": "💡 **Delete Syntax:** `delete [asset_type] | [Narration/Name]` (Example: `delete bank | ATM Cash Run` or `delete gold | Bullion Coin`)"})

    # 2. HANDLE MODIFY COMMAND BY NARRATION/NAME (e.g., modify bank | Old Text | narration | New Text)
    if user_message_lower.startswith('modify '):
        if '|' in user_message:
            parts = [p.strip() for p in user_message.split('|')]
            cmd_header = parts[0].split()
            if len(cmd_header) >= 2 and len(parts) >= 4:
                asset_key = " ".join(cmd_header[1:]).lower()
                target_identifier = parts[1]
                field = parts[2].lower()
                new_value = parts[3]
                table_name = table_map.get(asset_key)

                if table_name:
                    ident_column = 'investment_name' if asset_key in ['gold', 'real estate', 'cash', 'private equity'] else 'Narration'
                    if asset_key in ['equity', 'mutual fund', 'mf']:
                        ident_column = 'Company_name'
                    elif asset_key == 'fd':
                        ident_column = 'Portfolio_name'

                    # Field naming map aligning with your exact database casings
                    field_map = {
                        'narration': 'Narration',
                        'company': 'Company_name',
                        'quantity': 'Quantity',
                        'qty': 'Quantity',
                        'rate': 'Transaction_rate',
                        'name': 'investment_name',
                        'chq_ref_no': 'CHq_Ref_No',
                        'bank_name': 'bank_name'
                    }
                    actual_field = field_map.get(field, field)

                    # Manage Withdrawal / Deposit distribution routing dynamically for simple text allocations
                    if asset_key in ['bank', 'pf'] and field == 'amount':
                        try:
                            val = float(new_value)
                            if val >= 0:
                                query = f"UPDATE {table_name} SET Deposit_Amt = %s, Withdrawal_Amt = 0 WHERE {ident_column} = %s AND user_id = %s"
                            else:
                                query = f"UPDATE {table_name} SET Withdrawal_Amt = %s, Deposit_Amt = 0 WHERE {ident_column} = %s AND user_id = %s"
                                val = abs(val)
                            new_value = val
                        except ValueError:
                            return jsonify({"reply": "❌ Amount parameters must remain purely numeric numbers."})
                    else:
                        query = f"UPDATE {table_name} SET {actual_field} = %s WHERE {ident_column} = %s AND user_id = %s"

                    try:
                        conn = mysql.connector.connect(**db_config)
                        cursor = conn.cursor()
                        cursor.execute(query, (new_value, target_identifier, user_id))
                        conn.commit()
                        affected = cursor.rowcount
                        cursor.close()
                        conn.close()

                        if affected > 0:
                            return jsonify({"reply": f"✅ Successfully updated entries matching '{target_identifier}' in {asset_key.upper()} ({field} -> {new_value})."})
                        else:
                            return jsonify({"reply": f"❌ No matching records found under your account profile lines."})
                    except Exception as e:
                        return jsonify({"reply": f"❌ Database mutation error: {str(e)}"})

        return jsonify({"reply": "💡 **Modify Syntax:** `modify [asset] | [Current Narration/Name] | [Field] | [New Value]` (Example: `modify bank | Old Salary | narration | Updated Salary`)"})

    # 3. HANDLE ADD COMMAND USING PIPE SEPARATORS
    if user_message_lower.startswith('add '):
        if '|' in user_message:
            parts = [p.strip() for p in user_message.split('|')]
            cmd_header = parts[0].split()
            if len(cmd_header) >= 2:
                asset_key = " ".join(cmd_header[1:]).lower()
                table_name = table_map.get(asset_key)

                # Handle Banking & Provident Fund Ledgers matching exact columns
                if table_name in ['bank_transaction', 'pf'] and len(parts) >= 3:
                    narration = parts[1]
                    try:
                        amt = float(parts[2])
                        dep = amt if amt >= 0 else 0
                        wit = abs(amt) if amt < 0 else 0

                        conn = mysql.connector.connect(**db_config)
                        cursor = conn.cursor()
                        cursor.execute(
                            f"INSERT INTO {table_name} (DT, Narration, Deposit_Amt, Withdrawal_Amt, Value_Dt, user_id) VALUES (CURDATE(), %s, %s, %s, CURDATE(), %s)",
                            (narration, dep, wit, user_id)
                        )
                        conn.commit()
                        cursor.close()
                        conn.close()
                        return jsonify({"reply": f"✅ Posted transaction to {asset_key.upper()}: '{narration}' (₹{amt})."})
                    except Exception as e:
                        return jsonify({"reply": f"❌ Insertion error: {str(e)}"})

                # Handle Gold Commodities
                elif table_name == 'gold_investments' and len(parts) >= 4:
                    name = parts[1]
                    try:
                        rate = float(parts[2])
                        qty = float(parts[3])

                        conn = mysql.connector.connect(**db_config)
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO gold_investments (investment_name, value_per_gram, quantity, investment_date, user_id) VALUES (%s, %s, %s, CURDATE(), %s)",
                            (name, rate, qty, user_id)
                        )
                        conn.commit()
                        cursor.close()
                        conn.close()
                        return jsonify({"reply": f"✅ Logged commodity position to GOLD: '{name}' ({qty}g)."})
                    except Exception as e:
                        return jsonify({"reply": f"❌ Commodity post error: {str(e)}"})

                # Handle Asset Markets (Equities / Mutual Funds)
                elif table_name in ['equity_transactions', 'Mutual_Fund_transactions'] and len(parts) >= 5:
                    comp = parts[1]
                    try:
                        rate = float(parts[2])
                        qty = int(parts[3])
                        tx_type = parts[4]

                        conn = mysql.connector.connect(**db_config)
                        cursor = conn.cursor()
                        cursor.execute(
                            f"INSERT INTO {table_name} (Company_name, Transaction_date, Transaction_rate, Quantity, Transaction_type, user_id) VALUES (%s, CURDATE(), %s, %s, %s, %s)",
                            (comp, rate, qty, tx_type, user_id)
                        )
                        conn.commit()
                        cursor.close()
                        conn.close()
                        return jsonify({"reply": f"✅ Recorded security transaction inside {asset_key.upper()} registry."})
                    except Exception as e:
                        return jsonify({"reply": f"❌ Security tracking failure: {str(e)}"})

        return jsonify({"reply": "💡 **Add Command Formats (Use '|' as separators):**<br>"
                                 "• `add bank | Salary Input | 45000`<br>"
                                 "• `add bank | ATM Cash Run | -2000`<br>"
                                 "• `add gold | Bullion Coin | 6300 | 10`<br>"
                                 "• `add equity | Tata Motors | 920 | 25 | Buy`"})

    return jsonify({"reply": "I am ready for transactions! Use commands like `add bank | text | amt`, `modify bank | current_narration | field | new_val`, or `delete bank | narration`."})


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
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
