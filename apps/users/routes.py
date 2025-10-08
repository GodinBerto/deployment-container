from flask import Blueprint, jsonify

bp = Blueprint("users", __name__)

@bp.route("/list", methods=["GET"])
def get_users():
    """Fetch all users"""
    return jsonify({"users": ["Alice", "Bob", "Charlie"]})

@bp.route("/<int:id>", methods=["GET"])
def get_user(id):
    """Get a single user by ID"""
    return jsonify({"user": {"id": id, "name": "Alice"}})
