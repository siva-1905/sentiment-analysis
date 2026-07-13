from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for
)

from flask_login import (
    current_user,
    login_user,
    logout_user,
    login_required
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from extensions import (
    db,
    login_manager
)

from database.models import User
from utils.audit import create_log
auth_bp = Blueprint(
    "auth",
    __name__
)


@login_manager.user_loader
def load_user(user_id):

    return User.query.get(
        int(user_id)
    )


@auth_bp.route("/")
def home():

    return render_template(
        "home.html"
    )


@auth_bp.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form["name"]

        email = request.form["email"]

        password = request.form["password"]

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            return "Email already exists"

        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role="user"
        )

        db.session.add(user)

        db.session.commit()

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "register.html"
    )


@auth_bp.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form["email"]

        password = request.form["password"]

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            if not user.status:

                return "Account Disabled"

            login_user(user)
            create_log(
                user.id,
                "User Login"
            )
            return redirect(
                url_for(
                    "dashboard.dashboard"
                )
            )

        return "Invalid Credentials"

    return render_template(
        "login.html"
    )


@auth_bp.route("/logout")
@login_required
def logout():
    create_log(
    current_user.id,
    "User Logout"
)
    logout_user()

    return redirect(
        url_for("auth.home")
    )