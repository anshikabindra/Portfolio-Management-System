from flask import Blueprint, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error

private_equity_bp = Blueprint('private_equity', __name__)

db_config = {
    'user': 'root',
    'password': 'Anshika',
    'host': '127.0.0.1',
    'port': '3306',
    'database': 'portfolioManagement'
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
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM private_equity WHERE user_id = %s"
        cursor.execute(query, (session['user_id'],))
        transactions = cursor.fetchall()

        return render_template(
            'dashboard.html',
            transactions=transactions,
            title='Private Equity'
        )
    except Error as e:
        return f"An error occurred: {e}"
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@private_equity_bp.route('/add_private_equity', methods=['GET', 'POST'])
def add_private_equity():
    if request.method == 'POST':
        form = request.form
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

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
                session['user_id']
            ))

            conn.commit()
        except Error as e:
            return f"An error occurred: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

        return redirect(url_for('private_equity.private_equity'))

    return render_template(
        'add_transaction.html',
        title='Add Private Equity',
        fields=fields,
        back_url='private_equity.private_equity'
    )
