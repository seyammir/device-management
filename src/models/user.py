from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict

from src.core.utils import is_valid_email


class UserValidationError(Exception):
    """Custom exception for user validation errors."""
    pass


@dataclass
class User:
    """Represents a user in the device management system."""
    user_id: str
    name: str
    email: str
    phone: str = ""
    department: str = ""
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate user data after initialization."""
        self.validate()

    def validate(self) -> None:
        """Validate all user fields."""
        errors = []
        
        if not self.user_id or not self.user_id.strip():
            errors.append("User ID cannot be empty")
        
        if not self.name or not self.name.strip():
            errors.append("Name cannot be empty")
        
        if not self.email or not self.email.strip():
            errors.append("Email cannot be empty")
        elif not is_valid_email(self.email):
            errors.append(f"Invalid email format: {self.email}")
        
        if errors:
            raise UserValidationError("; ".join(errors))

    @property
    def display_name(self) -> str:
        """Get formatted display name."""
        return f"{self.name} ({self.user_id})"

    def update(self, **kwargs) -> 'User':
        """Update user fields with validation."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
        self.validate()
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Converts the User object to a dictionary for database storage."""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "department": self.department,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "User":
        """Creates a User object from a dictionary."""
        return User(
            user_id=data["user_id"],
            name=data["name"],
            email=data["email"],
            phone=data.get("phone", ""),
            department=data.get("department", ""),
            is_active=data.get("is_active", True),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now()
        )

    def __str__(self) -> str:
        return f"User({self.user_id}: {self.name})"

    def __repr__(self) -> str:
        return self.__str__()