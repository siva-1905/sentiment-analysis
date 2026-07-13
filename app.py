from flask import Flask

from config import Config
from extensions import db, login_manager


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    app.config["UPLOAD_FOLDER"] = "uploads"

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"

    with app.app_context():

        from database.models import (
            User,
            TextData,
            SentimentResult,
            AuditLog,
            Notification,
            Report
        )

        db.create_all()

        from routes.auth import auth_bp
        from routes.dashboard import dashboard_bp
        from routes.sentiment import sentiment_bp
        from routes.upload import upload_bp
        from routes.reports import reports_bp
        from routes.profile import profile_bp
        from routes.notifications import notifications_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(dashboard_bp)
        app.register_blueprint(sentiment_bp)
        app.register_blueprint(upload_bp)
        app.register_blueprint(reports_bp)
        app.register_blueprint(profile_bp)
        app.register_blueprint(notifications_bp)

        from werkzeug.security import generate_password_hash

        admin = User.query.filter_by(
            email="admin@sentiment.com"
        ).first()

        if not admin:

            admin = User(
                name="Administrator",
                email="admin@sentiment.com",
                password=generate_password_hash("Admin@123"),
                role="admin"
            )

            db.session.add(admin)
            db.session.commit()

            print("Default admin created")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)