"""Unit tests for the User model."""
import pytest
from datetime import datetime

from src.models.user import User, UserValidationError


class TestUserModel:
    """Tests for the User dataclass."""
    
    def test_user_creation_valid(self):
        """Test creating a valid user."""
        user = User(
            user_id="U001",
            name="John Doe",
            email="john@example.com"
        )
        assert user.user_id == "U001"
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.is_active is True
    
    def test_user_creation_with_all_fields(self):
        """Test creating a user with all fields."""
        user = User(
            user_id="U002",
            name="Jane Smith",
            email="jane@example.com",
            phone="+1234567890",
            department="Engineering",
            is_active=True
        )
        assert user.phone == "+1234567890"
        assert user.department == "Engineering"
    
    def test_user_invalid_empty_id(self):
        """Test that empty user_id raises validation error."""
        with pytest.raises(UserValidationError, match="User ID cannot be empty"):
            User(user_id="", name="Test", email="test@example.com")
    
    def test_user_invalid_empty_name(self):
        """Test that empty name raises validation error."""
        with pytest.raises(UserValidationError, match="Name cannot be empty"):
            User(user_id="U001", name="", email="test@example.com")
    
    def test_user_invalid_email_format(self):
        """Test that invalid email raises validation error."""
        with pytest.raises(UserValidationError, match="Invalid email format"):
            User(user_id="U001", name="Test", email="invalid-email")
    
    def test_user_to_dict(self):
        """Test converting user to dictionary."""
        user = User(
            user_id="U001",
            name="John Doe",
            email="john@example.com",
            department="Engineering"
        )
        data = user.to_dict()
        
        assert data["user_id"] == "U001"
        assert data["name"] == "John Doe"
        assert data["email"] == "john@example.com"
        assert data["department"] == "Engineering"
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_user_from_dict(self):
        """Test creating user from dictionary."""
        data = {
            "user_id": "U001",
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "department": "Engineering",
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        user = User.from_dict(data)
        
        assert user.user_id == "U001"
        assert user.name == "John Doe"
        assert user.phone == "+1234567890"
    
    def test_user_from_dict_minimal(self):
        """Test creating user from minimal dictionary (backward compatibility)."""
        data = {
            "user_id": "U001",
            "name": "John Doe",
            "email": "john@example.com"
        }
        user = User.from_dict(data)
        
        assert user.user_id == "U001"
        assert user.phone == ""
    
    def test_user_update(self):
        """Test updating user fields."""
        user = User(
            user_id="U001",
            name="John Doe",
            email="john@example.com"
        )
        original_updated = user.updated_at
        
        user.update(name="John Smith", department="Sales")
        
        assert user.name == "John Smith"
        assert user.department == "Sales"
        assert user.updated_at > original_updated
    
    def test_user_update_with_validation(self):
        """Test that update validates fields."""
        user = User(
            user_id="U001",
            name="John Doe",
            email="john@example.com"
        )
        
        with pytest.raises(UserValidationError):
            user.update(email="invalid-email")
    
    def test_user_display_name(self):
        """Test display name property."""
        user = User(
            user_id="U001",
            name="John Doe",
            email="john@example.com"
        )
        assert user.display_name == "John Doe (U001)"
    
    def test_user_str_repr(self):
        """Test string representation."""
        user = User(
            user_id="U001",
            name="John Doe",
            email="john@example.com"
        )
        assert str(user) == "User(U001: John Doe)"
        assert repr(user) == "User(U001: John Doe)"
    
    def test_email_validation_various_formats(self):
        """Test various valid email formats."""
        valid_emails = [
            "test@example.com",
            "test.name@example.com",
            "test+label@example.com",
            "test@sub.domain.com"
        ]
        for email in valid_emails:
            user = User(user_id="U001", name="Test", email=email)
            assert user.email == email
