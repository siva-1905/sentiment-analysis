import re

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required, login_user, logout_user

from extensions import db
from models import User
from services.audit_service import log_action

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not email or not password:
        return jsonify(message="Name, email and password are required"), 400
    if not EMAIL_RE.match(email):
        return jsonify(message="Invalid email address"), 400
    if len(password) < 6:
        return jsonify(message="Password must be at least 6 characters"), 400
    if User.query.filter_by(email=email).first():
        return jsonify(message="Email already exists"), 409

    user = User(name=name, email=email, role="user", status="active")  # role is never taken from the request
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    log_action("Registration", f"New user registered: {email}", user_id=user.id)
    return jsonify(message="Registration successful", user=user.to_dict()), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password:
        return jsonify(message="Email and password are required"), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify(message="Invalid email or password"), 401
    if user.status != "active":
        return jsonify(message="Your account is disabled"), 403

    login_user(user)
    log_action("Login", f"{email} logged in", user_id=user.id)
    return jsonify(message="Login successful", user=user.to_dict()), 200


@auth_bp.post("/logout")
@login_required
def logout():
    log_action("Logout", f"{current_user.email} logged out")
    logout_user()
    return jsonify(message="Logged out"), 200


@auth_bp.get("/me")
@login_required
def me():
    return jsonify(user=current_user.to_dict()), 200
