import pytest

USER = {"name": "Siva", "email": "siva@example.com", "password": "123456"}


@pytest.fixture(autouse=True)
def fake_predictor(monkeypatch):
    """Use a fake predictor so tests do not need the trained model."""
    monkeypatch.setattr(
        "services.predictor.predict_sentiment",
        lambda text: {"sentiment": "Positive", "confidence": 93.14},
    )


def register_and_login(client, data=USER):
    client.post("/api/auth/register", json=data)
    return client.post("/api/auth/login", json={"email": data["email"], "password": data["password"]})


def test_register_success_and_no_password_leak(client):
    res = client.post("/api/auth/register", json=USER)
    assert res.status_code == 201
    assert "password" not in res.get_json()["user"]


def test_register_validation_and_duplicate(client):
    assert client.post("/api/auth/register", json={"name": "x"}).status_code == 400
    assert client.post("/api/auth/register", json={**USER, "email": "bad"}).status_code == 400
    client.post("/api/auth/register", json=USER)
    assert client.post("/api/auth/register", json=USER).status_code == 409


def test_login_and_me(client):
    assert register_and_login(client).status_code == 200
    assert client.get("/api/auth/me").get_json()["user"]["email"] == USER["email"]


def test_login_invalid_password(client):
    client.post("/api/auth/register", json=USER)
    res = client.post("/api/auth/login", json={"email": USER["email"], "password": "wrong"})
    assert res.status_code == 401


def test_me_requires_login(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401
    assert res.get_json()["message"] == "Authentication required"


def test_predict_requires_login(client):
    assert client.post("/api/sentiment/predict", json={"text": "great"}).status_code == 401


def test_predict_history_delete(client):
    register_and_login(client)
    assert client.post("/api/sentiment/predict", json={"text": ""}).status_code == 400
    res = client.post("/api/sentiment/predict", json={"text": "This movie was fantastic."})
    assert res.status_code == 201
    assert res.get_json()["sentiment"] == "Positive"
    history = client.get("/api/sentiment/history").get_json()["history"]
    assert len(history) == 1
    assert client.delete(f"/api/sentiment/history/{history[0]['id']}").status_code == 200
    assert client.get("/api/sentiment/history").get_json()["history"] == []


def test_dashboard_counts(client):
    register_and_login(client)
    client.post("/api/sentiment/predict", json={"text": "good"})
    client.post("/api/sentiment/predict", json={"text": "great"})
    data = client.get("/api/dashboard").get_json()
    assert data["total"] == 2 and data["positive"] == 2 and data["negative"] == 0


def test_user_cannot_delete_other_users_result(app):
    a, b = app.test_client(), app.test_client()
    register_and_login(a)
    rid = a.post("/api/sentiment/predict", json={"text": "nice"}).get_json()["id"]
    register_and_login(b, {"name": "B", "email": "b@example.com", "password": "123456"})
    assert b.delete(f"/api/sentiment/history/{rid}").status_code == 404


def test_normal_user_gets_403_on_admin_endpoints(client):
    register_and_login(client)
    assert client.get("/api/admin/users").status_code == 403
    assert client.get("/api/admin/audit-logs").status_code == 403
    assert client.patch("/api/admin/users/1/role", json={"role": "user"}).status_code == 403


def test_anonymous_gets_401_on_admin_endpoints(client):
    assert client.get("/api/admin/users").status_code == 401


def test_admin_can_manage_users(client):
    client.post("/api/auth/login", json={"email": "admin@test.com", "password": "adminpass"})
    assert client.get("/api/admin/users").status_code == 200
    created = client.post("/api/admin/users", json={**USER, "role": "user"})
    assert created.status_code == 201
    uid = created.get_json()["user"]["id"]
    assert client.patch(f"/api/admin/users/{uid}/status", json={"status": "disabled"}).status_code == 200
    assert client.get("/api/admin/audit-logs").status_code == 200


def test_disabled_user_cannot_login(client):
    client.post("/api/auth/register", json=USER)
    client.post("/api/auth/login", json={"email": "admin@test.com", "password": "adminpass"})
    uid = client.get("/api/admin/users").get_json()["users"][-1]["id"]
    client.patch(f"/api/admin/users/{uid}/status", json={"status": "disabled"})
    client.post("/api/auth/logout")
    res = client.post("/api/auth/login", json={"email": USER["email"], "password": USER["password"]})
    assert res.status_code == 403


def test_csv_upload_and_reports(client):
    import io
    register_and_login(client)
    csv = b"id,Review\n1,Loved it\n2,Hated it\n"
    res = client.post("/api/sentiment/upload", data={"file": (io.BytesIO(csv), "r.csv")},
                      content_type="multipart/form-data")
    assert res.status_code == 201 and res.get_json()["count"] == 2
    bad = client.post("/api/sentiment/upload", data={"file": (io.BytesIO(b"a"), "r.txt")},
                      content_type="multipart/form-data")
    assert bad.status_code == 400
    for kind in ("csv", "excel", "pdf"):
        assert client.get(f"/api/reports/{kind}").status_code == 200
