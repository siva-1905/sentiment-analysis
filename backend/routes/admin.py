import re

from flask import Blueprint, jsonify, request
from flask_login import current_user

from extensions import admin_required, db
from models import AuditLog, User
from services.audit_service import log_action

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ROLES = {"user", "admin"}
STATUSES = {"active", "disabled"}


def _get_user(user_id):
    return db.session.get(User, user_id)


@admin_bp.get("/users")
@admin_required
def list_users():
    users = User.query.order_by(User.id).all()
    return jsonify(users=[u.to_dict() for u in users]), 200


@admin_bp.post("/users")
@admin_required
def create_user():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = data.get("role", "user")

    if not name or not email or not password:
        return jsonify(message="Name, email and password are required"), 400
    if not EMAIL_RE.match(email):
        return jsonify(message="Invalid email address"), 400
    if len(password) < 6:
        return jsonify(message="Password must be at least 6 characters"), 400
    if role not in ROLES:
        return jsonify(message="Role must be 'user' or 'admin'"), 400
    if User.query.filter_by(email=email).first():
        return jsonify(message="Email already exists"), 409

    user = User(name=name, email=email, role=role, status="active")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    log_action("User Created", f"Admin created user {email} ({role})")
    return jsonify(user=user.to_dict()), 201


@admin_bp.put("/users/<int:user_id>")
@admin_required
def update_user(user_id):
    user = _get_user(user_id)
    if not user:
        return jsonify(message="Resource not found"), 404
    data = request.get_json(silent=True) or {}

    if "name" in data:
        name = (data["name"] or "").strip()
        if not name:
            return jsonify(message="Name cannot be empty"), 400
        user.name = name
    if "email" in data:
        email = (data["email"] or "").strip().lower()
        if not EMAIL_RE.match(email):
            return jsonify(message="Invalid email address"), 400
        other = User.query.filter_by(email=email).first()
        if other and other.id != user.id:
            return jsonify(message="Email already exists"), 409
        user.email = email
    if data.get("password"):
        if len(data["password"]) < 6:
            return jsonify(message="Password must be at least 6 characters"), 400
        user.set_password(data["password"])
    if "role" in data:
        if data["role"] not in ROLES:
            return jsonify(message="Role must be 'user' or 'admin'"), 400
        if user.id == current_user.id and data["role"] != "admin":
            return jsonify(message="You cannot remove your own admin role"), 400
        user.role = data["role"]
    if "status" in data:
        if data["status"] not in STATUSES:
            return jsonify(message="Status must be 'active' or 'disabled'"), 400
        if user.id == current_user.id and data["status"] != "active":
            return jsonify(message="You cannot deactivate yourself"), 400
        user.status = data["status"]

    db.session.commit()
    log_action("User Updated", f"Admin updated user {user.email}")
    return jsonify(user=user.to_dict()), 200


@admin_bp.delete("/users/<int:user_id>")
@admin_required
def delete_user(user_id):
    user = _get_user(user_id)
    if not user:
        return jsonify(message="Resource not found"), 404
    if user.id == current_user.id:
        return jsonify(message="You cannot delete yourself"), 400
    email = user.email
    db.session.delete(user)
    db.session.commit()
    log_action("User Deleted", f"Admin deleted user {email}")
    return jsonify(message="User deleted"), 200


@admin_bp.patch("/users/<int:user_id>/status")
@admin_required
def change_status(user_id):
    user = _get_user(user_id)
    if not user:
        return jsonify(message="Resource not found"), 404
    status = (request.get_json(silent=True) or {}).get("status")
    if status not in STATUSES:
        return jsonify(message="Status must be 'active' or 'disabled'"), 400
    if user.id == current_user.id and status != "active":
        return jsonify(message="You cannot deactivate yourself"), 400
    user.status = status
    db.session.commit()
    log_action("User Activated" if status == "active" else "User Deactivated", f"Admin set {user.email} to {status}")
    return jsonify(user=user.to_dict()), 200


@admin_bp.patch("/users/<int:user_id>/role")
@admin_required
def change_role(user_id):
    user = _get_user(user_id)
    if not user:
        return jsonify(message="Resource not found"), 404
    role = (request.get_json(silent=True) or {}).get("role")
    if role not in ROLES:
        return jsonify(message="Role must be 'user' or 'admin'"), 400
    if user.id == current_user.id and role != "admin":
        return jsonify(message="You cannot remove your own admin role"), 400
    user.role = role
    db.session.commit()
    log_action("User Updated", f"Admin changed role of {user.email} to {role}")
    return jsonify(user=user.to_dict()), 200


@admin_bp.get("/audit-logs")
@admin_required
def audit_logs():
    limit = min(request.args.get("limit", 200, type=int), 1000)
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc(), AuditLog.id.desc()).limit(limit).all()
    return jsonify(logs=[l.to_dict() for l in logs]), 200
