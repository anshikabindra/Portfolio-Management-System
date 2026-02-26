from flask import Blueprint, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error
from flask import session
import os
# Blueprint setup
bank_bp = Blueprint('bank', __name__)

# MySQL configuration
#db_config = {
 #   'user': 'root',
  #  'password': 'Anshika',
   # 'host': '127.0.0.1',
  #  'port': '3306',
   # 'database': 'portfolioManagement'
#}


db_config = {
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASS"],
    "database": os.environ["DB_NAME"],
    "unix_socket": f"/cloudsql/{os.environ['INSTANCE_CONNECTION_NAME']}"
}

@bank_bp.route('/bank_transactions', methods=['GET', 'POST'])
def bank_transactions():
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')

        query = "SELECT * FROM bank_transaction"
        params = []

        if 'user_id' in session:
            query += " WHERE user_id = %s"
            params.append(session['user_id'])

        if from_date and to_date:
            if "WHERE" in query:
                query += " AND DT BETWEEN %s AND %s"
            else:
                query += " WHERE DT BETWEEN %s AND %s"
            params.extend([from_date, to_date])

        cursor.execute(query, params)
        transactions = cursor.fetchall()

        return render_template(
            'dashboard.html',
            transactions=transactions,
            title='Bank Transactions',
            from_date=from_date,
            to_date=to_date
        )

    except Error as e:
        return f"Database error: {e}"

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

fields = [
    {"label": "Date", "name": "DT", "type": "date"},
    {"label": "Narration", "name": "Narration", "type": "text"},
    {"label": "Cheque/Ref No", "name": "CHq_Ref_No", "type": "text"},
    {"label": "Value Date", "name": "Value_Dt", "type": "date"},
    {"label": "Withdrawal Amount", "name": "Withdrawal_Amt", "type": "number", "step": "0.01"},
    {"label": "Deposit Amount", "name": "Deposit_Amt", "type": "number", "step": "0.01"},
    {"label": "Closing Balance", "name": "Closing_Balance", "type": "number", "step": "0.01"},
    {"label": "Bank name", "name": "bank_name", "type": "text"}
]

@bank_bp.route('/add_bank_transaction', methods=['GET', 'POST'])
def add_bank_transaction():
    if request.method == 'POST':
        form = request.form
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        user_id = session.get('user_id')

        cursor.execute("""
            INSERT INTO bank_transaction 
            (DT, Narration, CHq_Ref_No, Value_Dt, Withdrawal_Amt, Deposit_Amt, Closing_Balance, bank_name, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            form['DT'],
            form['Narration'],
            form['CHq_Ref_No'],
            form['Value_Dt'],
            form['Withdrawal_Amt'],
            form['Deposit_Amt'],
            form['Closing_Balance'],
            form['bank_name'],
            user_id
        ))

        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('bank.bank_transactions'))

    return render_template('add_transaction.html', title='Add Bank Transaction', fields=fields, back_url='bank.bank_transactions')



