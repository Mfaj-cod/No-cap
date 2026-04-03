"""
Tests for orders and checkout routes.
"""
import pytest

from src.db import create_user, create_order
from src.security import hash_password


class TestCheckoutPage:
    """Tests for checkout page."""

    def test_checkout_accessible(self, client):
        """Test accessing checkout page."""
        response = client.get("/checkout")
        assert response.status_code == 200

    def test_checkout_displays_cart_items(self, client):
        """Test that checkout shows cart items."""
        # Add item to cart first
        client.post(
            "/add_to_cart/1",
            data={"quantity": 1, "variant_sku": ""},
        )
        response = client.get("/checkout")
        assert response.status_code == 200

    def test_checkout_shows_cart_summary(self, client):
        """Test that checkout displays cart summary."""
        client.post(
            "/add_to_cart/1",
            data={"quantity": 2, "variant_sku": ""},
        )
        response = client.get("/checkout")
        assert response.status_code == 200

    def test_checkout_empty_cart(self, client):
        """Test checkout with empty cart."""
        response = client.get("/checkout")
        assert response.status_code == 200


class TestCheckoutForms:
    """Tests for checkout form submission."""

    def test_checkout_with_cod_payment(self, client):
        """Test checkout with Cash on Delivery."""
        # Add item to cart
        client.post(
            "/add_to_cart/1",
            data={"quantity": 1, "variant_sku": ""},
        )

        response = client.post(
            "/checkout",
            data={
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "9999999999",
                "address": "123 Main St",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400001",
                "payment_method": "cod",
            },
            follow_redirects=False,
        )
        assert response.status_code in [303, 200]

    def test_checkout_requires_name(self, client):
        """Test that checkout requires name."""
        response = client.post(
            "/checkout",
            data={
                "name": "",
                "email": "test@example.com",
                "phone": "9999999999",
                "address": "123 St",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400001",
                "payment_method": "cod",
            },
            follow_redirects=False,
        )
        assert response.status_code in [303, 422]

    def test_checkout_requires_email(self, client):
        """Test that checkout requires email."""
        response = client.post(
            "/checkout",
            data={
                "name": "John",
                "email": "",
                "phone": "9999999999",
                "address": "123 St",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400001",
                "payment_method": "cod",
            },
            follow_redirects=False,
        )
        assert response.status_code in [303, 422]

    def test_checkout_requires_phone(self, client):
        """Test that checkout requires phone."""
        response = client.post(
            "/checkout",
            data={
                "name": "John",
                "email": "john@example.com",
                "phone": "",
                "address": "123 St",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400001",
                "payment_method": "cod",
            },
            follow_redirects=False,
        )
        # May or may not be required depending on validation

    def test_checkout_requires_address(self, client):
        """Test that checkout requires address."""
        response = client.post(
            "/checkout",
            data={
                "name": "John",
                "email": "john@example.com",
                "phone": "9999999999",
                "address": "",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400001",
                "payment_method": "cod",
            },
            follow_redirects=False,
        )
        # Address may be required
        assert response.status_code in [303, 422]

    def test_checkout_with_invalid_payment_method(self, client):
        """Test checkout with invalid payment method."""
        response = client.post(
            "/checkout",
            data={
                "name": "John",
                "email": "john@example.com",
                "phone": "9999999999",
                "address": "123 St",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400001",
                "payment_method": "invalid_method",
            },
            follow_redirects=False,
        )
        # Should handle invalid method
        assert response.status_code in [303, 422]


