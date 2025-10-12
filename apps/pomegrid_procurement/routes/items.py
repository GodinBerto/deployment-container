from flask import Blueprint, request, jsonify, session
from database import db_connection
from wrapper.role_required import role_required         

items_bp = Blueprint('items', __name__)

@items_bp.route('/', methods=['GET'])
def get_items():
    try:
        conn, cursor = db_connection()
        cursor.execute("SELECT * FROM items")
        items_rows = cursor.fetchall()
        conn.commit()
        conn.close()

        items = [dict(row) for row in items_rows]
        return jsonify({"message": "Successfully retrieved all items", "data": items, "code": 200}), 200
    except Exception as e:
        return jsonify({"error": str(e)})
    

@items_bp.route('/id=<int:item_id>', methods=['GET'])
def get_item(item_id):
    try:
        conn, cursor = db_connection()
        
        # Fetch the item by ID
        cursor.execute("SELECT * FROM Items WHERE id = ?", (item_id,))
        item_row = cursor.fetchone()
        conn.close()

        if not item_row:
            return jsonify({"error": "Item not found"}), 404

        # Convert the row to a dictionary
        item = dict(item_row)

        return jsonify({"message": "Successfully retrieved item", "data": item, "code": 200}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    

@items_bp.route('/', methods=['POST'])
def add_item():
    try:
        data = request.get_json()
        required_fields = ["name", "category", "stock_quantity", "description", "supplier_name", "department"]
        
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        user_name = session.get("user_name")

        conn, cursor = db_connection()
        cursor.execute(
            """
            INSERT INTO Items (name, category, stock_quantity, description, supplier_name, department, created_by) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (data["name"], data["category"], data["stock_quantity"], data["description"], data["supplier_name"], data["department"], user_name)
        )
        conn.commit()
        conn.close()

        cursor.execute

        return jsonify({"message": "Item added successfully","data": data ,"code": 201,}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@items_bp.route('/id=<int:item_id>', methods=['PUT'])
def update_item(item_id):
    try:
        data = request.get_json()
        required_fields = ["name", "category", "stock_quantity", "description", "supplier_name", "department"]
        
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        user_name = session.get("user_name")

        conn, cursor = db_connection()

        # Check if the item exists
        cursor.execute("SELECT * FROM Items WHERE id = ?", (item_id,))
        existing_item = cursor.fetchone()
        
        if not existing_item:
            conn.close()
            return jsonify({"error": "Item not found"}), 404

        # Update the item
        cursor.execute(
            """
            UPDATE Items 
            SET name = ?, category = ?, stock_quantity = ?, description = ?, supplier_name = ?, department = ?, edited_by = ?
            WHERE id = ?
            """,
            (data["name"], data["category"], data["stock_quantity"], data["description"], data["supplier_name"], data["department"], user_name, item_id)
        )

        conn.commit()
        conn.close()

        return jsonify({"message": "Item updated successfully", "data": data, "code": 200}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@items_bp.route('/id=<int:item_id>', methods=['DELETE'])
@role_required("Super Admin")
def delete_item(item_id):
    try:
        conn, cursor = db_connection()
        
        # Check if the item exists
        cursor.execute("SELECT * FROM Items WHERE id=?", (item_id,))
        item = cursor.fetchone()
        
        if not item:
            conn.close()
            return jsonify({"message": "Item not found"}), 404

        # Delete the item
        cursor.execute("DELETE FROM Items WHERE id=?", (item_id,))
        conn.commit()
        conn.close()

        return jsonify({"message": "Item deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
