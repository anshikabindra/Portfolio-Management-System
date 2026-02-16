from flask import Blueprint, render_template, request, redirect, url_for, session   # 🔹 ADDED session
import mysql.connector
from mysql.connector import Error

gold_bp = Blueprint('gold', __name__)

db_config = {
    'user': 'root',
    'password': 'Anshika',
    'host': '127.0.0.1',
    'port': '3306',
    'database': 'portfolioManagement'
}

fields = [
    {"label": "investment name", "name": "investment_name", "type": "text"},
    {"label": "value per gram (₹)", "name": "value_per_gram", "type": "number", "step": "0.01"},
    {"label": "quantity (grams)", "name": "quantity", "type": "number", "step": "0.01"},
    {"label": "investment date", "name": "investment_date", "type": "date"}
]

@gold_bp.route('/gold_transactions', methods=['GET'])
def gold_transactions():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # 🔹 NEW: filter by logged-in user
        user_id = session.get('user_id')

        cursor.execute("SELECT * FROM gold_investments WHERE user_id = %s", (user_id,))
        transactions = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template('dashboard.html', transactions=transactions, title='Gold Investments')

@gold_bp.route('/add_gold_transaction', methods=['GET', 'POST'])
def add_gold_transaction():
    if request.method == 'POST':
        form = request.form
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
        except Error as e:
            return f"An error occurred while inserting: {e}"
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('gold.gold_transactions'))

    return render_template(
        'add_transaction.html',
        title='Add Gold Investment',
        fields=fields,
        back_url='gold.gold_transactions'
    )
