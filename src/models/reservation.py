from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any
import uuid

@dataclass
class Reservation:
    """Represents a time-slot reservation for a specific device."""
    id: str
    device_id: str
    user_id: str
    start_time: datetime
    end_time: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "device_id": self.device_id,
            "user_id": self.user_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat()
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Reservation':
        """Create Reservation from dictionary."""
        return Reservation(
            id=data["id"],
            device_id=data["device_id"],
            user_id=data["user_id"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"])
        )

    @staticmethod
    def create_new(device_id: str, user_id: str, start: datetime, end: datetime) -> 'Reservation':
        """Factory method to create a new reservation with a unique UUID."""
        return Reservation(
            id=str(uuid.uuid4()),
            device_id=device_id,
            user_id=user_id,
            start_time=start,
            end_time=end
        )