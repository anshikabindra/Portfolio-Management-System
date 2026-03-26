from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error

private_equity_bp = Blueprint('private_equity', __name__)

# --- NEW AIVEN CLOUD DB CONFIG --- #
db_config = {
    'user': 'avnadmin',
    'password': 'AVNS_SRtc5d4cDCrezjU_70x',
    'host': 'portfolio-db-bindraanshika-32d.i.aivencloud.com',
    'port': 26174, # Fixed: Port should be an integer
    'database': 'defaultdb',
    'ssl_disabled': False  # Aiven requires SSL connection
}

fields = [
    {"label": "Investment Name", "name": "Investment_name", "type": "text"},
    {"label": "Invested Value Per Share", "name": "Invested_value_per_share", "type": "number", "step": "0.01"},
    {"label": "No. of Shares Issued", "name": "No_of_shares_issued", "type": "number"},
    {"label": "Date of Investment", "name": "Date_of_investment", "type": "date"},
    {"label": "Current Value Per Share", "name": "Current_value_per_share", "type": "number", "step": "0.01"}
]

@private_equity_bp.route('/private_equity', methods=['GET', 'POST'])
def private_equity():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        user_id = session.get('user_id')

        query = "SELECT * FROM private_equity WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        transactions = cursor.fetchall()

        return render_template(
            'dashboard.html',
            transactions=transactions,
            title='Private Equity' # Matches 'Equity' in dashboard logic
        )
    except Error as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for('dashboard'))
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


@private_equity_bp.route('/add_private_equity', methods=['GET', 'POST'])
def add_private_equity():
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
                INSERT INTO private_equity (
                    Investment_name, Invested_value_per_share, No_of_shares_issued,
                    Date_of_investment, Current_value_per_share, user_id
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                form['Investment_name'],
                form['Invested_value_per_share'],
                form['No_of_shares_issued'],
                form['Date_of_investment'],
                form['Current_value_per_share'],
                user_id
            ))

            conn.commit()
            flash('Private Equity record added successfully!', 'success')
        except Error as e:
            flash(f"Error inserting record: {e}", "error")
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

        return redirect(url_for('private_equity.private_equity'))

    return render_template(
        'add_transaction.html',
        title='Add Private Equity',
        fields=fields,
        back_url='private_equity.private_equity'
    )
