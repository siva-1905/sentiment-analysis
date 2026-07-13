from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for
)

from flask_login import (
    login_required,
    current_user
)

from werkzeug.utils import secure_filename

from extensions import db

from database.models import (
    TextData,
    SentimentResult
)

from utils.audit import create_log
from utils.predictor import (
    predict_sentiment
)

import pandas as pd

upload_bp = Blueprint(
    "upload",
    __name__
)
@upload_bp.route(
    "/upload",
    methods=["GET", "POST"]
)
@login_required
def upload():

    if request.method == "POST":

        file = request.files["file"]

        if not file:
            return "No file selected"

        filename = secure_filename(
            file.filename
        )

        extension = filename.split(".")[-1].lower()

        # ------------------
        # TXT FILE
        # ------------------

        if extension == "txt":

            content = file.read().decode(
                "utf-8"
            )

            sentiment, confidence = (
                predict_sentiment(content)
            )

            db.session.add(

                SentimentResult(
                    user_id=current_user.id,
                    text=content,
                    sentiment=sentiment,
                    confidence_score=confidence
                )

            )

            db.session.commit()

        # ------------------
        # CSV FILE
        # ------------------

        elif extension == "csv":

            df = pd.read_csv(file)

            review_column = df.columns[0]

            for review in df[
                review_column
            ].dropna():

                sentiment, confidence = (
                    predict_sentiment(
                        str(review)
                    )
                )

                result = SentimentResult(

                    user_id=current_user.id,

                    text=str(review),

                    sentiment=sentiment,

                    confidence_score=confidence

                )

                db.session.add(result)

            db.session.commit()

        # ------------------
        # EXCEL FILE
        # ------------------

        elif extension in [
            "xlsx",
            "xls"
        ]:

            df = pd.read_excel(file)

            review_column = df.columns[0]

            for review in df[
                review_column
            ].dropna():

                sentiment, confidence = (
                    predict_sentiment(
                        str(review)
                    )
                )

                result = SentimentResult(

                    user_id=current_user.id,

                    text=str(review),

                    sentiment=sentiment,

                    confidence_score=confidence

                )
                create_log(
                    current_user.id,
                    "File Upload"
                )
                db.session.add(result)

            db.session.commit()

        return redirect(
            url_for("upload.upload")
        )

    results = SentimentResult.query.filter_by(
        user_id=current_user.id
    ).order_by(
        SentimentResult.prediction_date.desc()
    ).all()

    return render_template(
        "upload.html",
        results=results
    )