from flask import Blueprint, render_template, request, redirect, url_for, session   # 🔹 ADDED session
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

        # 🔹 NEW: logged in user id
        user_id = session.get('user_id')

        query = "SELECT * FROM pf WHERE user_id = %s"
        params = [user_id]

        if from_date and to_date:
            query += " AND DT BETWEEN %s AND %s"
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
    except mysql.connector.Error as e:
        return f"An error occurred: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

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
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # 🔹 NEW: logged in user id
            user_id = session.get('user_id')

            # Parse safely
            dt = form.get('DT') or None
            narration = form.get('Narration') or None
            chq_ref_no = form.get('CHq_Ref_No') or None
            value_dt = form.get('Value_Dt') or None

            # Convert numeric fields
            withdrawal = int(form.get('Withdrawal_Amt')) if form.get('Withdrawal_Amt') else 0
            deposit = float(form.get('Deposit_Amt')) if form.get('Deposit_Amt') else 0.0
            closing = float(form.get('Closing_Balance')) if form.get('Closing_Balance') else 0.0

            cursor.execute("""
                INSERT INTO pf (DT, Narration, CHq_Ref_No, Value_Dt, Withdrawal_Amt, Deposit_Amt, Closing_Balance, user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (dt, narration, chq_ref_no, value_dt, withdrawal, deposit, closing, user_id))

            conn.commit()
        except Error as e:
            return f"An error occurred while inserting: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

        return redirect(url_for('pf.pf_transactions'))

    return render_template(
        'add_transaction.html',
        title='Add PF Transaction',
        fields=fields,
        back_url='pf.pf_transactions'
    )
