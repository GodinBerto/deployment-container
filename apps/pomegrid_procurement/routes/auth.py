from flask import Blueprint, request, jsonify, session
import sqlite3
import hashlib
from flask_cors import CORS
from database.pomegid_database.database import db_connection

bp = Blueprint("auth", __name__)
CORS(bp)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        conn, cursor = db_connection()
        cursor.execute("SELECT * FROM Users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and user["password"] == hash_password(password):
            session["user_name"] = user["name"]
            session["user_id"] = user["id"]
            return jsonify({
                "message": "Login successful",
                "user": {
                    "id": user["id"],
                    "name": user["name"],
                    "role": user["role"],
                    "email": user["email"]
                }
            }), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        name = data.get("name")
        role = data.get("role")
        department = data.get("department")
        email = data.get("email")
        phone = data.get("phone")
        password = data.get("password")
        created_by = data.get("created_by", None)

        # Basic validation
        if not all([name, role, department, email, phone, password]):
            return jsonify({"error": "All fields are required"}), 400

        # Hash password
        hashed_pw = hash_password(password)

        # Insert into DB
        conn, cursor = db_connection()
        cursor.execute(
            """
            INSERT INTO Users (name, role, department, email, phone, password, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name, role, department, email, phone, hashed_pw, created_by),
        )
        conn.commit()
        conn.close()

        return jsonify({"message": "User registered successfully"}), 201

    except sqlite3.IntegrityError as e:
        # Handle unique constraint errors
        if "email" in str(e):
            return jsonify({"error": "Email already exists"}), 400
        if "phone" in str(e):
            return jsonify({"error": "Phone number already exists"}), 400
        return jsonify({"error": "Database integrity error"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500