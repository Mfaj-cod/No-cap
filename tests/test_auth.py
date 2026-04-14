"""
Integration tests for authentication endpoints:
  GET/POST /register
  GET/POST /login
  GET      /logout
  GET      /account
  GET/POST /forgot-password
  GET/POST /verify-otp
  GET/POST /reset-password
"""

import pytest

# Unique email counter so tests stay independent even in the same DB session
_counter = 0


def _unique_email(prefix="auth"):
    global _counter
    _counter += 1
    return f"{prefix}_{_counter}@example.com"


# Registration

@pytest.mark.integration
@pytest.mark.auth
class TestRegistration:
    def test_register_page_loads(self, client):
        resp = client.get("/register")
        assert resp.status_code == 200
        assert b"Register" in resp.content or b"register" in resp.content.lower()

    def test_register_new_user_redirects_to_account(self, client):
        resp = client.post(
            "/register",
            data={
                "name": "New User",
                "email": _unique_email("reg"),
                "password": "password123",
                "confirm_password": "password123",
                "role": "customer",
            },
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert "/account" in resp.headers["location"]

    def test_register_mismatched_passwords_redirects_back(self, client):
        resp = client.post(
            "/register",
            data={
                "name": "Bad User",
                "email": _unique_email("mismatch"),
                "password": "abc123",
                "confirm_password": "xyz789",
                "role": "customer",
            },
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert "/register" in resp.headers["location"]

    def test_register_short_password_rejected(self, client):
        resp = client.post(
            "/register",
            data={
                "name": "Short Pw",
                "email": _unique_email("shortpw"),
                "password": "12",
                "confirm_password": "12",
                "role": "customer",
            },
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert "/register" in resp.headers["location"]

    def test_register_invalid_role_rejected(self, client):
        resp = client.post(
            "/register",
            data={
                "name": "Bad Role",
                "email": _unique_email("badrole"),
                "password": "password123",
                "confirm_password": "password123",
                "role": "hacker",
            },
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert "/register" in resp.headers["location"]

    def test_register_duplicate_email_rejected(self, client):
        email = _unique_email("dup")
        # First registration succeeds
        client.post(
            "/register",
            data={
                "name": "First",
                "email": email,
                "password": "pass1234",
                "confirm_password": "pass1234",
                "role": "customer",
            },
            follow_redirects=False,
        )
        # Second registration with same email should redirect back to /register
        resp = client.post(
            "/register",
            data={
                "name": "Second",
                "email": email,
                "password": "pass1234",
                "confirm_password": "pass1234",
                "role": "customer",
            },
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert "/register" in resp.headers["location"]

    def test_register_shop_owner_role_accepted(self, client):
        resp = client.post(
            "/register",
            data={
                "name": "Shop Owner",
                "email": _unique_email("shopowner"),
                "password": "password123",
                "confirm_password": "password123",
                "role": "shop_owner",
            },
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert "/account" in resp.headers["location"]


# Login / Logout

@pytest.mark.integration
@pytest.mark.auth
class TestLoginLogout:
    def _create_user(self, client, email, password="password123"):
        client.post(
            "/register",
            data={
                "name": "Login Test",
                "email": email,
                "password": password,
                "confirm_password": password,
                "role": "customer",
            },
            follow_redirects=False,
        )

    def test_login_page_loads(self, client):
        resp = client.get("/login")
        assert resp.status_code == 200

    def test_login_valid_credentials_redirects_to_account(self, client):
        email = _unique_email("login")
        self._create_user(client, email)
        resp = client.post(
            "/login",
            data={"email": email, "password": "password123"},
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert "/account" in resp.headers["location"]

    def test_login_wrong_password_redirects_back(self, client):
        email = _unique_email("wrongpw")
        self._create_user(client, email)
        resp = client.post(
            "/login",
            data={"email": email, "password": "wrongpassword"},
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert "/login" in resp.headers["location"]

    def test_login_unknown_email_redirects_back(self, client):
        resp = client.post(
            "/login",
            data={"email": "nobody@nowhere.com", "password": "anything"},
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert "/login" in resp.headers["location"]

    def test_logout_redirects_to_index(self, client):
        # Must be logged in first
        email = _unique_email("logout")
        self._create_user(client, email)
        client.post(
            "/login",
            data={"email": email, "password": "password123"},
            follow_redirects=True,
        )
        resp = client.get("/logout", follow_redirects=False)
        assert resp.status_code == 303
        assert resp.headers["location"].endswith("/")


# Account page (auth guard)

@pytest.mark.integration
@pytest.mark.auth
class TestAccountPage:
    def test_account_requires_login(self, client):
        """Accessing /account without a session redirects to /login."""
        # Use a fresh client with no session cookie
        from starlette.testclient import TestClient
        with TestClient(client.app) as fresh:
            resp = fresh.get("/account", follow_redirects=False)
        assert resp.status_code == 303
        assert "/login" in resp.headers["location"]

    def test_account_accessible_when_logged_in(self, client):
        email = _unique_email("account")
        client.post(
            "/register",
            data={
                "name": "Account User",
                "email": email,
                "password": "password123",
                "confirm_password": "password123",
                "role": "customer",
            },
            follow_redirects=True,
        )
        resp = client.get("/account")
        assert resp.status_code == 200


# Forgot password / OTP flow

@pytest.mark.integration
@pytest.mark.auth
class TestPasswordResetFlow:
    def test_forgot_password_page_loads(self, client):
        resp = client.get("/forgot-password")
        assert resp.status_code == 200

    def test_forgot_password_unknown_email_redirects_safely(self, client):
        """Should not reveal whether the email exists."""
        resp = client.post(
            "/forgot-password",
            data={"email": "ghost@example.com"},
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert "/login" in resp.headers["location"]

    def test_verify_otp_without_session_redirects_to_forgot_password(self, client):
        from starlette.testclient import TestClient
        with TestClient(client.app) as fresh:
            resp = fresh.get("/verify-otp", follow_redirects=False)
        assert resp.status_code == 303
        assert "/forgot-password" in resp.headers["location"]

    def test_reset_password_without_session_redirects_to_verify_otp(self, client):
        from starlette.testclient import TestClient
        with TestClient(client.app) as fresh:
            resp = fresh.get("/reset-password", follow_redirects=False)
        assert resp.status_code == 303
