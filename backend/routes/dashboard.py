from flask import Blueprint, jsonify
from flask_login import current_user, login_required
from sqlalchemy import func

from extensions import db
from models import SentimentResult, User

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.get("")
@login_required
def dashboard():
    query = db.session.query(SentimentResult.sentiment, func.count(SentimentResult.id))
    is_admin = current_user.role == "admin"
    if not is_admin:  # normal users only see their own numbers
        query = query.filter(SentimentResult.user_id == current_user.id)
    counts = dict(query.group_by(SentimentResult.sentiment).all())

    body = {
        "total": sum(counts.values()),
        "positive": counts.get("Positive", 0),
        "negative": counts.get("Negative", 0),
        "neutral": counts.get("Neutral", 0),
        "scope": "system" if is_admin else "personal",
    }
    if is_admin:
        body["users"] = User.query.count()
    return jsonify(body), 200
