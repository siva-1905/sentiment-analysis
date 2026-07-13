from flask_login import UserMixin
from app import db


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    email = db.Column(db.String(120), unique=True)

    password = db.Column(db.String(255))

    role = db.Column(db.String(20), default="user")

    status = db.Column(db.Boolean, default=True)

class AuditLog(db.Model):

    __tablename__ = "audit_logs"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    activity = db.Column(
        db.String(255)
    )

    ip_address = db.Column(
        db.String(100)
    )

    browser = db.Column(
        db.String(255)
    )

    timestamp = db.Column(
        db.DateTime,
        default=db.func.current_timestamp()
    )