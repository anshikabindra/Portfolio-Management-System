from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error

mf_bp = Blueprint('mf', __name__)

# --- NEW AIVEN CLOUD DB CONFIG --- #
db_config = {
    'user': 'avnadmin',
    'password': 'AVNS_SRtc5d4cDCrezjU_70x',
    'host': 'portfolio-db-bindraanshika-32d.i.aivencloud.com',
    'port': 26174,
    'database': 'defaultdb',
    'ssl_disabled': False
}

@mf_bp.route('/mf_transactions', methods=['GET', 'POST'])
def mf_transactions():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        user_id = session.get('user_id')

        query = "SELECT * FROM Mutual_Fund_transactions WHERE user_id = %s"
        params = [user_id]

        if from_date and to_date:
            query += " AND Transaction_date BETWEEN %s AND %s"
            params.extend([from_date, to_date])

        cursor.execute(query, params)
        transactions = cursor.fetchall()

        return render_template(
            'dashboard.html',
            transactions=transactions,
            title='Mutual Fund Transactions', # Triggers {% elif 'Mutual Fund' in title %}
            from_date=from_date,
            to_date=to_date
        )
    except mysql.connector.Error as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for('dashboard'))
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

fields = [
    {"label": "Company Name", "name": "Company_name", "type": "text"},
    {"label": "ISIN Number", "name": "ISIN_number", "type": "text"},
    {"label": "Transaction Date", "name": "Transaction_date", "type": "date"},
    {"label": "Transaction Rate", "name": "Transaction_rate", "type": "number", "step": "0.01"},
    {"label": "Quantity", "name": "Quantity", "type": "number"},
    {"label": "Transaction Type", "name": "Transaction_type", "type": "text"},
]

@mf_bp.route('/add_mf_transaction', methods=['GET', 'POST'])
def add_mf_transaction():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        form = request.form
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            user_id = session.get('user_id')

            cursor.execute("""
                INSERT INTO Mutual_Fund_transactions (
                    Company_name, ISIN_number, Transaction_date,
                    Transaction_rate, Quantity, Transaction_type, user_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                form['Company_name'],
                form['ISIN_number'],
                form['Transaction_date'],
                form['Transaction_rate'],
                form['Quantity'],
                form['Transaction_type'],
                user_id
            ))

            conn.commit()
            flash('Mutual Fund transaction added successfully!', 'success')
        except Error as e:
            flash(f"Error inserting record: {e}", "error")
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

        return redirect(url_for('mf.mf_transactions'))

    return render_template(
        'add_transaction.html',
        title='Add Mutual Fund Transaction',
        fields=fields,
        back_url='mf.mf_transactions'
    )
