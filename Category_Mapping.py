from flask import Blueprint, render_template, request, redirect, url_for
import mysql.connector
from decimal import Decimal
from datetime import datetime

# DB Config
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Anshika',
    'database': 'portfolioManagement'
}
fields = [
    {"label": "Category", "name": "Category", "type": "text"},
    {"label": "Description", "name": "Description", "type": "text"},
    {"label": "Sub Category", "name": "Sub_Category", "type": "text"}
]
category_mapping_bp = Blueprint('category_mapping', __name__)

@category_mapping_bp.route('/category_mapping', methods=['GET', 'POST'])
def category_mapping():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        filter_category = request.args.get('filter_category')

        query = "SELECT * FROM Category_Mapping WHERE 1=1"
        params = []

        if filter_category:
            if filter_category.lower() == 'none':
                query += " AND (Category IS NULL OR Category = '')"
            else:
                query += " AND Category LIKE %s"
                params.append(f"%{filter_category}%")

        cursor.execute(query, params)
        transactions = cursor.fetchall()

        return render_template(
            'dashboard.html',
            transactions=transactions,
            title='Category_Mapping',
        )
    except mysql.connector.Error as e:
        return f"An error occurred: {e}"
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@category_mapping_bp.route('/add_category_mapping', methods=['GET', 'POST'])
def add_category_mapping():
    if request.method == 'POST':
        form = request.form

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Category_Mapping (
                    Category, Description, Sub_Category
                ) VALUES (%s, %s, %s)
            """, (
                form['Category'],
                form['Description'],
                form['Sub_Category'],
            ))
            conn.commit()
        except mysql.connector.Error as e:
            return f"An error occurred while inserting: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

        return redirect(url_for('category_mapping.category_mapping'))

    return render_template(
        'add_transaction.html',
        title='Add Category_Mapping',
        fields=fields,
        back_url='category_mapping.category_mapping'
    )

@category_mapping_bp.route('/edit_category_mapping', methods=['GET', 'POST'])
def edit_category_mapping():
    if request.method == 'POST':
        orig_description = request.form['orig_description']

        # Get updated values from form
        new_category = request.form['Category']
        new_sub_category = request.form['Sub_Category']

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # Update based on original composite key
            cursor.execute("""
                UPDATE Category_Mapping
                SET Category=%s, Sub_Category=%s
                WHERE Description=%s
            """, (
                new_category, new_sub_category, orig_description
            ))
            conn.commit()
        except mysql.connector.Error as e:
            return f"Error during update: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

        return redirect(url_for('category_mapping.category_mapping'))

    # GET request
    description = request.args.get('description')

    # Fetch the latest data from the database using description
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT Category, Description, Sub_Category
            FROM Category_Mapping
            WHERE Description = %s
        """, (description,))
        transaction = cursor.fetchone()

        if not transaction:
            return "Transaction not found", 404

    except mysql.connector.Error as e:
        return f"Error fetching transaction: {e}"
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

    return render_template(
        'edit_transaction.html',
        transaction=transaction,
        fields=fields,
        title='Edit Category_Mapping',
        back_url='category_mapping.category_mapping'
    )
