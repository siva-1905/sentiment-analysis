from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for
)
from utils.audit import create_log
from flask_login import (
    login_required,
    current_user
)

from extensions import db

from database.models import SentimentResult

from utils.notification import create_notification
from utils.predictor import predict_sentiment

from wordcloud import WordCloud

from flask import redirect, url_for

import os


sentiment_bp = Blueprint(
    "sentiment",
    __name__
)


@sentiment_bp.route("/predict", methods=["GET", "POST"])
@login_required
def predict():

    sentiment = None
    confidence = None

    if request.method == "POST":

        review = request.form["review"]

        sentiment, confidence = predict_sentiment(
            review
        )

        result = SentimentResult(

            user_id=current_user.id,

            text=review,

            sentiment=sentiment,

            confidence_score=confidence

        )

        db.session.add(result)

        db.session.commit()
        create_log(
            current_user.id,
            "Sentiment Analysis"
        )

        from utils.notification import create_notification

        create_notification(

            current_user.id,

            "Analysis Completed",

            f"Result: {sentiment}"

        )
    return render_template(
        "predict.html",
        sentiment=sentiment,
        confidence=confidence
    )


@sentiment_bp.route("/history")
@login_required
def history():

    query = SentimentResult.query

    # User only sees own records
    if current_user.role != "admin":
        query = query.filter_by(
            user_id=current_user.id
        )

    sentiment = request.args.get(
        "sentiment"
    )

    keyword = request.args.get(
        "keyword"
    )
    start_date = request.args.get(
        "start_date"
    )

    end_date = request.args.get(
        "end_date"
    )
    if sentiment:

        query = query.filter(
            SentimentResult.sentiment == sentiment
        )

    if keyword:

        query = query.filter(
            SentimentResult.text.contains(
                keyword
            )
        )
    if start_date:

        query = query.filter(
            SentimentResult.prediction_date >= start_date
        )   

    if end_date:

        query = query.filter(
            SentimentResult.prediction_date <= end_date
    )








    results = query.order_by(
        SentimentResult.prediction_date.desc()
    ).all()

    return render_template(
        "history.html",
        results=results
    )


@sentiment_bp.route("/delete-result/<int:id>")
@login_required
def delete_result(id):

    result = SentimentResult.query.get_or_404(id)

    if result.user_id != current_user.id:
        return "Unauthorized"

    db.session.delete(result)

    db.session.commit()

    return redirect(
        url_for("sentiment.history")
    )

@sentiment_bp.route("/analytics")
@login_required
def analytics():

    positive_count = SentimentResult.query.filter_by(
        user_id=current_user.id,
        sentiment="Positive"
    ).count()

    negative_count = SentimentResult.query.filter_by(
        user_id=current_user.id,
        sentiment="Negative"
    ).count()

    neutral_count = SentimentResult.query.filter_by(
        user_id=current_user.id,
        sentiment="Neutral"
    ).count()

    return render_template(
        "analytics.html",
        positive_count=positive_count,
        negative_count=negative_count,
        neutral_count=neutral_count
    )


@sentiment_bp.route("/wordcloud")
@login_required
def wordcloud_view():

    results = SentimentResult.query.filter_by(
        user_id=current_user.id
    ).all()

    text = " ".join(
        [r.text for r in results]
    )

    if not text:
        return "No predictions available"

    wc = WordCloud(
        width=800,
        height=400,
        background_color="white"
    ).generate(text)

    save_path = os.path.join(
        "static",
        "wordcloud.png"
    )

    wc.to_file(save_path)

    return render_template(
        "wordcloud.html"
    )