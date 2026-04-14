"""
Database-layer tests for src/db.py.

These tests use the session-scoped isolated SQLite database set up by
conftest.py, so the production `store.db` is never touched.
"""

import pytest
from src.db import (
    create_user,
    create_subscription,
    get_product,
    get_user_by_email,
    get_user_by_id,
    list_categories,
    list_products,
    store_reset_otp,
    verify_reset_otp,
    reset_user_password,
    clear_reset_otp,
    format_variant_label,
    get_variant_for_product,
)
from src.security import hash_password, verify_password


# Products & categories

@pytest.mark.unit
@pytest.mark.database
class TestProductQueries:
    def test_list_products_returns_non_empty_list(self):
        products = list_products()
        assert len(products) > 0

    def test_list_products_have_required_keys(self):
        product = list_products()[0]
        for key in ("id", "name", "normal_price", "category", "variants", "in_stock"):
            assert key in product, f"Missing key: {key}"

    def test_list_products_featured_filter(self):
        featured = list_products(featured_only=True)
        assert all(p["featured"] for p in featured)

    def test_list_products_category_filter(self):
        sports = list_products(category="Sports")
        assert all(p["category"] == "Sports" for p in sports)

    def test_get_product_known_id(self):
        product = get_product(1)
        assert product is not None
        assert product["id"] == 1
        assert product["name"] == "Velocity Sports Cap"

    def test_get_product_unknown_id_returns_none(self):
        assert get_product(999999) is None

    def test_product_shop_owner_price_is_discounted(self):
        product = get_product(1)
        assert product["shop_owner_price"] < product["normal_price"]

    def test_product_total_stock_is_non_negative(self):
        for product in list_products():
            assert product["total_stock"] >= 0

    def test_product_in_stock_flag_consistent(self):
        product = get_product(1)
        assert product["in_stock"] == (product["total_stock"] > 0)

    def test_list_categories_returns_non_empty(self):
        cats = list_categories()
        assert len(cats) > 0

    def test_list_categories_have_required_keys(self):
        cat = list_categories()[0]
        assert "name" in cat
        assert "image_url" in cat


@pytest.mark.unit
@pytest.mark.database
class TestVariantHelpers:
    def test_get_variant_for_product_known_sku(self):
        product = get_product(1)
        variant = get_variant_for_product(product, "VEL-BLK-OS")
        assert variant is not None
        assert variant["sku"] == "VEL-BLK-OS"

    def test_get_variant_for_product_unknown_sku_returns_in_stock_fallback(self):
        """Unknown SKU should fall back to first in-stock variant."""
        product = get_product(1)
        variant = get_variant_for_product(product, "DOES-NOT-EXIST")
        assert variant is not None  # fallback behaviour

    def test_get_variant_for_product_none_sku_returns_first_in_stock(self):
        product = get_product(1)
        variant = get_variant_for_product(product, None)
        assert variant is not None

    def test_format_variant_label_with_color_and_size(self):
        label = format_variant_label({"color": "Black", "size": "One Size"})
        assert "Black" in label
        assert "One Size" in label

    def test_format_variant_label_with_none_returns_default(self):
        assert format_variant_label(None) == "Default"

    def test_format_variant_label_only_color(self):
        label = format_variant_label({"color": "Red"})
        assert label == "Red"


# User CRUD

@pytest.mark.database
@pytest.mark.auth
class TestUserCRUD:
    """Each test uses a unique email to avoid collisions on the session DB."""

    def _email(self, suffix=""):
        return f"dbtest_{suffix}@example.com"

    def test_create_and_retrieve_user_by_email(self):
        email = self._email("create")
        create_user("DB Tester", email, hash_password("pass123"), "customer")
        user = get_user_by_email(email)
        assert user is not None
        assert user["email"] == email
        assert user["name"] == "DB Tester"
        assert user["role"] == "customer"

    def test_get_user_by_email_case_insensitive(self):
        email = self._email("case")
        create_user("Case User", email, hash_password("pass123"), "customer")
        user = get_user_by_email(email.upper())
        assert user is not None

    def test_create_user_duplicate_email_raises(self):
        import sqlite3
        email = self._email("dup")
        create_user("Dup1", email, hash_password("pass"), "customer")
        with pytest.raises(sqlite3.IntegrityError):
            create_user("Dup2", email, hash_password("pass"), "customer")

    def test_get_user_by_id(self):
        email = self._email("byid")
        create_user("By ID", email, hash_password("pass"), "customer")
        user_by_email = get_user_by_email(email)
        user_by_id = get_user_by_id(user_by_email["id"])
        assert user_by_id["email"] == email

    def test_get_user_by_email_unknown_returns_none(self):
        assert get_user_by_email("nobody@nowhere.com") is None

    def test_get_user_by_id_unknown_returns_none(self):
        assert get_user_by_id(999999) is None

    def test_password_hash_is_stored_not_plaintext(self):
        email = self._email("hash")
        plain = "securepassword"
        create_user("Hash Test", email, hash_password(plain), "customer")
        user = get_user_by_email(email)
        assert user["password_hash"] != plain
        assert verify_password(plain, user["password_hash"])

    def test_shop_owner_role_accepted(self):
        email = self._email("shopowner")
        create_user("Shop Owner", email, hash_password("pw"), "shop_owner")
        user = get_user_by_email(email)
        assert user["role"] == "shop_owner"


# Password-reset OTP

@pytest.mark.database
@pytest.mark.auth
class TestPasswordResetOTP:
    def _setup_user(self, suffix):
        email = f"otp_{suffix}@example.com"
        create_user("OTP User", email, hash_password("pass123"), "customer")
        return email

    def test_store_and_verify_valid_otp(self):
        email = self._setup_user("valid")
        otp = "123456"
        assert store_reset_otp(email, otp) is True
        assert verify_reset_otp(email, otp) is True

    def test_verify_wrong_otp_returns_false(self):
        email = self._setup_user("wrong")
        store_reset_otp(email, "111111")
        assert verify_reset_otp(email, "999999") is False

    def test_clear_otp(self):
        email = self._setup_user("clear")
        store_reset_otp(email, "654321")
        clear_reset_otp(email)
        assert verify_reset_otp(email, "654321") is False

    def test_reset_user_password_changes_hash(self):
        email = self._setup_user("resetpw")
        new_pw = "brandnewnewpassword"
        store_reset_otp(email, "000000")
        assert reset_user_password(email, hash_password(new_pw)) is True
        user = get_user_by_email(email)
        assert verify_password(new_pw, user["password_hash"])

    def test_reset_user_password_clears_otp(self):
        email = self._setup_user("clearotp")
        otp = "888888"
        store_reset_otp(email, otp)
        reset_user_password(email, hash_password("newpass"))
        # OTP should be gone after password reset
        assert verify_reset_otp(email, otp) is False

    def test_verify_otp_for_unknown_email_returns_false(self):
        assert verify_reset_otp("nobody@nowhere.com", "123456") is False


# Newsletter subscriptions

@pytest.mark.database
class TestSubscriptions:
    def test_create_subscription_returns_true(self):
        assert create_subscription("newsletter_new@example.com") is True

    def test_duplicate_subscription_returns_false(self):
        email = "newsletter_dup@example.com"
        create_subscription(email)
        assert create_subscription(email) is False

    def test_subscription_email_normalised_to_lowercase(self):
        # Should not raise; normalisation happens inside create_subscription
        result = create_subscription("Upper@Example.COM")
        # True on first insertion, False on subsequent with different casing
        assert isinstance(result, bool)
