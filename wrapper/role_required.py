from functools import wraps
from flask import jsonify, session


def role_required(*allowed_roles):
    """Simple role gate for routes that require session-based authorization."""

    normalized_roles = {str(role).strip().lower() for role in allowed_roles if role}

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            user_role = str(session.get("user_role", "")).strip().lower()
            if normalized_roles and user_role not in normalized_roles:
                return jsonify({"error": "Unauthorized"}), 403
            return view_func(*args, **kwargs)

        return wrapped

    return decorator
