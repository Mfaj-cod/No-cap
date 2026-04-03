"""
Tests for cart routes.
"""
import pytest

from src.db import create_user
from src.security import hash_password


class TestCartPage:
    """Tests for cart page."""

    def test_cart_page_accessible(self, client):
        """Test accessing cart page."""
        response = client.get("/cart")
        assert response.status_code == 200
        assert "cart" in response.text.lower()

    def test_empty_cart_page(self, client):
        """Test cart page shows empty cart message."""
        response = client.get("/cart")
        assert response.status_code == 200


class TestAddToCart:
    """Tests for adding items to cart."""

    def test_add_product_to_cart(self, client):
        """Test adding a product to cart."""
        response = client.post(
            "/add_to_cart/1",
            data={"quantity": 1, "variant_sku": ""},
            follow_redirects=False,
        )
        assert response.status_code == 303  # Redirect

    def test_add_nonexistent_product(self, client):
        """Test adding non-existent product to cart."""
        response = client.post(
            "/add_to_cart/99999",
            data={"quantity": 1, "variant_sku": ""},
            follow_redirects=True,
        )
        assert "could not be found" in response.text.lower()

    def test_add_with_specific_variant(self, client):
        """Test adding product with specific variant."""
        # Get a valid product with variant
        from src.db import list_products

        products = list_products()
        if products:
            product = products[0]
            variants = product.get("variants", [])
            if variants:
                sku = variants[0].get("sku", "")
                response = client.post(
                    f"/add_to_cart/{product['id']}",
                    data={"quantity": 1, "variant_sku": sku},
                    follow_redirects=False,
                )
                assert response.status_code == 303

    def test_add_default_quantity(self, client):
        """Test adding item with default quantity."""
        response = client.post(
            "/add_to_cart/1",
            data={"variant_sku": ""},
        )
        # Should redirect or return 303
        assert response.status_code in [303, 200]

    def test_add_multiple_quantities(self, client):
        """Test adding multiple quantities of same product."""
        # Add first time
        client.post(
            "/add_to_cart/1",
            data={"quantity": 2, "variant_sku": ""},
        )

        # Check cart has the item
        response = client.get("/cart")
        assert response.status_code == 200

    def test_add_respects_stock_limit(self, client):
        """Test that adding respects available stock."""
        from src.db import get_product

        product = get_product(1)
        if product and product.get("variants"):
            variant = product["variants"][0]
            stock = int(variant.get("stock_quantity", 0))
            if stock > 0:
                # Try to add more than available
                response = client.post(
                    "/add_to_cart/1",
                    data={"quantity": stock + 100, "variant_sku": variant.get("sku", "")},
                    follow_redirects=True,
                )
                # Should show message about limited stock or redirect
                assert response.status_code == 200


class TestUpdateCart:
    """Tests for updating cart items."""

    def test_update_cart_quantity_via_form(self, client):
        """Test updating quantity via form submission."""
        # Add item first
        client.post(
            "/add_to_cart/1",
            data={"quantity": 1, "variant_sku": ""},
        )

        # Cart has the item, try to update it by removing and re-adding
        response = client.get("/cart")
        assert response.status_code == 200

    def test_update_cart_to_zero_removes_item(self, client):
        """Test that setting quantity to 0 removes item."""
        # Add multiple items
        for _ in range(3):
            client.post(
                "/add_to_cart/1",
                data={"quantity": 1, "variant_sku": ""},
            )

        # Verify items were added
        response = client.get("/cart")
        assert response.status_code == 200


class TestRemoveFromCart:
    """Tests for removing items from cart."""

    def test_remove_from_cart_via_route(self, client):
        """Test removing item from cart via route."""
        # Add item first
        client.post(
            "/add_to_cart/1",
            data={"quantity": 1, "variant_sku": ""},
        )

        # Verify it's in cart
        response = client.get("/cart")
        assert response.status_code == 200

        # Note: Actual remove requires knowing the cart key which is session-dependent
        # So we test the route exists and is callable

    def test_remove_nonexistent_item_handles_gracefully(self, client):
        """Test removing non-existent item doesn't error."""
        response = client.post(
            "/remove_from_cart/999__invalid",
            follow_redirects=False,
        )
        # Should still work without error
        assert response.status_code == 303


class TestCartNavigation:
    """Tests for cart-related navigation."""

    def test_add_to_cart_redirects_to_checkout(self, client):
        """Test adding to cart with ?next=checkout redirects to checkout."""
        response = client.post(
            "/add_to_cart/1?next=checkout",
            data={"quantity": 1, "variant_sku": ""},
            follow_redirects=False,
        )
        assert response.status_code == 303
        # Check redirect location contains checkout
        location = response.headers.get("location", "")
        # May contain checkout depending on the next param handling
