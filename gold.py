from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error

gold_bp = Blueprint('gold', __name__)

# --- NEW AIVEN CLOUD DB CONFIG --- #
db_config = {
    'user': 'avnadmin',
    'password': 'AVNS_SRtc5d4cDCrezjU_70x',
    'host': 'portfolio-db-bindraanshika-32d.i.aivencloud.com',
    'port': 26174,
    'database': 'defaultdb',
    'ssl_disabled': False
}

fields = [
    {"label": "investment name", "name": "investment_name", "type": "text"},
    {"label": "value per gram (₹)", "name": "value_per_gram", "type": "number", "step": "0.01"},
    {"label": "quantity (grams)", "name": "quantity", "type": "number", "step": "0.01"},
    {"label": "investment date", "name": "investment_date", "type": "date"}
]


@gold_bp.route('/gold_transactions', methods=['GET'])
def gold_transactions():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        user_id = session.get('user_id')

        cursor.execute("SELECT * FROM gold_investments WHERE user_id = %s", (user_id,))
        transactions = cursor.fetchall()

        return render_template(
            'dashboard.html',
            transactions=transactions,
            title='Gold Investments'  # NOTE: Ensure dashboard.html has {% elif 'Gold' in title %}
        )
    except Error as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for('dashboard'))
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


@gold_bp.route('/add_gold_transaction', methods=['GET', 'POST'])
def add_gold_transaction():
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
                INSERT INTO gold_investments (investment_name, value_per_gram, quantity, investment_date, user_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                form.get('investment_name'),
                float(form.get('value_per_gram')),
                float(form.get('quantity')),
                form.get('investment_date'),
                user_id
            ))
            conn.commit()
            flash('Gold investment added successfully!', 'success')
        except Error as e:
            flash(f"Error inserting record: {e}", "error")
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

        return redirect(url_for('gold.gold_transactions'))

    return render_template(
        'add_transaction.html',
        title='Add Gold Investment',
        fields=fields,
        back_url='gold.gold_transactions'
    )
