import pytest
from werkzeug.security import check_password_hash

import database.db as db
from app import app as flask_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    db.init_db()
    flask_app.config["TESTING"] = True
    return flask_app.test_client()


def _users(email=None):
    conn = db.get_db()
    try:
        if email:
            return conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchall()
        return conn.execute("SELECT * FROM users").fetchall()
    finally:
        conn.close()


def _post(client, name="Asha Rao", email="asha@example.com", password="password123"):
    return client.post("/register", data={"name": name, "email": email, "password": password})


def test_get_register(client):
    assert client.get("/register").status_code == 200


def test_valid_registration_redirects_to_login(client):
    resp = _post(client)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login?registered=1")
    assert b"Account created" in client.get(resp.headers["Location"]).data


def test_password_is_hashed(client):
    _post(client)
    row = _users("asha@example.com")[0]
    assert row["password_hash"] != "password123"
    assert check_password_hash(row["password_hash"], "password123")


def test_duplicate_email_rejected(client):
    _post(client)
    resp = _post(client, name="Other")
    assert resp.status_code == 200
    assert b"already exists" in resp.data
    assert len(_users("asha@example.com")) == 1


def test_duplicate_email_case_insensitive(client):
    _post(client, email="a@x.com")
    resp = _post(client, email="A@X.COM")
    assert b"already exists" in resp.data
    assert len(_users()) == 1


@pytest.mark.parametrize(
    "kwargs",
    [
        {"name": ""},
        {"email": ""},
        {"password": ""},
        {"email": "no-at-sign"},
        {"email": "a@nodot"},
        {"password": "1234567"},
    ],
)
def test_invalid_input_rejected(client, kwargs):
    resp = _post(client, **kwargs)
    assert resp.status_code == 200
    assert b"auth-error" in resp.data
    assert _users() == []


def test_form_repopulated_but_not_password(client):
    resp = _post(client, name="Asha Rao", email="asha@example.com", password="short")
    assert b'value="Asha Rao"' in resp.data
    assert b'value="asha@example.com"' in resp.data
    assert b"short" not in resp.data.replace(b"Password must be at least", b"")
