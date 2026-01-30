from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Any
import uuid


class ReservationValidationError(Exception):
    """Custom exception for reservation validation errors."""
    pass


@dataclass
class Reservation:
    """Represents a time-slot reservation for a specific device."""
    id: str
    device_id: str
    user_id: str
    start_time: datetime
    end_time: datetime
    purpose: str = ""
    notes: str = ""
    status: str = "confirmed"  # pending, confirmed, cancelled, completed
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate reservation data after initialization."""
        self.validate()

    def validate(self) -> None:
        """Validate all reservation fields."""
        errors = []
        
        if not self.id or not self.id.strip():
            errors.append("Reservation ID cannot be empty")
        
        if not self.device_id or not self.device_id.strip():
            errors.append("Device ID cannot be empty")
        
        if not self.user_id or not self.user_id.strip():
            errors.append("User ID cannot be empty")
        
        if self.start_time >= self.end_time:
            errors.append("End time must be after start time")
        
        if self.status not in ["pending", "confirmed", "cancelled", "completed"]:
            errors.append(f"Invalid status: {self.status}")
        
        if errors:
            raise ReservationValidationError("; ".join(errors))

    @property
    def duration(self) -> timedelta:
        """Calculate reservation duration."""
        return self.end_time - self.start_time

    @property
    def duration_hours(self) -> float:
        """Get duration in hours."""
        return self.duration.total_seconds() / 3600

    @property
    def is_active(self) -> bool:
        """Check if reservation is currently active."""
        now = datetime.now()
        return self.start_time <= now <= self.end_time and self.status == "confirmed"

    @property
    def is_upcoming(self) -> bool:
        """Check if reservation is in the future."""
        return self.start_time > datetime.now() and self.status in ["pending", "confirmed"]

    @property
    def is_past(self) -> bool:
        """Check if reservation is in the past."""
        return self.end_time < datetime.now()

    def conflicts_with(self, other: 'Reservation') -> bool:
        """Check if this reservation conflicts with another."""
        if self.device_id != other.device_id:
            return False
        if self.id == other.id:
            return False
        return self.start_time < other.end_time and self.end_time > other.start_time

    def cancel(self) -> None:
        """Cancel the reservation."""
        self.status = "cancelled"
        self.updated_at = datetime.now()

    def confirm(self) -> None:
        """Confirm the reservation."""
        self.status = "confirmed"
        self.updated_at = datetime.now()

    def complete(self) -> None:
        """Mark reservation as completed."""
        self.status = "completed"
        self.updated_at = datetime.now()

    def update(self, **kwargs) -> 'Reservation':
        """Update reservation fields with validation."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
        self.validate()
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "device_id": self.device_id,
            "user_id": self.user_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "purpose": self.purpose,
            "notes": self.notes,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Reservation':
        """Create Reservation from dictionary."""
        return Reservation(
            id=data["id"],
            device_id=data["device_id"],
            user_id=data["user_id"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]),
            purpose=data.get("purpose", ""),
            notes=data.get("notes", ""),
            status=data.get("status", "confirmed"),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now()
        )

    @staticmethod
    def create_new(
        device_id: str, 
        user_id: str, 
        start: datetime, 
        end: datetime,
        purpose: str = "",
        notes: str = "",
        status: str = "confirmed"
    ) -> 'Reservation':
        """Factory method to create a new reservation with a unique UUID."""
        return Reservation(
            id=str(uuid.uuid4()),
            device_id=device_id,
            user_id=user_id,
            start_time=start,
            end_time=end,
            purpose=purpose,
            notes=notes,
            status=status
        )

    def __str__(self) -> str:
        return f"Reservation({self.id[:8]}: {self.device_id} from {self.start_time} to {self.end_time})"

    def __repr__(self) -> str:
        return self.__str__()