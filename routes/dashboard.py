from flask import (
    Blueprint,
    render_template,
    redirect,
    request,
    url_for,
    abort
)

from flask_login import (
    login_required,
    current_user
)
from werkzeug.security import generate_password_hash
from functools import wraps

from extensions import db
from flask import send_file
import pandas as pd
from io import BytesIO
from database.models import (
    User,
    SentimentResult,
    TextData
)
from database.models import Report
from sqlalchemy import func
from database.models import SentimentResult
dashboard_bp = Blueprint(
    "dashboard",
    __name__
)


def admin_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if current_user.role != "admin":

            abort(403)

        return func(*args, **kwargs)

    return wrapper


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():

    user_results = SentimentResult.query.filter_by(
        user_id=current_user.id
    )

    total_predictions = user_results.count()

    positive_count = user_results.filter_by(
        sentiment="Positive"
    ).count()

    negative_count = user_results.filter_by(
        sentiment="Negative"
    ).count()

    neutral_count = user_results.filter_by(
        sentiment="Neutral"
    ).count()
    total = (
        positive_count +
        negative_count +
        neutral_count
    )

    if total > 0:

        positive_percentage = round(
            (positive_count / total) * 100,
            2
        )

    else:

        positive_percentage = 0
    trend_data = db.session.query(

        func.date(
            SentimentResult.prediction_date
        ),

        func.count(
            SentimentResult.id
        )

    ).filter_by(

        user_id=current_user.id

    ).group_by(

        func.date(
            SentimentResult.prediction_date
        )

    ).all()
    dates = [
        str(row[0]) 
        for row in trend_data
    ]

    counts = [
        row[1] 
        for row in trend_data
    ]
    recent_results = (
        SentimentResult.query
        .filter_by(user_id=current_user.id)
        .order_by(
            SentimentResult.prediction_date.desc()
        )
        .limit(5)
        .all()
    )
    return render_template(
     "dashboard.html",

     total_predictions=total_predictions,

     positive_count=positive_count,

     negative_count=negative_count,

     neutral_count=neutral_count,

     positive_percentage=positive_percentage,

     recent_results=recent_results
 )


@dashboard_bp.route("/admin")
@login_required
@admin_required
def admin_dashboard():

    total_users = User.query.count()

    total_reviews = SentimentResult.query.count()

    positive_reviews = SentimentResult.query.filter_by(
        sentiment="Positive"
    ).count()

    negative_reviews = SentimentResult.query.filter_by(
        sentiment="Negative"
    ).count()

    neutral_reviews = SentimentResult.query.filter_by(
        sentiment="Neutral"
    ).count()
    recent_uploads = (
        SentimentResult.query
        .order_by(
            SentimentResult.prediction_date.desc()
        )
        .limit(5)
        .all()
    )
    trend_data = db.session.query(
        func.date(
            SentimentResult.prediction_date
        ),
        func.count(
            SentimentResult.id
        )
    ).group_by(
        func.date(
            SentimentResult.prediction_date
        )
    ).all()

    dates = [
        str(row[0])
        for row in trend_data
    ]

    counts = [
        row[1]
        for row in trend_data
    ]
    pdf_reports = Report.query.filter_by(
        report_type="PDF"
    ).count()

    csv_reports = Report.query.filter_by(
        report_type="CSV"
    ).count()

    excel_reports = Report.query.filter_by(
        report_type="Excel"
    ).count()
    return render_template(
        "admin_dashboard.html",

        total_users=total_users,
        total_reviews=total_reviews,
        positive_reviews=positive_reviews,
        negative_reviews=negative_reviews,
        neutral_reviews=neutral_reviews,

        recent_uploads=recent_uploads,
        dates=dates,
        counts=counts,
        pdf_reports=pdf_reports,
        csv_reports=csv_reports,
        excel_reports=excel_reports
    )

@dashboard_bp.route("/admin/users")
@login_required
@admin_required
def manage_users():

    users = User.query.all()

    return render_template(
        "manage_users.html",
        users=users
    )


@dashboard_bp.route("/admin/toggle-user/<int:user_id>")
@login_required
@admin_required
def toggle_user(user_id):

    user = User.query.get_or_404(user_id)

    if user.role == "admin":

        return "Admin account cannot be disabled."

    user.status = not user.status

    db.session.commit()

    return redirect(
        url_for("dashboard.manage_users")
    )


@dashboard_bp.route("/admin/delete-user/<int:user_id>")
@login_required
@admin_required
def delete_user(user_id):

    user = User.query.get_or_404(user_id)

    if user.role == "admin":

        return "Admin account cannot be deleted."

    db.session.delete(user)

    db.session.commit()

    return redirect(
        url_for("dashboard.manage_users")
    )

@dashboard_bp.route("/admin/add-user", methods=["GET", "POST"])
@login_required
@admin_required
def add_user():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:
            return "User already exists"

        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role=role
        )

        db.session.add(user)
        db.session.commit()

        return redirect(
            url_for("dashboard.manage_users")
        )

    return render_template(
        "add_user.html"
    )

@dashboard_bp.route(
    "/admin/edit-user/<int:user_id>",
    methods=["GET", "POST"]
)
@login_required
@admin_required
def edit_user(user_id):

    user = User.query.get_or_404(user_id)

    if request.method == "POST":

        user.name = request.form["name"]

        user.email = request.form["email"]

        user.role = request.form["role"]

        db.session.commit()

        return redirect(
            url_for("dashboard.manage_users")
        )

    return render_template(
        "edit_user.html",
        user=user
    )

@dashboard_bp.route("/admin/export-users")
@login_required
@admin_required
def export_users():

    users = User.query.all()

    data = []

    for user in users:

        data.append({
            "ID": user.id,
            "Name": user.name,
            "Email": user.email,
            "Role": user.role,
            "Status": "Active" if user.status else "Inactive"
        })

    df = pd.DataFrame(data)

    output = BytesIO()

    df.to_csv(
        output,
        index=False
    )

    output.seek(0)

    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name="users.csv"
    )

@dashboard_bp.route(
    "/admin/import-users",
    methods=["GET", "POST"]
)
@login_required
@admin_required
def import_users():

    if request.method == "POST":

        file = request.files["file"]

        if file.filename == "":
            return "No file selected"

        df = pd.read_csv(file)

        for _, row in df.iterrows():

            existing_user = User.query.filter_by(
                email=row["Email"]
            ).first()

            if existing_user:
                continue

            user = User(
                name=row["Name"],
                email=row["Email"],
                password=generate_password_hash(
                    str(row["Password"])
                ),
                role=row["Role"]
            )

            db.session.add(user)

        db.session.commit()

        return redirect(
            url_for("dashboard.manage_users")
        )

    return render_template(
        "import_users.html"
    )