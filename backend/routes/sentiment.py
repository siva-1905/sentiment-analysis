import io
import os

import pandas as pd
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from extensions import db
from models import SentimentResult
from services import predictor
from services.audit_service import log_action

sentiment_bp = Blueprint("sentiment", __name__, url_prefix="/api/sentiment")

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
TEXT_COLUMNS = {"review", "text", "reviews", "comment"}
MAX_ROWS = 1000
MAX_TEXT_LENGTH = 5000


@sentiment_bp.post("/predict")
@login_required
def predict():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or data.get("review") or "").strip()
    if not text:
        return jsonify(message="Review is required"), 400
    if len(text) > MAX_TEXT_LENGTH:
        return jsonify(message=f"Review must be at most {MAX_TEXT_LENGTH} characters"), 400

    result = predictor.predict_sentiment(text)
    row = SentimentResult(
        user_id=current_user.id, text=text,
        sentiment=result["sentiment"], confidence_score=result["confidence"],
    )
    db.session.add(row)
    db.session.commit()
    log_action("Prediction", f"Predicted {result['sentiment']} ({result['confidence']}%)")
    return jsonify(id=row.id, sentiment=result["sentiment"], confidence=result["confidence"]), 201


@sentiment_bp.get("/history")
@login_required
def history():
    rows = (
        SentimentResult.query.filter_by(user_id=current_user.id)
        .order_by(SentimentResult.prediction_date.desc())
        .limit(500)
        .all()
    )
    return jsonify(history=[r.to_dict() for r in rows]), 200


def _own_result_or_none(result_id):
    # Filtering by user_id means other users' rows look like "not found"
    return SentimentResult.query.filter_by(id=result_id, user_id=current_user.id).first()


@sentiment_bp.get("/history/<int:result_id>")
@login_required
def history_item(result_id):
    row = _own_result_or_none(result_id)
    if not row:
        return jsonify(message="Resource not found"), 404
    return jsonify(result=row.to_dict()), 200


@sentiment_bp.delete("/history/<int:result_id>")
@login_required
def delete_history_item(result_id):
    row = _own_result_or_none(result_id)
    if not row:
        return jsonify(message="Resource not found"), 404
    db.session.delete(row)
    db.session.commit()
    log_action("Delete Prediction", f"Deleted prediction #{result_id}")
    return jsonify(message="Deleted"), 200


def _read_file(raw, ext):
    if ext == ".csv":
        try:
            return pd.read_csv(io.BytesIO(raw))
        except UnicodeDecodeError:
            return pd.read_csv(io.BytesIO(raw), encoding="latin-1")
    return pd.read_excel(io.BytesIO(raw))  # .xlsx (openpyxl) / .xls (xlrd)


@sentiment_bp.post("/upload")
@login_required
def upload():
    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify(message="File is required"), 400
    ext = os.path.splitext(file.filename.lower())[1]
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify(message="Only .csv, .xlsx and .xls files are allowed"), 400

    # The file is only parsed as data in memory. It is never saved or executed.
    try:
        df = _read_file(file.read(), ext)
    except Exception:
        return jsonify(message="Could not read the file. Make sure it is a valid CSV/Excel file"), 400

    column = next((c for c in df.columns if str(c).strip().lower() in TEXT_COLUMNS), None)
    if column is None:
        return jsonify(message="No review column found. Name the column 'review' or 'text'"), 400

    texts = [str(t).strip()[:MAX_TEXT_LENGTH] for t in df[column].dropna()]
    texts = [t for t in texts if t]
    if not texts:
        return jsonify(message="The review column has no data"), 400
    if len(texts) > MAX_ROWS:
        return jsonify(message=f"Too many rows (max {MAX_ROWS})"), 400

    results, summary = [], {"Positive": 0, "Negative": 0, "Neutral": 0}
    for text in texts:
        res = predictor.predict_sentiment(text)
        summary[res["sentiment"]] += 1
        results.append({"text": text, "sentiment": res["sentiment"], "confidence": res["confidence"]})
        db.session.add(SentimentResult(
            user_id=current_user.id, text=text,
            sentiment=res["sentiment"], confidence_score=res["confidence"],
        ))
    db.session.commit()
    log_action("File Upload", f"Uploaded {file.filename}: {len(results)} reviews analysed")
    return jsonify(count=len(results), summary=summary, results=results), 201
