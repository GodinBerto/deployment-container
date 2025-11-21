from flask import Blueprint, request, jsonify, session
from database import db_connection
import hashlib

staff_bp = Blueprint('staffs', __name__)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@staff_bp.route('/', methods=['GET'])
def get_all_staff():
    try:
        conn, cursor = db_connection()
        cursor.execute("SELECT * FROM users WHERE role = 'Admin' OR role = 'Staff' OR role = 'Customer'")
        staff_rows = cursor.fetchall()
        conn.close()
        

        staff = [dict(row) for row in staff_rows]
        return jsonify({"message": "Successfully retrieved all staff", "data": staff, "code": 200}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@staff_bp.route('/id=<int:staff_id>', methods=['GET'])
def get_staff(staff_id):
    try:
        conn, cursor = db_connection()
        cursor.execute("SELECT * FROM Users WHERE id = ?", (staff_id,))
        staff = cursor.fetchone()
        conn.close()

        if not staff:
            return jsonify({"error": "Staff not found"}), 404

        return jsonify({"message": "Successfully retrieved staff", "data": dict(staff), "code": 200}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@staff_bp.route('/', methods=['POST'])
def add_staff():
    try:
        data = request.get_json()
        required_fields = ["name", "email", "password", "phone", "department", "role"]
        
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        existing_staff = db_connection()[1].execute("SELECT * FROM users WHERE email = ?", (data["email"],)).fetchone()
        if existing_staff:
            return jsonify({"error": "Staff already exists"}), 400
        username = session.get("user_name")
        
        hashed_password = hash_password(data["password"])
        conn, cursor = db_connection()
        cursor.execute(
            "INSERT INTO Users (name, email, password, phone, role, department, created_by, edited_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (data["name"], data["email"], data["password"], data["phone"],  data["role"], data["department"], username, "")
        )
        conn.commit()
        conn.close()

        return jsonify({"message": "Staff added successfully", "data": data, "code": 201}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@staff_bp.route('/id=<int:staff_id>', methods=['PUT'])
def update_staff(staff_id):
    try:
        data = request.get_json()
        required_fields = ["name", "email", "phone", "role", "department"]
        
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        conn, cursor = db_connection()
        cursor.execute("SELECT * FROM Users WHERE id = ? AND role = ?", (staff_id, data["role"],))
        existing_staff = cursor.fetchone()
        
        if not existing_staff:
            conn.close()
            return jsonify({"error": "Staff not found"}), 404

        cursor.execute(
            "UPDATE Users SET name = ?, email = ?, phone = ?, edited_by = ?, role = ?, department = ? WHERE id = ?",
            (data["name"], data["email"], data["phone"], session.get("user_name"), data["role"], data["department"], staff_id)
        )
        conn.commit()
        conn.close()

        return jsonify({"message": "Staff updated successfully", "data": data, "code": 200}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@staff_bp.route('/id=<int:staff_id>', methods=['DELETE'])
def delete_staff(staff_id):
    try:
        conn, cursor = db_connection()
        cursor.execute("SELECT * FROM Users WHERE id = ?", (staff_id,))
        staff = cursor.fetchone()
        
        if not staff:
            conn.close()
            return jsonify({"error": "Staff not found"}), 404

        cursor.execute("DELETE FROM Users WHERE id = ?", (staff_id,))
        conn.commit()
        conn.close()

        return jsonify({"message": "Staff deleted successfully", "code": 200}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
