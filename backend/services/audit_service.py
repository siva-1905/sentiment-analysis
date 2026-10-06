from flask_login import current_user

from extensions import db
from models import AuditLog


def log_action(action, description="", user_id=None):
    """Save one audit log row. Uses the logged-in user unless user_id is given."""
    if user_id is None and current_user and current_user.is_authenticated:
        user_id = current_user.id
    db.session.add(AuditLog(user_id=user_id, action=action, description=description[:500]))
    db.session.commit()
