from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def iso(dt):
    return dt.isoformat() + "Z" if dt else None


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)  # hashed, never plain text
    role = db.Column(db.String(10), nullable=False, default="user")      # "user" | "admin"
    status = db.Column(db.String(10), nullable=False, default="active")  # "active" | "disabled"
    created_at = db.Column(db.DateTime, default=utcnow)

    results = db.relationship("SentimentResult", backref="user", cascade="all, delete-orphan")
    logs = db.relationship("AuditLog", backref="user")  # logs are kept (user_id becomes NULL)

    def set_password(self, raw):
        self.password = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password, raw)

    def to_dict(self):  # password is intentionally NOT included
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "status": self.status,
            "created_at": iso(self.created_at),
        }


class SentimentResult(db.Model):
    __tablename__ = "sentiment_results"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    text = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(10), nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    prediction_date = db.Column(db.DateTime, default=utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "sentiment": self.sentiment,
            "confidence": self.confidence_score,
            "date": iso(self.prediction_date),
        }


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    action = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_email": self.user.email if self.user else None,
            "action": self.action,
            "description": self.description,
            "timestamp": iso(self.timestamp),
        }
