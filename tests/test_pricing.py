"""
Unit tests for wholesale / shop-owner pricing logic in build_cart_summary.

These tests mock the DB queries so no real database rows are needed.
"""

import pytest
from unittest.mock import patch

from src.data import WHOLESALE_DISCOUNT, WHOLESALE_THRESHOLD
from src.services import build_cart_key


# Helpers

def _fake_product(product_id: int, normal_price: float = 100.0):
    return {
        "id": product_id,
        "name": f"Test Cap {product_id}",
        "normal_price": normal_price,
        "shop_owner_price": round(normal_price * (1 - WHOLESALE_DISCOUNT), 2),
        "variants": [
            {"sku": f"TEST-{product_id}-OS", "color": "Black", "size": "One Size", "stock_quantity": 200}
        ],
    }


def _make_request(cart: dict):
    class FakeRequest:
        session = {"cart": cart}
    return FakeRequest()


def _mock_get_product(product_id):
    return _fake_product(product_id)


def _mock_get_variant(product, sku=None):
    return product["variants"][0]


def _mock_format_label(variant):
    return f"{variant['color']} / {variant['size']}"


# Tests

@pytest.mark.unit
@pytest.mark.cart
class TestWholesalePricing:
    """
    Tests that build_cart_summary applies the correct tier depending on
    buyer role and total quantity.
    """

    @patch("src.services.format_variant_label", side_effect=_mock_format_label)
    @patch("src.services.get_variant_for_product", side_effect=_mock_get_variant)
    @patch("src.services.get_product", side_effect=_mock_get_product)
    def test_retail_customer_pays_normal_price(self, mock_gp, mock_gv, mock_fl):
        cart_key = build_cart_key(1, "TEST-1-OS")
        request = _make_request({cart_key: 5})
        user = {"role": "customer"}

        from src.services import build_cart_summary
        summary = build_cart_summary(request, user)

        assert summary["pricing_tier"] == "retail"
        assert summary["wholesale_eligible"] is False
        for item in summary["items"]:
            assert item["applied_unit_price"] == item["retail_unit_price"]

    @patch("src.services.format_variant_label", side_effect=_mock_format_label)
    @patch("src.services.get_variant_for_product", side_effect=_mock_get_variant)
    @patch("src.services.get_product", side_effect=_mock_get_product)
    def test_shop_owner_below_threshold_pays_retail(self, mock_gp, mock_gv, mock_fl):
        qty = WHOLESALE_THRESHOLD - 1  # one below threshold
        cart_key = build_cart_key(1, "TEST-1-OS")
        request = _make_request({cart_key: qty})
        user = {"role": "shop_owner"}

        from src.services import build_cart_summary
        summary = build_cart_summary(request, user)

        assert summary["wholesale_eligible"] is False
        assert summary["pricing_tier"] == "retail"

    @patch("src.services.format_variant_label", side_effect=_mock_format_label)
    @patch("src.services.get_variant_for_product", side_effect=_mock_get_variant)
    @patch("src.services.get_product", side_effect=_mock_get_product)
    def test_shop_owner_at_threshold_gets_wholesale(self, mock_gp, mock_gv, mock_fl):
        qty = WHOLESALE_THRESHOLD  # exactly at threshold
        cart_key = build_cart_key(1, "TEST-1-OS")
        request = _make_request({cart_key: qty})
        user = {"role": "shop_owner"}

        from src.services import build_cart_summary
        summary = build_cart_summary(request, user)

        assert summary["wholesale_eligible"] is True
        assert summary["pricing_tier"] == "shop_owner"
        for item in summary["items"]:
            assert item["applied_unit_price"] == item["wholesale_unit_price"]

    @patch("src.services.format_variant_label", side_effect=_mock_format_label)
    @patch("src.services.get_variant_for_product", side_effect=_mock_get_variant)
    @patch("src.services.get_product", side_effect=_mock_get_product)
    def test_wholesale_discount_is_25_percent(self, mock_gp, mock_gv, mock_fl):
        qty = WHOLESALE_THRESHOLD
        cart_key = build_cart_key(1, "TEST-1-OS")
        request = _make_request({cart_key: qty})
        user = {"role": "shop_owner"}

        from src.services import build_cart_summary
        summary = build_cart_summary(request, user)

        item = summary["items"][0]
        expected = round(item["retail_unit_price"] * (1 - WHOLESALE_DISCOUNT), 2)
        assert abs(item["applied_unit_price"] - expected) < 0.01

    @patch("src.services.format_variant_label", side_effect=_mock_format_label)
    @patch("src.services.get_variant_for_product", side_effect=_mock_get_variant)
    @patch("src.services.get_product", side_effect=_mock_get_product)
    def test_remaining_to_wholesale_calculated_correctly(self, mock_gp, mock_gv, mock_fl):
        qty = 10
        cart_key = build_cart_key(1, "TEST-1-OS")
        request = _make_request({cart_key: qty})
        user = {"role": "shop_owner"}

        from src.services import build_cart_summary
        summary = build_cart_summary(request, user)

        expected_remaining = WHOLESALE_THRESHOLD - qty
        assert summary["remaining_to_wholesale"] == expected_remaining

    @patch("src.services.format_variant_label", side_effect=_mock_format_label)
    @patch("src.services.get_variant_for_product", side_effect=_mock_get_variant)
    @patch("src.services.get_product", side_effect=_mock_get_product)
    def test_final_total_matches_sum_of_line_totals(self, mock_gp, mock_gv, mock_fl):
        cart = {
            build_cart_key(1, "TEST-1-OS"): 3,
        }
        request = _make_request(cart)
        user = {"role": "customer"}

        from src.services import build_cart_summary
        summary = build_cart_summary(request, user)

        expected = sum(item["line_total"] for item in summary["items"])
        assert abs(summary["final_total"] - round(expected, 2)) < 0.01

    @patch("src.services.format_variant_label", side_effect=_mock_format_label)
    @patch("src.services.get_variant_for_product", side_effect=_mock_get_variant)
    @patch("src.services.get_product", side_effect=_mock_get_product)
    def test_guest_treated_as_customer_role(self, mock_gp, mock_gv, mock_fl):
        cart_key = build_cart_key(1, "TEST-1-OS")
        request = _make_request({cart_key: 5})

        from src.services import build_cart_summary
        summary = build_cart_summary(request, user=None)

        assert summary["buyer_role"] == "customer"
        assert summary["pricing_tier"] == "retail"
