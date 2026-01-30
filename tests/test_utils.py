"""Unit tests for utility functions."""
import pytest
from datetime import datetime

from src.core.utils import (
    format_currency,
    format_date,
    format_datetime,
    is_valid_email,
    get_status_emoji
)


class TestFormatFunctions:
    """Tests for formatting functions."""
    
    def test_format_currency_default(self):
        """Test currency formatting with default symbol."""
        assert format_currency(1234.56) == "€1,234.56"
        assert format_currency(0) == "€0.00"
        assert format_currency(1000000) == "€1,000,000.00"
    
    def test_format_currency_custom_symbol(self):
        """Test currency formatting with custom symbol."""
        assert format_currency(100, "$") == "$100.00"
        assert format_currency(50, "£") == "£50.00"
    
    def test_format_date(self):
        """Test date formatting."""
        dt = datetime(2025, 1, 15, 10, 30)
        assert format_date(dt) == "2025-01-15"
    
    def test_format_datetime(self):
        """Test datetime formatting."""
        dt = datetime(2025, 1, 15, 10, 30)
        assert format_datetime(dt) == "2025-01-15 10:30"


class TestUtilityFunctions:
    """Tests for utility functions."""
    
    def test_is_valid_email(self):
        """Test email validation."""
        assert is_valid_email("test@example.com") is True
        assert is_valid_email("test.name@example.com") is True
        assert is_valid_email("invalid") is False
        assert is_valid_email("@example.com") is False
        assert is_valid_email("test@") is False
    
    def test_get_status_emoji(self):
        """Test status emoji mapping."""
        assert get_status_emoji("active") == "✅"
        assert get_status_emoji("overdue") == "🚨"
        assert get_status_emoji("unknown") == "❓"
