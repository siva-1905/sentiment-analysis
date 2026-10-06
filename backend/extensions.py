from functools import wraps

from flask import jsonify
from flask_login import LoginManager, current_user, login_required
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()


def admin_required(fn):
    """Allow only logged-in admins. Returns 401 if not logged in, 403 if not admin."""

    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        if current_user.role != "admin":
            return jsonify(message="Admin access required"), 403
        return fn(*args, **kwargs)

    return wrapper
