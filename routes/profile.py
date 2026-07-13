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

from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from extensions import db

profile_bp = Blueprint(
    "profile",
    __name__
)
@profile_bp.route(
    "/change-password",
    methods=["GET", "POST"]
)
@login_required
def change_password():

    if request.method == "POST":

        old_password = request.form[
            "old_password"
        ]

        new_password = request.form[
            "new_password"
        ]

        if not check_password_hash(
            current_user.password,
            old_password
        ):
            return "Old password incorrect"

        current_user.password = (
            generate_password_hash(
                new_password
            )
        )

        db.session.commit()

        return redirect(
            url_for(
                "dashboard.dashboard"
            )
        )

    return render_template(
        "change_password.html"
    )