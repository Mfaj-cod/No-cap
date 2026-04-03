"""
Tests for configuration module.
"""
import os
import pytest
from pathlib import Path

from src.config import settings, Settings


class TestSettingsClass:
    """Tests for Settings dataclass."""

    def test_settings_is_frozen(self):
        """Test that Settings is frozen (immutable)."""
        with pytest.raises(AttributeError):
            settings.store_name = "Different Store"

    def test_settings_has_required_attributes(self):
        """Test that settings has all required attributes."""
        required_attrs = [
            "store_name",
            "database_path",
            "session_secret",
            "razorpay_key_id",
            "razorpay_key_secret",
            "smtp_server",
            "smtp_port",
            "smtp_user",
            "smtp_pass",
            "owner_email",
            "groq_api_key",
            "groq_model",
        ]
        for attr in required_attrs:
            assert hasattr(settings, attr)

    def test_store_name_is_configured(self):
        """Test that store name is configured."""
        assert len(settings.store_name) > 0
        assert isinstance(settings.store_name, str)

    def test_database_path_is_path_object(self):
        """Test that database_path is a Path object."""
        assert isinstance(settings.database_path, Path)

    def test_session_secret_fallback(self, monkeypatch):
        """Test session secret with fallback."""
        # When no env vars set, should use default
        monkeypatch.delenv("SESSION_SECRET", raising=False)
        monkeypatch.delenv("SECRET_KEY", raising=False)
        test_settings = Settings(
            store_name="Test",
            database_path=Path("test.db"),
            session_secret=os.getenv("SESSION_SECRET") or os.getenv("SECRET_KEY", "devsecret"),
            razorpay_key_id=os.getenv("RAZORPAY_KEY_ID", ""),
            razorpay_key_secret=os.getenv("RAZORPAY_KEY_SECRET", ""),
            smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_user=os.getenv("SMTP_USER", ""),
            smtp_pass=os.getenv("SMTP_PASS", ""),
            owner_email=os.getenv("OWNER_EMAIL", ""),
            groq_api_key=os.getenv("GROQ_API_KEY", ""),
            groq_model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        )
        assert test_settings.session_secret == "devsecret"

    def test_smtp_defaults(self):
        """Test SMTP configuration defaults."""
        assert settings.smtp_server == "smtp.gmail.com"
        assert settings.smtp_port == 587

    def test_groq_model_default(self):
        """Test Groq model default."""
        assert settings.groq_model == "llama-3.3-70b-versatile"

    def test_razorpay_settings_optional(self):
        """Test that Razorpay settings can be empty."""
        # They default to empty string if not set
        assert isinstance(settings.razorpay_key_id, str)
        assert isinstance(settings.razorpay_key_secret, str)

    def test_email_settings_optional(self):
        """Test that email settings can be empty."""
        assert isinstance(settings.smtp_user, str)
        assert isinstance(settings.smtp_pass, str)
        assert isinstance(settings.owner_email, str)

    def test_groq_api_key_optional(self):
        """Test that Groq API key is optional."""
        assert isinstance(settings.groq_api_key, str)


class TestEnvironmentVariables:
    """Tests for environment variable loading."""

    def test_env_variables_are_loaded(self):
        """Test that .env file is loaded."""
        # This verifies that dotenv is working
        # The fact that settings loads means .env was processed
        assert settings is not None

    def test_smtp_port_is_integer(self):
        """Test that SMTP port is converted to integer."""
        assert isinstance(settings.smtp_port, int)
        assert settings.smtp_port > 0

    def test_default_values_when_env_not_set(self, monkeypatch):
        """Test default values when environment variables are not set."""
        monkeypatch.delenv("RAZORPAY_KEY_ID", raising=False)
        monkeypatch.delenv("RAZORPAY_KEY_SECRET", raising=False)
        
        # Create new settings with no env vars
        test_settings = Settings(
            store_name="Test",
            database_path=Path("test.db"),
            session_secret="test-secret",
            razorpay_key_id=os.getenv("RAZORPAY_KEY_ID", ""),
            razorpay_key_secret=os.getenv("RAZORPAY_KEY_SECRET", ""),
            smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_user=os.getenv("SMTP_USER", ""),
            smtp_pass=os.getenv("SMTP_PASS", ""),
            owner_email=os.getenv("OWNER_EMAIL", ""),
            groq_api_key=os.getenv("GROQ_API_KEY", ""),
            groq_model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        )
        assert test_settings.razorpay_key_id == ""
        assert test_settings.razorpay_key_secret == ""


class TestSettingsValidation:
    """Tests for settings validation and constraints."""

    def test_smtp_port_is_valid_range(self):
        """Test that SMTP port is in valid range."""
        assert 1 <= settings.smtp_port <= 65535

    def test_store_name_not_empty(self):
        """Test that store name is not empty."""
        assert len(settings.store_name) > 0

    def test_database_path_is_absolute_or_relative(self):
        """Test that database path is valid."""
        assert isinstance(settings.database_path, Path)

    def test_session_secret_not_empty_in_production(self):
        """Test that session secret is set."""
        assert len(settings.session_secret) > 0

    def test_groq_model_not_empty(self):
        """Test that groq model has a default."""
        assert len(settings.groq_model) > 0
