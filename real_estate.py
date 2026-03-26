from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error

real_estate_bp = Blueprint('real_estate', __name__)

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
    {"label": "Invested Value", "name": "Invested_value", "type": "number", "step": "0.01"},
    {"label": "Date of Investment", "name": "Date_of_investment", "type": "date"},
    {"label": "Current Value", "name": "Current_value", "type": "number", "step": "0.01"}
]

@real_estate_bp.route('/real_estate', methods=['GET', 'POST'])
def real_estate():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        user_id = session.get('user_id')

        query = "SELECT * FROM real_estate WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        transactions = cursor.fetchall()

        return render_template(
            'dashboard.html',
            transactions=transactions,
            title='Real Estate'
        )
    except Error as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for('dashboard'))
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


@real_estate_bp.route('/add_real_estate', methods=['GET', 'POST'])
def add_real_estate():
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
                INSERT INTO real_estate (
                    Investment_name, Invested_value, Date_of_investment,
                    Current_value, user_id
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                form['Investment_name'],
                form['Invested_value'],
                form['Date_of_investment'],
                form['Current_value'],
                user_id
            ))

            conn.commit()
            flash('Real Estate record added successfully!', 'success')
        except Error as e:
            flash(f"Error inserting record: {e}", "error")
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

        return redirect(url_for('real_estate.real_estate'))

    return render_template(
        'add_transaction.html',
        title='Add Real Estate',
        fields=fields,
        back_url='real_estate.real_estate'
    )
