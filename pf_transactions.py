from flask import Blueprint, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error

pf_bp = Blueprint('pf', __name__)

db_config = {
    'user': 'root',
    'password': 'Anshika',
    'host': '127.0.0.1',
    'port': '3306',
    'database': 'portfolioManagement'
}

@pf_bp.route('/pf_transactions', methods=['GET', 'POST'])
def pf_transactions():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')

        query = "SELECT * FROM pf"
        params = []

        if from_date and to_date:
            query += " WHERE DT BETWEEN %s AND %s"
            params.extend([from_date, to_date])

        cursor.execute(query, params)
        transactions = cursor.fetchall()

        return render_template(
            'dashboard.html',
            transactions=transactions,
            title='PF Transactions',
            from_date=from_date,
            to_date=to_date
        )
    except Error as e:
        return f"An error occurred: {e}"
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
fields = [
    {"label": "Date", "name": "DT", "type": "date"},
    {"label": "Narration", "name": "Narration", "type": "text"},
    {"label": "Cheque/Ref No", "name": "CHq_Ref_No", "type": "text"},
    {"label": "Value Date", "name": "Value_Dt", "type": "date"},
    {"label": "Withdrawal Amount", "name": "Withdrawal_Amt", "type": "number", "step": "0.01"},
    {"label": "Deposit Amount", "name": "Deposit_Amt", "type": "number", "step": "0.01"},
    {"label": "Closing Balance", "name": "Closing_Balance", "type": "number", "step": "0.01"},
]
@pf_bp.route('/add_pf_transaction', methods=['GET', 'POST'])
def add_pf_transaction():
    if request.method == 'POST':
        form = request.form
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pf_transaction (DT, Narration, CHq_Ref_No, Value_Dt, Withdrawal_Amt, Deposit_Amt, Closing_Balance)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (form['DT'], form['Narration'], form['CHq_Ref_No'], form['Value_Dt'], form['Withdrawal_Amt'], form['Deposit_Amt'], form['Closing_Balance']))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('pf.pf_transactions'))

    return render_template('add_transaction.html', title='Add PF Transaction', fields=fields, back_url='pf.pf_transactions')