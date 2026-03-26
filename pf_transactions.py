from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error

pf_bp = Blueprint('pf', __name__)

# --- NEW AIVEN CLOUD DB CONFIG --- #
db_config = {
    'user': 'avnadmin',
    'password': 'AVNS_SRtc5d4cDCrezjU_70x',
    'host': 'portfolio-db-bindraanshika-32d.i.aivencloud.com',
    'port': 26174,  # Fixed: Port should be an integer
    'database': 'defaultdb',
    'ssl_disabled': False  # Aiven requires SSL connection
}

@pf_bp.route('/pf_transactions', methods=['GET', 'POST'])
def pf_transactions():
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
            title='PF Transactions', # Triggers {% elif 'PF' in title %} in dashboard
            from_date=from_date,
            to_date=to_date
        )
    except Error as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for('dashboard'))
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
]

@pf_bp.route('/add_pf_transaction', methods=['GET', 'POST'])
def add_pf_transaction():
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

            dt = form.get('DT') or None
            narration = form.get('Narration') or None
            chq_ref_no = form.get('CHq_Ref_No') or None
            value_dt = form.get('Value_Dt') or None
            withdrawal = float(form.get('Withdrawal_Amt')) if form.get('Withdrawal_Amt') else 0.0
            deposit = float(form.get('Deposit_Amt')) if form.get('Deposit_Amt') else 0.0
            closing = float(form.get('Closing_Balance')) if form.get('Closing_Balance') else 0.0

            cursor.execute("""
                INSERT INTO pf (DT, Narration, CHq_Ref_No, Value_Dt, Withdrawal_Amt, Deposit_Amt, Closing_Balance, user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (dt, narration, chq_ref_no, value_dt, withdrawal, deposit, closing, user_id))

            conn.commit()
            flash('PF transaction added successfully!', 'success')
        except Error as e:
            flash(f"Error inserting record: {e}", "error")
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

        return redirect(url_for('pf.pf_transactions'))

    return render_template(
        'add_transaction.html',
        title='Add PF Transaction',
        fields=fields,
        back_url='pf.pf_transactions'
    )
