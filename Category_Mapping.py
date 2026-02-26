from flask import Blueprint, render_template, request, redirect, url_for, session
import mysql.connector
import os

# Cloud SQL configuration (Cloud Run compatible)
db_config = {
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASS"],
    "database": os.environ["DB_NAME"],
    "unix_socket": f"/cloudsql/{os.environ['INSTANCE_CONNECTION_NAME']}"
}

category_mapping_bp = Blueprint('category_mapping', __name__)

fields = [
    {"label": "Category", "name": "Category", "type": "text"},
    {"label": "Description", "name": "Description", "type": "text"},
    {"label": "Sub Category", "name": "Sub_Category", "type": "text"}
]


# ============================
# VIEW CATEGORY MAPPING
# ============================
@category_mapping_bp.route('/category_mapping', methods=['GET'])
def category_mapping():
    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        filter_category = request.args.get('filter_category')
        user_id = session.get('user_id')

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
            title='Category Mapping',
            filter_category=filter_category
        )

    except mysql.connector.Error as e:
        return f"Database error: {e}"

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


# ============================
# ADD CATEGORY MAPPING
# ============================
@category_mapping_bp.route('/add_category_mapping', methods=['GET', 'POST'])
def add_category_mapping():

    if request.method == 'POST':
        conn = None
        cursor = None

        try:
            form = request.form
            user_id = session.get('user_id')

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

        except mysql.connector.Error as e:
            return f"Insert error: {e}"

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


# ============================
# EDIT CATEGORY MAPPING
# ============================
@category_mapping_bp.route('/edit_category_mapping', methods=['GET', 'POST'])
def edit_category_mapping():

    if request.method == 'POST':
        conn = None
        cursor = None

        try:
            orig_description = request.form['orig_description']
            new_category = request.form['Category']
            new_sub_category = request.form['Sub_Category']
            user_id = session.get('user_id')

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

        except mysql.connector.Error as e:
            return f"Update error: {e}"

        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

        return redirect(url_for('category_mapping.category_mapping'))

    # ---------- GET REQUEST ----------
    conn = None
    cursor = None

    try:
        description = request.args.get('description')
        user_id = session.get('user_id')

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT Category, Description, Sub_Category
            FROM Category_Mapping
            WHERE Description=%s AND user_id=%s
        """, (description, user_id))

        transaction = cursor.fetchone()

        if not transaction:
            return "Transaction not found", 404

    except mysql.connector.Error as e:
        return f"Fetch error: {e}"

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

    return render_template(
        'edit_transaction.html',
        transaction=transaction,
        fields=fields,
        title='Edit Category Mapping',
        back_url='category_mapping.category_mapping'
    )