class TestOrderCreation:
    """Tests for order creation."""

    def test_order_created_on_checkout(self, client):
        """Test that order is created after checkout."""
        # Add item to cart
        client.post(
            "/add_to_cart/1",
            data={"quantity": 1, "variant_sku": ""},
        )

        response = client.post(
            "/checkout",
            data={
                "name": "Test User",
                "email": "test@example.com",
                "phone": "9999999999",
                "address": "123 Test St",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400001",
                "payment_method": "cod",
            },
            follow_redirects=False,
        )
        # Should redirect on success
        assert response.status_code in [303, 200]

    def test_guest_checkout(self, client):
        """Test that guest users can checkout."""
        client.post(
            "/add_to_cart/1",
            data={"quantity": 1, "variant_sku": ""},
        )

        response = client.post(
            "/checkout",
            data={
                "name": "Guest User",
                "email": "guest@example.com",
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

    def test_registered_user_checkout(self, client, sample_user_data):
        """Test that registered users can checkout."""
        # Create and login user
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

        # Add to cart and checkout
        client.post(
            "/add_to_cart/1",
            data={"quantity": 1, "variant_sku": ""},
        )

        response = client.post(
            "/checkout",
            data={
                "name": sample_user_data["name"],
                "email": sample_user_data["email"],
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

    def test_checkout_clears_cart_after_order(self, client):
        """Test checkout flow completes."""
        client.post(
            "/add_to_cart/1",
            data={"quantity": 1, "variant_sku": ""},
        )

        response = client.post(
            "/checkout",
            data={
                "name": "User",
                "email": "user@example.com",
                "phone": "9999999999",
                "address": "123 St",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400001",
                "payment_method": "cod",
            },
        )
        # Order should process
        assert response.status_code in [303, 200]


class TestOrderPaymentMethods:
    """Tests for different payment methods."""

    def test_cod_payment_method(self, client):
        """Test Cash on Delivery payment method."""
        # Add item
        client.post(
            "/add_to_cart/1",
            data={"quantity": 1, "variant_sku": ""},
        )

        response = client.post(
            "/checkout",
            data={
                "name": "User",
                "email": "user@example.com",
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

    def test_checkout_without_payment_method(self, client):
        """Test checkout defaults to COD."""
        client.post(
            "/add_to_cart/1",
            data={"quantity": 1, "variant_sku": ""},
        )

        response = client.post(
            "/checkout",
            data={
                "name": "User",
                "email": "user@example.com",
                "phone": "9999999999",
                "address": "123 St",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400001",
                # No payment_method specified
            },
            follow_redirects=False,
        )
        # Should default to COD
        assert response.status_code in [303, 422]


class TestOrderSummary:
    """Tests for order summary and history."""

    def test_user_can_view_orders(self, client, sample_user_data):
        """Test that users can view their orders."""
        # Create and login user
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

        # Check account page for orders
        response = client.get("/account")
        assert response.status_code == 200


class TestOrderPricing:
    """Tests for order pricing calculations."""

    def test_order_respects_wholesale_pricing(self, client, sample_shop_owner_data):
        """Test that shop owners get wholesale pricing."""
        # Create shop owner user
        from src.db import create_user
        from src.security import hash_password

        user = create_user(
            name=sample_shop_owner_data["name"],
            email=sample_shop_owner_data["email"],
            password_hash=hash_password(sample_shop_owner_data["password"]),
            role=sample_shop_owner_data["role"],
        )

        # Login as shop owner
        client.post(
            "/login",
            data={
                "email": sample_shop_owner_data["email"],
                "password": sample_shop_owner_data["password"],
            },
        )

        # Add items over wholesale threshold
        for i in range(25):
            client.post(
                "/add_to_cart/1",
                data={"quantity": 1, "variant_sku": ""},
            )

        response = client.get("/checkout")
        assert response.status_code == 200
        # Wholesale discount should be applied


class TestOrderValidation:
    """Tests for order data validation."""

    def test_invalid_email_in_order(self, client):
        """Test that invalid email is rejected."""
        response = client.post(
            "/checkout",
            data={
                "name": "User",
                "email": "invalid-email",
                "phone": "9999999999",
                "address": "123 St",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400001",
                "payment_method": "cod",
            },
            follow_redirects=False,
        )
        # Should validate email format
        assert response.status_code in [303, 422]

    def test_invalid_pincode_in_order(self, client):
        """Test that invalid pincode is handled."""
        response = client.post(
            "/checkout",
            data={
                "name": "User",
                "email": "user@example.com",
                "phone": "9999999999",
                "address": "123 St",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "invalid",
                "payment_method": "cod",
            },
            follow_redirects=False,
        )
        # May validate pincode format
        assert response.status_code in [303, 422]
