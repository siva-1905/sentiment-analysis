import pytest

from app import create_app


@pytest.fixture
def app():
    return create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",  # in-memory database
        "SECRET_KEY": "test-secret",
        "ADMIN_EMAIL": "admin@test.com",
        "ADMIN_PASSWORD": "adminpass",
    })


@pytest.fixture
def client(app):
    return app.test_client()
