import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def _database_url():
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        url = "sqlite:///instance/sentiment.db"
    # Some hosts (Heroku/Render) still give "postgres://", SQLAlchemy needs "postgresql://"
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    # Make relative SQLite paths relative to the backend folder
    if url.startswith("sqlite:///") and not url.startswith("sqlite:////") and url != "sqlite://":
        rel = url[len("sqlite:///"):]
        url = "sqlite:///" + os.path.join(BASE_DIR, rel)
    return url


IS_PRODUCTION = os.getenv("FLASK_ENV", "development").lower() == "production"
_secret = os.getenv("SECRET_KEY", "dev-only-secret-key")
if IS_PRODUCTION and _secret in ("", "change-this-secret", "dev-only-secret-key"):
    raise RuntimeError("Set a strong SECRET_KEY environment variable in production.")


class Config:
    BASE_DIR = BASE_DIR
    SECRET_KEY = _secret
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:5173").rstrip("/")
    ADMIN_NAME = os.getenv("ADMIN_NAME", "Administrator")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB upload limit
    # Session cookie settings.
    # Production (frontend and backend on different domains) needs SameSite=None + Secure (HTTPS).
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "None" if IS_PRODUCTION else "Lax"
    SESSION_COOKIE_SECURE = IS_PRODUCTION
