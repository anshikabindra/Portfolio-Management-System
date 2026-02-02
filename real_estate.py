from flask import Blueprint, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error

real_estate_bp = Blueprint('real_estate', __name__)

db_config = {
    'user': 'root',
    'password': 'Anshika',
    'host': '127.0.0.1',
    'port': '3306',
    'database': 'portfolioManagement'
}

fields = [
    {"label": "Investment Name", "name": "Investment_name", "type": "text"},
    {"label": "Invested Value", "name": "Invested_value", "type": "number", "step": "0.01"},
    {"label": "Date of Investment", "name": "Date_of_investment", "type": "date"},
    {"label": "Current Value", "name": "Current_value", "type": "number", "step": "0.01"}
]

@real_estate_bp.route('/real_estate', methods=['GET', 'POST'])
def real_estate():
    try:
        # ✅ SAFETY CHECK (does not change functionality)
        if 'user_id' not in session:
            return render_template(
                'dashboard.html',
                transactions=[],
                title='Real Estate'
            )

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM real_estate WHERE user_id = %s"
        cursor.execute(query, (session['user_id'],))
        transactions = cursor.fetchall()

        return render_template(
            'dashboard.html',
            transactions=transactions,
            title='Real Estate'
        )
    except Error as e:
        return f"An error occurred: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@real_estate_bp.route('/add_real_estate', methods=['GET', 'POST'])
def add_real_estate():
    if request.method == 'POST':
        form = request.form
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

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
                session['user_id']
            ))

            conn.commit()
        except Error as e:
            return f"An error occurred: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return redirect(url_for('real_estate.real_estate'))

    return render_template(
        'add_transaction.html',
        title='Add Real Estate',
        fields=fields,
        back_url='real_estate.real_estate'
    )
