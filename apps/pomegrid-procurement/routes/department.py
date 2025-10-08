from flask import Blueprint, request, jsonify, session
from database import db_connection

department_bp = Blueprint('departments', __name__)

@department_bp.route('/', methods=['GET'])
def get_departments():
    try:
        conn, cursor = db_connection()
        cursor.execute("SELECT * FROM Department")
        department_rows = cursor.fetchall()
        conn.close()

        departments = [dict(row) for row in department_rows]
        return jsonify({"message": "Successfully retrieved all departments", "data": departments, "code": 200}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@department_bp.route('/id=<int:department_id>', methods=['GET'])
def get_department(department_id):
    try:
        conn, cursor = db_connection()
        cursor.execute("SELECT * FROM Department WHERE id = ?", (department_id,))
        department_row = cursor.fetchone()
        conn.close()

        if not department_row:
            return jsonify({"error": "Department not found"}), 404

        department = dict(department_row)
        return jsonify({"message": "Successfully retrieved department", "data": department, "code": 200}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@department_bp.route('/', methods=['POST'])
def add_department():
    try:
        data = request.get_json()
        if "name" not in data:
            return jsonify({"error": "Missing required fields"}), 400
        
        conn, cursor = db_connection()
        cursor.execute(
            """
            INSERT INTO Department (name, description) 
            VALUES (?, ?)
            """,
            (data["name"], data.get("description", ""))
        )
        conn.commit()
        conn.close()

        return jsonify({"message": "Department added successfully", "data": data, "code": 201}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@department_bp.route('/id=<int:department_id>', methods=['PUT'])
def update_department(department_id):
    try:
        data = request.get_json()
        if "name" not in data:
            return jsonify({"error": "Missing required fields"}), 400
        
        conn, cursor = db_connection()
        cursor.execute("SELECT * FROM Department WHERE id = ?", (department_id,))
        existing_department = cursor.fetchone()
        
        if not existing_department:
            conn.close()
            return jsonify({"error": "Department not found"}), 404

        cursor.execute(
            """
            UPDATE Department 
            SET name = ?, description = ?
            WHERE id = ?
            """,
            (data["name"], data.get("description", ""), department_id)
        )

        conn.commit()
        conn.close()

        return jsonify({"message": "Department updated successfully", "data": data, "code": 200}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@department_bp.route('/id=<int:department_id>', methods=['DELETE'])
def delete_department(department_id):
    try:
        conn, cursor = db_connection()
        cursor.execute("SELECT * FROM Department WHERE id=?", (department_id,))
        department = cursor.fetchone()
        
        if not department:
            conn.close()
            return jsonify({"message": "Department not found"}), 404

        cursor.execute("DELETE FROM Department WHERE id=?", (department_id,))
        conn.commit()
        conn.close()

        return jsonify({"message": "Department deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
