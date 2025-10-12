from flask import Blueprint, request, jsonify, session
from database import db_connection

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/', methods=['GET'])
def get_categories():
    try:
        conn, cursor = db_connection()
        cursor.execute("SELECT * FROM Categories")
        categories_rows = cursor.fetchall()
        conn.close()

        categories = [dict(row) for row in categories_rows]
        return jsonify({"message": "Successfully retrieved all categories", "data": categories, "code": 200}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@categories_bp.route('/id=<int:category_id>', methods=['GET'])
def get_category(category_id):
    try:
        conn, cursor = db_connection()
        cursor.execute("SELECT * FROM Categories WHERE id = ?", (category_id,))
        category_row = cursor.fetchone()
        conn.close()

        if not category_row:
            return jsonify({"error": "Category not found"}), 404

        category = dict(category_row)
        return jsonify({"message": "Successfully retrieved category", "data": category, "code": 200}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@categories_bp.route('/', methods=['POST'])
def add_category():
    try:
        data = request.get_json()
        if "name" not in data:
            return jsonify({"error": "Missing required fields"}), 400
        
        user_name = session.get("user_name")

        conn, cursor = db_connection()
        cursor.execute(
            """
            INSERT INTO Categories (name, created_by) 
            VALUES (?, ?)
            """,
            (data["name"], user_name)
        )
        conn.commit()
        conn.close()

        return jsonify({"message": "Category added successfully", "data": data, "code": 201}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@categories_bp.route('/id=<int:category_id>', methods=['PUT'])
def update_category(category_id):
    try:
        data = request.get_json()
        if "name" not in data:
            return jsonify({"error": "Missing required fields"}), 400
        
        user_name = session.get("user_name")

        conn, cursor = db_connection()
        cursor.execute("SELECT * FROM Categories WHERE id = ?", (category_id,))
        existing_category = cursor.fetchone()
        
        if not existing_category:
            conn.close()
            return jsonify({"error": "Category not found"}), 404

        cursor.execute(
            """
            UPDATE Categories 
            SET name = ?, edited_by = ?
            WHERE id = ?
            """,
            (data["name"], user_name, category_id)
        )

        conn.commit()
        conn.close()

        return jsonify({"message": "Category updated successfully", "data": data, "code": 200}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@categories_bp.route('/id=<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    try:
        conn, cursor = db_connection()
        cursor.execute("SELECT * FROM Categories WHERE id=?", (category_id,))
        category = cursor.fetchone()
        
        if not category:
            conn.close()
            return jsonify({"message": "Category not found"}), 404

        cursor.execute("DELETE FROM Categories WHERE id=?", (category_id,))
        conn.commit()
        conn.close()

        return jsonify({"message": "Category deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
