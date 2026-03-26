from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector
from decimal import Decimal
from datetime import datetime

# Blueprint setup
fd_bp = Blueprint('fd', __name__)

# --- NEW AIVEN CLOUD DB CONFIG --- #
db_config = {
    'user': 'avnadmin',
    'password': 'AVNS_SRtc5d4cDCrezjU_70x',
    'host': 'portfolio-db-bindraanshika-32d.i.aivencloud.com',
    'port': 26174,  # Fixed: Port should be an integer
    'database': 'defaultdb',
    'ssl_disabled': False  # Aiven requires SSL connection
}

fields = [
    {"label": "Portfolio Name", "name": "Portfolio_name", "type": "text"},
    {"label": "FD number", "name": "FD_number", "type": "number"},
    {"label": "Principal Amount", "name": "Principal_amt", "type": "number", "step": "0.01"},
    {"label": "Start date", "name": "Start_date", "type": "date"},
    {"label": "Rate (%)", "name": "Rate", "type": "number", "step": "0.01"},
    {"label": "Opening Balance", "name": "Opening_Balance", "type": "number", "step": "0.01"},
    {"label": "Current value", "name": "Current_value", "type": "number", "step": "0.01"},
    {"label": "Maturity date", "name": "Maturity_date", "type": "date"}
]

@fd_bp.route('/fd_transactions', methods=['GET', 'POST'])
def fd_transactions():
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

        query = "SELECT * FROM fd_transactions WHERE user_id = %s"
        params = [user_id]

        if from_date and to_date:
            query += " AND Start_date BETWEEN %s AND %s"
            params.extend([from_date, to_date])

        cursor.execute(query, params)
        transactions = cursor.fetchall()

        return render_template(
            'dashboard.html',
            transactions=transactions,
            title='FD Transactions', # Triggers {% elif 'FD' in title %}
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

@fd_bp.route('/add_fd_transaction', methods=['GET', 'POST'])
def add_fd_transaction():
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

            # Parse values safely
            start_date = form['Start_date'] or None
            maturity_date = form['Maturity_date'] or None
            rate = Decimal(form['Rate']) if form['Rate'] else None
            principal = float(form['Principal_amt']) if form['Principal_amt'] else 0.0
            opening = float(form['Opening_Balance']) if form['Opening_Balance'] else 0.0
            current = float(form['Current_value']) if form['Current_value'] else 0.0

            cursor.execute("""
                INSERT INTO fd_transactions (
                    Portfolio_name, FD_number, Principal_amt, Start_date, Rate, 
                    Opening_Balance, Current_value, Maturity_date, user_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                form['Portfolio_name'],
                form['FD_number'],
                principal,
                start_date,
                rate,
                opening,
                current,
                maturity_date,
                user_id
            ))

            conn.commit()
            flash('FD transaction added successfully!', 'success')
        except mysql.connector.Error as e:
            flash(f"Error inserting record: {e}", "error")
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

        return redirect(url_for('fd.fd_transactions'))

    return render_template(
        'add_transaction.html',
        title='Add FD Transaction',
        fields=fields,
        back_url='fd.fd_transactions'
    )
