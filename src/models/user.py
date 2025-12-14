class User:
    """
    Represents a user of the system (e.g., student, professor, admin).
    """
    def __init__(self, user_id: str, name: str, email: str) -> None:
        self.user_id = user_id  # Unique identifier (e.g., matriculation number or employee ID)
        self.name = name
        self.email = email

    def __str__(self) -> str:
        return f"{self.name} (ID: {self.user_id})"

    def to_dict(self) -> dict: 
        """
        Converts the user object to a dictionary for database storage.
        """
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email
        }

    @staticmethod
    def from_dict(data) -> "User":
        """
        Creates a User object from a dictionary (e.g., loaded from database).
        """
        return User(
            user_id=data["user_id"],
            name=data["name"],
            email=data["email"]
        )