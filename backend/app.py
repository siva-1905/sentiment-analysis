import logging
import os

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from config import Config
from extensions import db, login_manager
from models import User
from routes import register_blueprints
from services.predictor import ModelNotFoundError


def seed_admin(app):
    """Create the first admin from ADMIN_EMAIL / ADMIN_PASSWORD if no admin exists."""
    if User.query.filter_by(role="admin").first():
        return
    email, password = app.config["ADMIN_EMAIL"].strip().lower(), app.config["ADMIN_PASSWORD"]
    if not email or not password:
        app.logger.warning("No admin exists and ADMIN_EMAIL / ADMIN_PASSWORD are not set.")
        return
    admin = User(name=app.config["ADMIN_NAME"], email=email, role="admin", status="active")
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    app.logger.info("Admin user created: %s", email)


def create_app(overrides=None):
    app = Flask(__name__, instance_path=os.path.join(Config.BASE_DIR, "instance"))
    app.config.from_object(Config)
    if overrides:
        app.config.update(overrides)
    os.makedirs(app.instance_path, exist_ok=True)
    logging.basicConfig(level=logging.INFO)

    db.init_app(app)
    login_manager.init_app(app)

    # CORS with cookies: origins must be listed explicitly (never "*")
    origins = {app.config["FRONTEND_URL"], "http://127.0.0.1:5173", "http://localhost:5173"}
    CORS(app, origins=[o for o in origins if o], supports_credentials=True)

    @login_manager.user_loader
    def load_user(user_id):
        user = db.session.get(User, int(user_id))
        return user if user and user.status == "active" else None  # disabled users are logged out

    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify(message="Authentication required"), 401

    # ---------- JSON error handlers ----------
    messages = {404: "Resource not found", 413: "File too large (max 5 MB)", 405: "Method not allowed"}

    @app.errorhandler(HTTPException)
    def handle_http(e):
        return jsonify(message=messages.get(e.code, e.description)), e.code

    @app.errorhandler(ModelNotFoundError)
    def handle_model_missing(e):
        return jsonify(message=str(e)), 500

    @app.errorhandler(Exception)
    def handle_unexpected(e):
        db.session.rollback()
        app.logger.exception("Unhandled error")
        return jsonify(message="Internal server error"), 500

    register_blueprints(app)

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    with app.app_context():
        db.create_all()  # creates tables automatically (simple project, no migrations)
        seed_admin(app)

    return app


if __name__ == "__main__":
    # Development server only. In production use: gunicorn "app:create_app()"
    create_app().run(
        host="127.0.0.1",
        port=int(os.getenv("PORT", 5000)),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
