from routes.admin import admin_bp
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.reports import reports_bp
from routes.sentiment import sentiment_bp


def register_blueprints(app):
    for bp in (auth_bp, sentiment_bp, dashboard_bp, reports_bp, admin_bp):
        app.register_blueprint(bp)
