from flask import Blueprint, render_template, request, redirect, url_for, session   # 🔹 ADDED session
import mysql.connector
from decimal import Decimal
from datetime import datetime

# DB Config
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Anshika',
    'database': 'portfolioManagement'
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

fd_bp = Blueprint('fd', __name__)

@fd_bp.route('/fd_transactions', methods=['GET', 'POST'])
def fd_transactions():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')

        # 🔹 NEW: get logged-in user id
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
            title='FD Transactions',
            from_date=from_date,
            to_date=to_date
        )
    except mysql.connector.Error as e:
        return f"An error occurred: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



@fd_bp.route('/add_fd_transaction', methods=['GET', 'POST'])
def add_fd_transaction():
    if request.method == 'POST':
        form = request.form

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # 🔹 NEW: get logged-in user id
            user_id = session.get('user_id')

            # Parse values safely
            start_date = form['Start_date'] or None
            maturity_date = form['Maturity_date'] or None

            # Convert to correct formats
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
        except mysql.connector.Error as e:
            return f"An error occurred while inserting: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

        return redirect(url_for('fd.fd_transactions'))

    return render_template(
        'add_transaction.html',
        title='Add FD Transaction',
        fields=fields,
        back_url='fd.fd_transactions'
    )
