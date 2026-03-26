from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error
import os

# Blueprint setup
category_mapping_bp = Blueprint('category_mapping', __name__, url_prefix='/category_mapping')

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
    {"label": "Category", "name": "Category", "type": "text"},
    {"label": "Description", "name": "Description", "type": "text"},
    {"label": "Sub Category", "name": "Sub_Category", "type": "text"}
]

@category_mapping_bp.route('/', methods=['GET'])
def category_mapping():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        filter_category = request.args.get('filter_category')
        user_id = session['user_id']

        query = "SELECT * FROM Category_Mapping WHERE user_id = %s"
        params = [user_id]

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
            title='Category Mapping', # Trigger for dashboard buttons
            filter_category=filter_category
        )

    except Error as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for('dashboard'))

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

@category_mapping_bp.route('/add', methods=['GET', 'POST'])
def add_category_mapping():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        conn = None
        cursor = None
        try:
            form = request.form
            user_id = session['user_id']

            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO Category_Mapping
                (Category, Description, Sub_Category, user_id)
                VALUES (%s, %s, %s, %s)
            """, (
                form['Category'],
                form['Description'],
                form['Sub_Category'],
                user_id
            ))

            conn.commit()
            flash('Category mapping added successfully!', 'success')

        except Error as e:
            flash(f"Insert error: {e}", "error")

        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

        return redirect(url_for('category_mapping.category_mapping'))

    return render_template(
        'add_transaction.html',
        title='Add Category Mapping',
        fields=fields,
        back_url='category_mapping.category_mapping'
    )

@category_mapping_bp.route('/edit', methods=['GET', 'POST'])
def edit_category_mapping():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        conn = None
        cursor = None
        try:
            orig_description = request.form['orig_description']
            new_category = request.form['Category']
            new_sub_category = request.form['Sub_Category']
            user_id = session['user_id']

            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE Category_Mapping
                SET Category=%s, Sub_Category=%s
                WHERE Description=%s AND user_id=%s
            """, (
                new_category,
                new_sub_category,
                orig_description,
                user_id
            ))

            conn.commit()
            flash('Category mapping updated successfully!', 'success')

        except Error as e:
            flash(f"Update error: {e}", "error")

        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

        return redirect(url_for('category_mapping.category_mapping'))

    conn = None
    cursor = None
    try:
        description = request.args.get('description')
        user_id = session['user_id']

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT Category, Description, Sub_Category
            FROM Category_Mapping
            WHERE Description=%s AND user_id=%s
        """, (description, user_id))

        transaction = cursor.fetchone()

        if not transaction:
            flash("Transaction not found", "error")
            return redirect(url_for('category_mapping.category_mapping'))

    except Error as e:
        flash(f"Fetch error: {e}", "error")
        return redirect(url_for('category_mapping.category_mapping'))

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

    return render_template(
        'add_transaction.html', # Changed to add_transaction for consistency if using shared fields
        transaction=transaction,
        values=transaction, # Passing values to prepopulate the form
        fields=fields,
        title='Edit Category Mapping',
        back_url='category_mapping.category_mapping'
    )
