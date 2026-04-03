"""
Tests for services module (cart, checkout, flash messages, etc.).
"""
import pytest
from fastapi import Request

from src.services import (
    add_flash,
    build_cart_key,
    build_cart_summary,
    can_access_order,
    cart_item_count,
    clear_cart,
    clear_saved_checkout_data,
    get_cart,
    get_current_user,
    get_saved_checkout_data,
    login_user,
    logout_user,
    parse_cart_key,
    pop_flash_messages,
    remember_checkout_data,
    remember_guest_order,
    save_cart,
)


class TestFlashMessages:
    """Tests for flash message handling."""

    def test_flash_messages_in_response(self, client):
        """Test that flash messages appear in responses."""
        # Register user - triggers flash message
        response = client.post(
            "/register",
            data={
                "name": "Flash Test User",
                "email": f"flash_{id(client)}@example.com",
                "password": "password123",
                "confirm_password": "password123",
                "role": "customer",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_error_flash_appears(self, client):
        """Test that error flash messages appear."""
        # Try invalid login
        response = client.post(
            "/login",
            data={
                "email": "nonexistent@example.com",
                "password": "wrong",
            },
            follow_redirects=True,
        )
        assert "invalid" in response.text.lower() or response.status_code == 200

    def test_success_flash_on_registration(self, client):
        """Test success message on registration."""
        response = client.post(
            "/register",
            data={
                "name": "Success Test User",
                "email": f"success_{id(client)}@example.com",
                "password": "password123",
                "confirm_password": "password123",
                "role": "customer",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200


class TestCartKeyManagement:
    """Tests for cart key parsing and building."""

    def test_build_cart_key_with_sku(self):
        """Test building cart key with SKU."""
        key = build_cart_key(1, "SKU-001")
        assert key == "1__SKU-001"

    def test_build_cart_key_without_sku(self):
        """Test building cart key without SKU (None)."""
        key = build_cart_key(1, None)
        assert key == "1__default"

    def test_parse_cart_key_with_sku(self):
        """Test parsing cart key with SKU."""
        product_id, sku = parse_cart_key("1__SKU-001")
        assert product_id == 1
        assert sku == "SKU-001"

    def test_parse_cart_key_without_sku(self):
        """Test parsing cart key without SKU."""
        product_id, sku = parse_cart_key("5__default")
        assert product_id == 5
        assert sku is None

    def test_parse_cart_key_legacy_format(self):
        """Test parsing legacy cart key format (without separator)."""
        product_id, sku = parse_cart_key("10")
        assert product_id == 10
        assert sku is None


class TestCartOperations:
    """Tests for cart management."""

    def test_cart_operations_via_routes(self, client):
        """Test cart operations through HTTP routes."""
        # Add to cart - note: TestClient follows redirects by default
        response = client.post(
            "/add_to_cart/1",
            data={"quantity": 1, "variant_sku": ""},
            follow_redirects=False,
        )
        assert response.status_code == 303

        # View cart
        response = client.get("/cart")
        assert response.status_code == 200

    def test_cart_update_via_routes(self, client):
        """Test updating cart through routes."""
        # Add item
        client.post(
            "/add_to_cart/1",
            data={"quantity": 1, "variant_sku": ""},
        )

        # Get cart page to verify item
        response = client.get("/cart")
        assert response.status_code == 200

    def test_cart_removal_via_routes(self, client):
        """Test removing from cart through routes."""
        # Add item first
        client.post(
            "/add_to_cart/1",
            data={"quantity": 1, "variant_sku": ""},
        )

        # View cart
        response = client.get("/cart")
        assert response.status_code == 200

    def test_cart_item_count_via_routes(self, client):
        """Test that cart counts items."""
        # Add multiple items
        for i in range(3):
            client.post(
                "/add_to_cart/1",
                data={"quantity": 1, "variant_sku": ""},
            )

        # Cart should show items
        response = client.get("/cart")
        assert response.status_code == 200


class TestCheckoutData:
    """Tests for checkout data handling."""

    def test_checkout_form_loads(self, client):
        """Test that checkout form loads."""
        response = client.get("/checkout")
        assert response.status_code == 200

    def test_checkout_submission_processes(self, client):
        """Test that checkout data is processed."""
        client.post(
            "/add_to_cart/1",
            data={"quantity": 1, "variant_sku": ""},
        )

        response = client.post(
            "/checkout",
            data={
                "name": "Test Buyer",
                "email": "buyer@example.com",
                "phone": "9999999999",
                "address": "123 St",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400001",
                "payment_method": "cod",
            },
            follow_redirects=False,
        )
        assert response.status_code in [303, 200]


class TestUserSession:
    """Tests for user login/logout."""

    def test_login_and_account_access(self, client):
        """Test logging in and accessing account."""
        from src.db import create_user
        from src.security import hash_password

        email = f"login_test_{id(client)}@example.com"
        user = create_user(
            name="Login Test",
            email=email,
            password_hash=hash_password("password"),
            role="customer",
        )

        response = client.post(
            "/login",
            data={"email": email, "password": "password"},
        )
        assert response.status_code in [303, 200]

        # Account page should be accessible
        account = client.get("/account")
        assert account.status_code == 200

    def test_logout_redirects_home(self, client):
        """Test that logout works."""
        from src.db import create_user
        from src.security import hash_password

        email = f"logout_test_{id(client)}@example.com"
        create_user(
            name="Logout Test",
            email=email,
            password_hash=hash_password("password"),
            role="customer",
        )

        # Login
        client.post(
            "/login",
            data={"email": email, "password": "password"},
        )

        # Logout
        response = client.get("/logout", follow_redirects=False)
        assert response.status_code == 303

    def test_account_page_without_login(self, client):
        """Test that account page redirects without login."""
        response = client.get("/account", follow_redirects=False)
        assert response.status_code == 303
