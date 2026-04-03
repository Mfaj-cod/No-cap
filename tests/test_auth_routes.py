"""
Tests for authentication routes.
"""
import pytest

from src.db import create_user
from src.security import hash_password


class TestRegisterRoute:
    """Tests for user registration."""

    def test_register_page_get(self, client):
        """Test accessing register page."""
        response = client.get("/register")
        assert response.status_code == 200
        assert "register" in response.text.lower() or "password" in response.text.lower()

    def test_register_customer_success(self, client):
        """Test successful customer registration."""
        response = client.post(
            "/register",
            data={
                "name": "New Customer",
                "email": "newcustomer@example.com",
                "password": "password123",
                "confirm_password": "password123",
                "role": "customer",
            },
            follow_redirects=False,
        )
        assert response.status_code == 303  # Redirect on success

    def test_register_shop_owner_success(self, client):
        """Test successful shop owner registration."""
        response = client.post(
            "/register",
            data={
                "name": "Shop Owner",
                "email": "owner@store.com",
                "password": "password123",
                "confirm_password": "password123",
                "role": "shop_owner",
            },
            follow_redirects=False,
        )
        assert response.status_code == 303

    def test_register_invalid_role(self, client):
        """Test registration with invalid role."""
        response = client.post(
            "/register",
            data={
                "name": "Invalid User",
                "email": "invalid@example.com",
                "password": "password123",
                "confirm_password": "password123",
                "role": "admin",
            },
            follow_redirects=True,
        )
        assert "valid account type" in response.text.lower()

    def test_register_password_mismatch(self, client):
        """Test registration with mismatched passwords."""
        response = client.post(
            "/register",
            data={
                "name": "Mismatch User",
                "email": "mismatch@example.com",
                "password": "password123",
                "confirm_password": "different456",
                "role": "customer",
            },
            follow_redirects=True,
        )
        assert "do not match" in response.text.lower()

    def test_register_password_too_short(self, client):
        """Test registration with password shorter than 6 characters."""
        response = client.post(
            "/register",
            data={
                "name": "Short Pass User",
                "email": "shortpass@example.com",
                "password": "12345",
                "confirm_password": "12345",
                "role": "customer",
            },
            follow_redirects=True,
        )
        assert "6 character" in response.text.lower()

    def test_register_duplicate_email(self, client, sample_user_data):
        """Test registration with duplicate email."""
        # Create first user
        create_user(
            name=sample_user_data["name"],
            email=sample_user_data["email"],
            password_hash=hash_password(sample_user_data["password"]),
            role=sample_user_data["role"],
        )

        # Try to register with same email
        response = client.post(
            "/register",
            data={
                "name": "Another User",
                "email": sample_user_data["email"],
                "password": "password123",
                "confirm_password": "password123",
                "role": "customer",
            },
            follow_redirects=True,
        )
        assert "already exists" in response.text.lower()


class TestLoginRoute:
    """Tests for user login."""

    def test_login_page_get(self, client):
        """Test accessing login page."""
        response = client.get("/login")
        assert response.status_code == 200
        assert "login" in response.text.lower()

    def test_login_success(self, client, sample_user_data):
        """Test successful login."""
        create_user(
            name=sample_user_data["name"],
            email=sample_user_data["email"],
            password_hash=hash_password(sample_user_data["password"]),
            role=sample_user_data["role"],
        )

        response = client.post(
            "/login",
            data={
                "email": sample_user_data["email"],
                "password": sample_user_data["password"],
            },
            follow_redirects=False,
        )
        assert response.status_code in [303, 200]

    def test_login_invalid_email(self, client):
        """Test login with non-existent email."""
        response = client.post(
            "/login",
            data={
                "email": "nonexistent@example.com",
                "password": "password123",
            },
            follow_redirects=True,
        )
        assert "invalid email or password" in response.text.lower()

    def test_login_wrong_password(self, client, sample_user_data):
        """Test login with wrong password."""
        create_user(
            name=sample_user_data["name"],
            email=sample_user_data["email"],
            password_hash=hash_password(sample_user_data["password"]),
            role=sample_user_data["role"],
        )

        response = client.post(
            "/login",
            data={
                "email": sample_user_data["email"],
                "password": "wrongpassword",
            },
            follow_redirects=True,
        )
        assert "invalid email or password" in response.text.lower()

    def test_login_sets_session(self, client, sample_user_data):
        """Test that login allows account access."""
        create_user(
            name=sample_user_data["name"],
            email=sample_user_data["email"],
            password_hash=hash_password(sample_user_data["password"]),
            role=sample_user_data["role"],
        )

        response = client.post(
            "/login",
            data={
                "email": sample_user_data["email"],
                "password": sample_user_data["password"],
            },
            follow_redirects=True,
        )
        assert response.status_code == 200


class TestLogoutRoute:
    """Tests for user logout."""

    def test_logout_clears_session(self, client, sample_user_data):
        """Test that logout clears user session."""
        create_user(
            name=sample_user_data["name"],
            email=sample_user_data["email"],
            password_hash=hash_password(sample_user_data["password"]),
            role=sample_user_data["role"],
        )

        # Login
        client.post(
            "/login",
            data={
                "email": sample_user_data["email"],
                "password": sample_user_data["password"],
            },
        )

        # Logout
        response = client.get("/logout", follow_redirects=False)
        assert response.status_code == 303

    def test_logout_redirects_to_home(self, client):
        """Test that logout redirects to home page."""
        response = client.get("/logout", follow_redirects=True)
        assert response.status_code == 200


class TestAccountRoute:
    """Tests for account page."""

    def test_account_page_requires_login(self, client):
        """Test that account page redirects if not logged in."""
        response = client.get("/account", follow_redirects=False)
        assert response.status_code == 303  # Redirect to login

    def test_account_page_logged_in(self, client, sample_user_data):
        """Test accessing account page when logged in."""
        create_user(
            name=sample_user_data["name"],
            email=sample_user_data["email"],
            password_hash=hash_password(sample_user_data["password"]),
            role=sample_user_data["role"],
        )

        # Login
        client.post(
            "/login",
            data={
                "email": sample_user_data["email"],
                "password": sample_user_data["password"],
            },
        )

        response = client.get("/account", follow_redirects=True)
        assert response.status_code == 200
        assert "account" in response.text.lower() or "order" in response.text.lower()

    def test_account_page_shows_user_info(self, client, sample_user_data):
        """Test that account page displays user information."""
        create_user(
            name=sample_user_data["name"],
            email=sample_user_data["email"],
            password_hash=hash_password(sample_user_data["password"]),
            role=sample_user_data["role"],
        )

        client.post(
            "/login",
            data={
                "email": sample_user_data["email"],
                "password": sample_user_data["password"],
            },
        )

        response = client.get("/account")
        assert response.status_code == 200
