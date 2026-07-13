from flask import Blueprint, render_template

from flask_login import (
    login_required,
    current_user
)

from database.models import AuditLog

admin_bp = Blueprint(
    "admin",
    __name__
)
@admin_bp.route("/audit-logs")
@login_required
def audit_logs():

    logs = AuditLog.query.order_by(
        AuditLog.timestamp.desc()
    ).all()

    return render_template(
        "audit_logs.html",
        logs=logs
    )