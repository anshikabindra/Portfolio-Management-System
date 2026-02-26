from flask import Blueprint, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error

equity_bp = Blueprint('equity', __name__)

import os

# MySQL configuration
#db_config = {
#   'user': 'root',
#   'password': 'Anshika',
#   'host': '127.0.0.1',
#   'port': '3306',
#   'database': 'portfolioManagement'
#}

db_config = {
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASS"],
    "database": os.environ["DB_NAME"],
    "unix_socket": f"/cloudsql/{os.environ['INSTANCE_CONNECTION_NAME']}"
}

# Form fields for equity_transactions table
fields = [
    {"label": "Company Name", "name": "Company_name", "type": "text"},
    {"label": "ISIN Number", "name": "ISIN_number", "type": "number"},
    {"label": "Transaction Date", "name": "Transaction_date", "type": "date"},
    {"label": "Transaction Rate", "name": "Transaction_rate", "type": "number", "step": "0.01"},
    {"label": "Quantity", "name": "Quantity", "type": "number"},
    {"label": "Transaction Type", "name": "Transaction_type", "type": "text"}
]

# Route to view transactions
@equity_bp.route('/equity_transactions', methods=['GET', 'POST'])
def equity_transactions():
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')

        query = "SELECT * FROM equity_transactions WHERE user_id = %s"
        params = [session.get('user_id')]

        if from_date and to_date:
            query += " AND Transaction_date BETWEEN %s AND %s"
            params.extend([from_date, to_date])

        cursor.execute(query, params)
        transactions = cursor.fetchall()

        return render_template(
            'dashboard.html',
            transactions=transactions,
            title='Equity Transactions',
            from_date=from_date,
            to_date=to_date
        )
    except mysql.connector.Error as e:
        return f"An error occurred: {e}"
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


# Route to add transaction
@equity_bp.route('/add_equity_transaction', methods=['GET', 'POST'])
def add_equity_transaction():
    if request.method == 'POST':
        form = request.form
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO equity_transactions (
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
                session.get('user_id')
            ))

            conn.commit()
        except Error as e:
            return f"An error occurred: {e}"
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

        return redirect(url_for('equity.equity_transactions'))

    return render_template(
        'add_transaction.html',
        title='Add Equity Transaction',
        fields=fields,
        back_url='equity.equity_transactions'
    )
