from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class User:
    user_id: str
    name: str
    email: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the User object to a dictionary (e.g., for database storage).
        """
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "User":
        """
        Creates a User object from a dictionary (e.g., loaded from database).
        """
        return User(
            user_id=data["user_id"],
            name=data["name"],
            email=data["email"]
        )