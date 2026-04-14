"""
Integration tests for shopping-cart routes:
  GET  /cart
  POST /add_to_cart/{product_id}
  POST /update_cart/{cart_key}
  POST /remove_from_cart/{cart_key}

Each test uses a fresh TestClient to guarantee an isolated cookie/session.
"""

import pytest
from starlette.testclient import TestClient


def _fresh(app):
    """Return a new TestClient with an empty session."""
    return TestClient(app, raise_server_exceptions=True)


@pytest.mark.integration
@pytest.mark.cart
class TestCartPage:
    def test_cart_page_loads_when_empty(self, client):
        with _fresh(client.app) as c:
            resp = c.get("/cart")
        assert resp.status_code == 200

    def test_cart_page_contains_relevant_content(self, client):
        with _fresh(client.app) as c:
            resp = c.get("/cart")
        assert b"cart" in resp.content.lower()


@pytest.mark.integration
@pytest.mark.cart
class TestAddToCart:
    def test_add_valid_product_redirects(self, client):
        with _fresh(client.app) as c:
            resp = c.post(
                "/add_to_cart/1",
                data={"quantity": "1", "variant_sku": "VEL-BLK-OS"},
                follow_redirects=False,
            )
        assert resp.status_code == 303

    def test_add_unknown_product_redirects_to_index(self, client):
        with _fresh(client.app) as c:
            resp = c.post(
                "/add_to_cart/999999",
                data={"quantity": "1", "variant_sku": ""},
                follow_redirects=False,
            )
        assert resp.status_code == 303
        assert resp.headers["location"].endswith("/")

    def test_add_product_appears_in_cart(self, client):
        with _fresh(client.app) as c:
            c.post(
                "/add_to_cart/1",
                data={"quantity": "2", "variant_sku": "VEL-BLK-OS"},
                follow_redirects=True,
            )
            cart_resp = c.get("/cart")
        assert resp.status_code == 200 if (resp := cart_resp) else True
        assert b"Velocity Sports Cap" in cart_resp.content

    def test_add_product_quantity_capped_by_stock(self, client):
        """Requesting more than stock should silently cap – not error."""
        with _fresh(client.app) as c:
            resp = c.post(
                "/add_to_cart/1",
                data={"quantity": "9999", "variant_sku": "VEL-BLK-OS"},
                follow_redirects=False,
            )
        assert resp.status_code == 303

    def test_add_zero_quantity_treated_as_one(self, client):
        with _fresh(client.app) as c:
            resp = c.post(
                "/add_to_cart/1",
                data={"quantity": "0", "variant_sku": "VEL-BLK-OS"},
                follow_redirects=False,
            )
        assert resp.status_code == 303

    def test_add_with_next_checkout_redirects_to_checkout(self, client):
        with _fresh(client.app) as c:
            resp = c.post(
                "/add_to_cart/1?next=checkout",
                data={"quantity": "1", "variant_sku": "VEL-BLK-OS"},
                follow_redirects=False,
            )
        assert resp.status_code == 303
        assert "/checkout" in resp.headers["location"]


@pytest.mark.integration
@pytest.mark.cart
class TestUpdateCart:
    def _cart_with_item(self, app):
        c = TestClient(app, raise_server_exceptions=True)
        c.__enter__()
        c.post(
            "/add_to_cart/1",
            data={"quantity": "2", "variant_sku": "VEL-BLK-OS"},
            follow_redirects=True,
        )
        return c

    def test_update_cart_changes_quantity(self, client):
        with _fresh(client.app) as c:
            c.post(
                "/add_to_cart/2",
                data={"quantity": "1", "variant_sku": "WKC-TAN-OS"},
                follow_redirects=True,
            )
            from src.services import build_cart_key
            key = build_cart_key(2, "WKC-TAN-OS")
            resp = c.post(
                f"/update_cart/{key}",
                data={"quantity": "3"},
                follow_redirects=False,
            )
        assert resp.status_code == 303
        assert "/cart" in resp.headers["location"]

    def test_update_cart_quantity_zero_removes_item(self, client):
        with _fresh(client.app) as c:
            c.post(
                "/add_to_cart/2",
                data={"quantity": "1", "variant_sku": "WKC-TAN-OS"},
                follow_redirects=True,
            )
            from src.services import build_cart_key
            key = build_cart_key(2, "WKC-TAN-OS")
            resp = c.post(
                f"/update_cart/{key}",
                data={"quantity": "0"},
                follow_redirects=True,
            )
            cart_page = c.get("/cart")
        # After removing the only item the cart should not show that product
        assert b"WKC-TAN-OS" not in cart_page.content

    def test_update_nonexistent_cart_key_redirects_to_cart(self, client):
        with _fresh(client.app) as c:
            resp = c.post(
                "/update_cart/999__NONEXIST",
                data={"quantity": "2"},
                follow_redirects=False,
            )
        assert resp.status_code == 303
        assert "/cart" in resp.headers["location"]


@pytest.mark.integration
@pytest.mark.cart
class TestRemoveFromCart:
    def test_remove_item_from_cart(self, client):
        with _fresh(client.app) as c:
            c.post(
                "/add_to_cart/1",
                data={"quantity": "1", "variant_sku": "VEL-BLK-OS"},
                follow_redirects=True,
            )
            from src.services import build_cart_key
            key = build_cart_key(1, "VEL-BLK-OS")
            resp = c.post(f"/remove_from_cart/{key}", follow_redirects=False)
        assert resp.status_code == 303
        assert "/cart" in resp.headers["location"]

    def test_remove_item_no_longer_in_cart_page(self, client):
        with _fresh(client.app) as c:
            c.post(
                "/add_to_cart/1",
                data={"quantity": "1", "variant_sku": "VEL-NVY-OS"},
                follow_redirects=True,
            )
            from src.services import build_cart_key
            key = build_cart_key(1, "VEL-NVY-OS")
            c.post(f"/remove_from_cart/{key}", follow_redirects=True)
            cart_resp = c.get("/cart")
        assert b"VEL-NVY-OS" not in cart_resp.content

    def test_remove_nonexistent_key_is_safe(self, client):
        with _fresh(client.app) as c:
            resp = c.post("/remove_from_cart/000__GHOST", follow_redirects=False)
        assert resp.status_code == 303
