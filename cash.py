from flask import Blueprint, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error

cash_bp = Blueprint('cash', __name__)

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

fields = [
    {"label": "Investment Name", "name": "Investment_name", "type": "text"},
    {"label": "Invested Value Per Share", "name": "Invested_value_per_share", "type": "number", "step": "0.01"},
    {"label": "No. of Units", "name": "No_of_units", "type": "number"},
    {"label": "Date of Investment", "name": "Date_of_investment", "type": "date"},
    {"label": "Current Value Per Share", "name": "Current_value_per_share", "type": "number", "step": "0.01"}
]

@cash_bp.route('/cash_investments', methods=['GET', 'POST'])
def cash_investments():
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM cash_investments WHERE user_id = %s"
        cursor.execute(query, (session['user_id'],))
        transactions = cursor.fetchall()

        return render_template(
            'dashboard.html',
            transactions=transactions,
            title='Cash Investments'
        )
    except Error as e:
        return f"An error occurred: {e}"
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


@cash_bp.route('/add_cash_investment', methods=['GET', 'POST'])
def add_cash_investment():
    if request.method == 'POST':
        form = request.form
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO cash_investments (
                    Investment_name, Invested_value_per_share, No_of_units,
                    Date_of_investment, Current_value_per_share, user_id
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                form['Investment_name'],
                form['Invested_value_per_share'],
                form['No_of_units'],
                form['Date_of_investment'],
                form['Current_value_per_share'],
                session['user_id']
            ))

            conn.commit()
        except Error as e:
            return f"An error occurred: {e}"
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

        return redirect(url_for('cash.cash_investments'))

    return render_template(
        'add_transaction.html',
        title='Add Cash Investment',
        fields=fields,
        back_url='cash.cash_investments'
    )
