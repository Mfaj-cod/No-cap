"""
Integration tests for order / checkout routes:
  GET  /checkout
  POST /checkout   (COD path; Razorpay is not configured in CI)
  GET  /success
  GET  /failure
  POST /success    (payment-verification logic)

All tests run without Razorpay keys – online payments fall back to COD
or return the expected error message.
"""

import pytest
from starlette.testclient import TestClient


def _fresh(app):
    return TestClient(app, raise_server_exceptions=True)


def _cart_loaded(app, product_id=1, sku="VEL-BLK-OS", qty=1):
    """Return a TestClient that already has one product in the cart."""
    c = TestClient(app, raise_server_exceptions=True)
    c.__enter__()
    c.post(
        f"/add_to_cart/{product_id}",
        data={"quantity": str(qty), "variant_sku": sku},
        follow_redirects=True,
    )
    return c


_CHECKOUT_DATA = {
    "name": "Test Buyer",
    "email": "buyer@example.com",
    "phone": "9876543210",
    "address": "123 Test Street",
    "city": "Mumbai",
    "state": "Maharashtra",
    "pincode": "400001",
    "payment_method": "cod",
}


@pytest.mark.integration
class TestCheckoutPage:
    def test_checkout_with_empty_cart_redirects_to_cart(self, client):
        with _fresh(client.app) as c:
            resp = c.get("/checkout", follow_redirects=False)
        assert resp.status_code == 303
        assert "/cart" in resp.headers["location"]

    def test_checkout_with_item_in_cart_loads(self, client):
        with _cart_loaded(client.app) as c:
            resp = c.get("/checkout")
        assert resp.status_code == 200

    def test_checkout_page_contains_form_fields(self, client):
        with _cart_loaded(client.app) as c:
            resp = c.get("/checkout")
        content = resp.content.lower()
        for field in (b"name", b"email", b"phone", b"address"):
            assert field in content


@pytest.mark.integration
class TestPlaceOrder:
    def test_cod_order_redirects_to_success(self, client):
        with _cart_loaded(client.app) as c:
            resp = c.post(
                "/checkout",
                data=_CHECKOUT_DATA,
                follow_redirects=False,
            )
        assert resp.status_code == 303
        assert "/success" in resp.headers["location"]

    def test_cod_order_clears_cart(self, client):
        with _cart_loaded(client.app) as c:
            c.post("/checkout", data=_CHECKOUT_DATA, follow_redirects=True)
            cart_resp = c.get("/cart")
        # Cart page should show empty cart after order
        assert b"Velocity Sports Cap" not in cart_resp.content

    def test_invalid_payment_method_redirects_back(self, client):
        with _cart_loaded(client.app) as c:
            data = {**_CHECKOUT_DATA, "payment_method": "bitcoin"}
            resp = c.post("/checkout", data=data, follow_redirects=False)
        assert resp.status_code == 303
        assert "/checkout" in resp.headers["location"]

    def test_empty_cart_post_redirects_to_cart(self, client):
        with _fresh(client.app) as c:
            resp = c.post("/checkout", data=_CHECKOUT_DATA, follow_redirects=False)
        assert resp.status_code == 303
        assert "/cart" in resp.headers["location"]

    def test_online_payment_method_handled_gracefully(self, client):
        """
        Choosing 'upi' should either:
          - redirect (303) back/to success when Razorpay is absent/configured, OR
          - render the payment page inline (200) when Razorpay IS configured.
        Either outcome is acceptable for CI; we just verify it doesn't crash (500).
        """
        with _cart_loaded(client.app) as c:
            data = {**_CHECKOUT_DATA, "payment_method": "upi"}
            resp = c.post("/checkout", data=data, follow_redirects=False)
        assert resp.status_code in (200, 303)

    def test_multiple_items_in_cart_produce_order(self, client):
        with _fresh(client.app) as c:
            c.post("/add_to_cart/1", data={"quantity": "1", "variant_sku": "VEL-BLK-OS"}, follow_redirects=True)
            c.post("/add_to_cart/2", data={"quantity": "1", "variant_sku": "WKC-TAN-OS"}, follow_redirects=True)
            resp = c.post("/checkout", data=_CHECKOUT_DATA, follow_redirects=False)
        assert resp.status_code == 303
        assert "/success" in resp.headers["location"]


@pytest.mark.integration
class TestSuccessPage:
    def _place_cod_order(self, app):
        """Place a COD order and return (client, order_id)."""
        c = _cart_loaded(app)
        resp = c.post("/checkout", data=_CHECKOUT_DATA, follow_redirects=False)
        location = resp.headers["location"]
        order_id = int(location.split("order_id=")[1])
        return c, order_id

    def test_success_page_loads_for_own_order(self, client):
        c, order_id = self._place_cod_order(client.app)
        resp = c.get(f"/success?order_id={order_id}")
        assert resp.status_code == 200

    def test_success_page_unknown_order_id_redirects(self, client):
        with _fresh(client.app) as c:
            resp = c.get("/success?order_id=999999", follow_redirects=False)
        assert resp.status_code == 303

    def test_success_page_other_user_blocked(self, client):
        """A fresh session (different 'user') should not see another guest's order."""
        c, order_id = self._place_cod_order(client.app)

        with _fresh(client.app) as fresh_c:
            resp = fresh_c.get(f"/success?order_id={order_id}", follow_redirects=False)
        assert resp.status_code == 303


@pytest.mark.integration
class TestFailurePage:
    def test_failure_page_loads_without_order_id(self, client):
        with _fresh(client.app) as c:
            resp = c.get("/failure")
        assert resp.status_code == 200

    def test_failure_page_loads_with_unknown_order_id(self, client):
        with _fresh(client.app) as c:
            resp = c.get("/failure?order_id=999999")
        assert resp.status_code == 200

    def test_upi_checkout_does_not_crash(self, client):
        """
        Posting with payment_method=upi should not return a 5xx regardless
        of whether Razorpay is configured or not.
        """
        with _cart_loaded(client.app) as c:
            resp = c.post(
                "/checkout",
                data={**_CHECKOUT_DATA, "payment_method": "upi"},
                follow_redirects=False,
            )
        # 200 (Razorpay widget rendered inline) or 303 (redirect) – never 500
        assert resp.status_code in (200, 303)
