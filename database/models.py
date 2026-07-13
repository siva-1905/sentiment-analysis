from flask_login import UserMixin
from extensions import db


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), default="user")

    status = db.Column(db.Boolean, default=True)


class TextData(db.Model):

    __tablename__ = "text_data"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    category = db.Column(
        db.String(100),
        default="General"
    )

    source = db.Column(
        db.String(50)
    )

    upload_date = db.Column(
        db.DateTime,
        default=db.func.current_timestamp()
    )

class SentimentResult(db.Model):

    __tablename__ = "sentiment_results"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    text = db.Column(db.Text)

    sentiment = db.Column(db.String(20))

    confidence_score = db.Column(db.Float)

    prediction_date = db.Column(
        db.DateTime,
        default=db.func.current_timestamp()
    )

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
class Notification(db.Model):

    __tablename__ = "notifications"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    title = db.Column(
        db.String(255)
    )

    message = db.Column(
        db.Text
    )

    status = db.Column(
        db.String(20),
        default="Unread"
    )

    created_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp()
    )

class Report(db.Model):

    __tablename__ = "reports"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    report_name = db.Column(
        db.String(100)
    )

    report_type = db.Column(
        db.String(50)
    )

    generated_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    generated_date = db.Column(
        db.DateTime,
        default=db.func.current_timestamp()
    )