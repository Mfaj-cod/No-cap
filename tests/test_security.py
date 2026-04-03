"""
Tests for security module (password hashing and verification).
"""
import pytest

from src.security import hash_password, verify_password


class TestPasswordHashing:
    """Tests for password hashing and verification."""

    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string."""
        password = "test_password_123"
        hashed = hash_password(password)
        assert isinstance(hashed, str)
        assert "$" in hashed  # salt and hash separated by $

    def test_hash_password_produces_different_hashes_for_same_password(self):
        """Test that the same password hashes differently (due to different salt)."""
        password = "test_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2  # Different salts

    def test_verify_password_with_correct_password(self):
        """Test that verify_password returns True for correct password."""
        password = "correct_password_123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_with_incorrect_password(self):
        """Test that verify_password returns False for incorrect password."""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = hash_password(password)
        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_with_malformed_hash(self):
        """Test that verify_password handles malformed hashes gracefully."""
        assert verify_password("password", "malformed_hash") is False
        assert verify_password("password", "") is False

    def test_verify_password_is_case_sensitive(self):
        """Test that password verification is case-sensitive."""
        password = "MyPassword123"
        hashed = hash_password(password)
        assert verify_password("mypassword123", hashed) is False
        assert verify_password("MYPASSWORD123", hashed) is False
        assert verify_password("MyPassword123", hashed) is True

    def test_hash_password_with_special_characters(self):
        """Test hashing passwords with special characters."""
        password = "p@$$w0rd!#%&*()_+-=[]{}|;:,.<>?"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_hash_password_with_unicode_characters(self):
        """Test hashing passwords with unicode characters."""
        password = "पासवर्ड🔐🔒"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
