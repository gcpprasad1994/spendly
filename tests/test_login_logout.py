import pytest
from werkzeug.security import generate_password_hash

import database.db as db

EMAIL = "asha@example.com"
PASSWORD = "password123"


@pytest.fixture
def user(client):
    conn = db.get_db()
    try:
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Asha Rao", EMAIL, generate_password_hash(PASSWORD)),
        )
        conn.commit()
    finally:
        conn.close()


def _login(client, email=EMAIL, password=PASSWORD):
    return client.post("/login", data={"email": email, "password": password})


def test_get_login(client):
    assert client.get("/login").status_code == 200


def test_valid_login_sets_session(client, user):
    resp = _login(client)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/profile")
    with client.session_transaction() as sess:
        assert sess["user_id"]
        assert sess["name"] == "Asha Rao"
        assert not any("hash" in key for key in sess)
        assert PASSWORD not in str(dict(sess))


def test_email_case_insensitive(client, user):
    assert _login(client, email="ASHA@Example.com").status_code == 302


def test_wrong_password_and_unknown_email_are_identical(client, user):
    wrong = _login(client, password="wrong-password")
    unknown = _login(client, email="nobody@example.com")
    for resp in (wrong, unknown):
        assert resp.status_code == 200
        assert b"Invalid email or password." in resp.data
    with client.session_transaction() as sess:
        assert "user_id" not in sess


@pytest.mark.parametrize("kwargs", [{"email": ""}, {"password": ""}])
def test_empty_fields_rejected(client, user, kwargs):
    resp = _login(client, **kwargs)
    assert resp.status_code == 200
    assert b"Invalid email or password." in resp.data
    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_failed_login_keeps_email_not_password(client, user):
    resp = _login(client, password="wrong-password")
    assert f'value="{EMAIL}"'.encode() in resp.data
    assert b"wrong-password" not in resp.data


def test_login_page_redirects_when_logged_in(client, user):
    _login(client)
    resp = client.get("/login")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/profile")


def test_navbar_reflects_login_state(client, user):
    page = client.get("/").data
    assert b"Get started" in page and b"Sign out" not in page

    _login(client)
    page = client.get("/").data
    assert b"Asha Rao" in page and b"Sign out" in page and b"Get started" not in page

    client.get("/logout")
    page = client.get("/").data
    assert b"Get started" in page and b"Sign out" not in page


def test_logout_clears_session(client, user):
    _login(client)
    resp = client.get("/logout")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/")
    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_logout_when_logged_out(client):
    resp = client.get("/logout")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/")
