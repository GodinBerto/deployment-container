from flask import Blueprint, request, jsonify, session
from database import db_connection
from wrapper.role_required import role_required         

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route("/cards", methods=["GET"])
def get_card_data():
    conn, cursor = db_connection()
    
    # Fetch total items
    cursor.execute("SELECT COUNT(*) FROM Items")
    total_items = cursor.fetchone()[0]
    
    # Fetch issued items (assuming issued items have stock_quantity < original quantity, adjust as needed)
    cursor.execute("SELECT COUNT(*) FROM Items WHERE stock_quantity < (SELECT MAX(stock_quantity) FROM Items)")
    issued_items = cursor.fetchone()[0]
    
    # Fetch registered staff
    cursor.execute("SELECT COUNT(*) FROM Users WHERE role IN ('Admin', 'Staff')")
    registered_staff = cursor.fetchone()[0]
    
    # Fetch total departments
    cursor.execute("SELECT COUNT(*) FROM Department")
    total_departments = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        "Total Items": total_items,
        "Issued Items": issued_items,
        "Registered Staff": registered_staff,
        "Department": total_departments
    })


@dashboard_bp.route('/monthlyitems', methods=['GET'])
def get_monthly_item_totals():
    conn, cursor = db_connection()

    monthly_counts = [0] * 12

    query = """
        SELECT strftime('%m', created_at) AS month, COUNT(*) AS total_items
        FROM Items
        GROUP BY month
    """

    cursor.execute(query)
    results = cursor.fetchall()

    for row in results:
        month_index = int(row["month"]) - 1  # Convert "01" -> 1
        monthly_counts[month_index] = row["total_items"] if row["total_items"] else 0

    conn.close()

    return jsonify({"MonthlyItems": monthly_counts})