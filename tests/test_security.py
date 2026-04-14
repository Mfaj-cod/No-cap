"""
Unit tests for src/security.py – password hashing and verification.
"""

import pytest
from src.security import hash_password, verify_password


@pytest.mark.unit
class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        pw = "mysecretpassword"
        assert hash_password(pw) != pw

    def test_hash_contains_salt_separator(self):
        h = hash_password("test123")
        assert "$" in h, "Expected salt$hash format"

    def test_two_hashes_of_same_password_differ(self):
        """Each call uses a fresh random salt."""
        h1 = hash_password("samepassword")
        h2 = hash_password("samepassword")
        assert h1 != h2

    def test_verify_correct_password_returns_true(self):
        pw = "correcthorse"
        stored = hash_password(pw)
        assert verify_password(pw, stored) is True

    def test_verify_wrong_password_returns_false(self):
        stored = hash_password("rightpassword")
        assert verify_password("wrongpassword", stored) is False

    def test_verify_empty_password_returns_false(self):
        stored = hash_password("nonempty")
        assert verify_password("", stored) is False

    def test_verify_malformed_stored_value_is_safe(self):
        """Should not raise – just return False."""
        assert verify_password("anything", "notahash") is False

    def test_verify_empty_stored_value_is_safe(self):
        assert verify_password("anything", "") is False

    def test_minimum_password_length_hashes_fine(self):
        """The app enforces >=6 at the route level; hashing must work for any length."""
        h = hash_password("ab")
        assert verify_password("ab", h) is True

    def test_unicode_password_roundtrip(self):
        pw = "pässwörд123"
        assert verify_password(pw, hash_password(pw)) is True
