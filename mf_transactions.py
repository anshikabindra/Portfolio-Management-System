from flask import Blueprint, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error

mf_bp = Blueprint('mf', __name__)

db_config = {
    'user': 'root',
    'password': 'Anshika',
    'host': '127.0.0.1',
    'port': '3306',
    'database': 'portfolioManagement'
}

@mf_bp.route('/mf_transactions', methods=['GET', 'POST'])
def mf_transactions():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')

        query = "SELECT * FROM Mutual_Fund_transactions"
        params = []

        if from_date and to_date:
            query += " WHERE Transaction_date BETWEEN %s AND %s"
            params.extend([from_date, to_date])

        cursor.execute(query, params)
        transactions = cursor.fetchall()

        return render_template(
            'dashboard.html',
            transactions=transactions,
            title='Mutual Fund Transactions',
            from_date=from_date,
            to_date=to_date
        )
    except Error as e:
        return f"An error occurred: {e}"
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

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
    if request.method == 'POST':
        form = request.form
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Mutual_Fund_transactions (
                Company_name, ISIN_number, Transaction_date,
                Transaction_rate, Quantity, Transaction_type
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            form['Company_name'],
            form['ISIN_number'],
            form['Transaction_date'],
            form['Transaction_rate'],
            form['Quantity'],
            form['Transaction_type']
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('mf.mf_transactions'))

    return render_template(
        'add_transaction.html',
        title='Add Mutual Fund Transaction',
        fields=fields,
        back_url='mf.mf_transactions'
    )
