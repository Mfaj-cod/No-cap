"""
Unit tests for cart helper functions in src/services.py.

These tests exercise pure-logic functions only; no HTTP round-trips needed.
"""

import pytest
from src.services import (
    CART_KEY_SEPARATOR,
    build_cart_key,
    parse_cart_key,
)


@pytest.mark.unit
@pytest.mark.cart
class TestCartKeyHelpers:
    # build_cart_key

    def test_build_cart_key_with_sku(self):
        key = build_cart_key(42, "VEL-BLK-OS")
        assert key == f"42{CART_KEY_SEPARATOR}VEL-BLK-OS"

    def test_build_cart_key_none_sku_uses_default(self):
        key = build_cart_key(7, None)
        assert key == f"7{CART_KEY_SEPARATOR}default"

    def test_build_cart_key_empty_sku_uses_default(self):
        key = build_cart_key(3, "")
        # empty string is falsy, should become 'default'
        assert key.endswith("default")

    # parse_cart_key

    def test_parse_key_with_sku(self):
        key = f"5{CART_KEY_SEPARATOR}VEL-BLK-OS"
        product_id, sku = parse_cart_key(key)
        assert product_id == 5
        assert sku == "VEL-BLK-OS"

    def test_parse_key_default_sku_returns_none(self):
        key = f"9{CART_KEY_SEPARATOR}default"
        product_id, sku = parse_cart_key(key)
        assert product_id == 9
        assert sku is None

    def test_parse_key_without_separator(self):
        """Graceful fallback when no separator present."""
        product_id, sku = parse_cart_key("12")
        assert product_id == 12
        assert sku is None

    def test_build_then_parse_roundtrip(self):
        original_id, original_sku = 99, "WKC-TAN-OS"
        key = build_cart_key(original_id, original_sku)
        parsed_id, parsed_sku = parse_cart_key(key)
        assert parsed_id == original_id
        assert parsed_sku == original_sku

    def test_build_then_parse_roundtrip_no_sku(self):
        key = build_cart_key(1, None)
        product_id, sku = parse_cart_key(key)
        assert product_id == 1
        assert sku is None


@pytest.mark.unit
@pytest.mark.cart
class TestFlashMessages:
    """Flash messages are stored in / read from the session dict."""

    def _make_request(self, session_data=None):
        """Minimal fake request object for services that only need .session."""
        class FakeRequest:
            session = session_data or {}
        return FakeRequest()

    def test_add_flash_stores_message(self):
        from src.services import add_flash
        req = self._make_request()
        add_flash(req, "Hello!", "success")
        assert req.session["_flash_messages"] == [
            {"category": "success", "message": "Hello!"}
        ]

    def test_add_flash_defaults_to_info(self):
        from src.services import add_flash
        req = self._make_request()
        add_flash(req, "Note")
        assert req.session["_flash_messages"][0]["category"] == "info"

    def test_pop_flash_empties_messages(self):
        from src.services import add_flash, pop_flash_messages
        req = self._make_request()
        add_flash(req, "msg1")
        add_flash(req, "msg2")
        msgs = pop_flash_messages(req)
        assert len(msgs) == 2
        # After popping, list is empty
        assert req.session["_flash_messages"] == []

    def test_pop_flash_returns_empty_list_when_none(self):
        from src.services import pop_flash_messages
        req = self._make_request()
        assert pop_flash_messages(req) == []


@pytest.mark.unit
@pytest.mark.cart
class TestCartSessionHelpers:
    def _make_request(self, session_data=None):
        class FakeRequest:
            session = dict(session_data or {})
        return FakeRequest()

    def test_get_cart_returns_empty_dict_when_no_cart(self):
        from src.services import get_cart
        req = self._make_request()
        assert get_cart(req) == {}

    def test_save_and_get_cart(self):
        from src.services import get_cart, save_cart
        req = self._make_request()
        save_cart(req, {"1__VEL-BLK-OS": 3})
        assert get_cart(req) == {"1__VEL-BLK-OS": 3}

    def test_clear_cart(self):
        from src.services import clear_cart, get_cart, save_cart
        req = self._make_request()
        save_cart(req, {"1__VEL-BLK-OS": 2})
        clear_cart(req)
        assert get_cart(req) == {}

    def test_cart_item_count_sums_quantities(self):
        from src.services import cart_item_count, save_cart
        req = self._make_request()
        save_cart(req, {"1__A": 3, "2__B": 5})
        assert cart_item_count(req) == 8

    def test_cart_item_count_empty_cart(self):
        from src.services import cart_item_count
        req = self._make_request()
        assert cart_item_count(req) == 0
