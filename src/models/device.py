from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List


class DeviceValidationError(Exception):
    """Custom exception for device validation errors."""
    pass


@dataclass
class Device:
    """Represents a physical device (e.g. 3D Printer) with maintenance tracking."""
    id: str
    name: str
    responsible_person_id: str
    end_of_life: datetime
    first_maintenance: datetime
    next_maintenance: datetime
    maintenance_interval: int
    maintenance_cost: float
    description: str = ""
    location: str = ""
    status: str = "active"  # active, maintenance, retired
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate device data after initialization."""
        self.validate()

    def validate(self) -> None:
        """Validate all device fields."""
        errors = []
        
        if not self.id or not self.id.strip():
            errors.append("Device ID cannot be empty")
        
        if not self.name or not self.name.strip():
            errors.append("Device name cannot be empty")
        
        if not self.responsible_person_id or not self.responsible_person_id.strip():
            errors.append("Responsible person ID cannot be empty")
        
        if self.maintenance_interval < 1:
            errors.append("Maintenance interval must be at least 1 day")
        
        if self.maintenance_cost < 0:
            errors.append("Maintenance cost cannot be negative")
        
        if self.status not in ["active", "maintenance", "retired"]:
            errors.append(f"Invalid status: {self.status}")
        
        if errors:
            raise DeviceValidationError("; ".join(errors))

    @property
    def is_overdue_maintenance(self) -> bool:
        """Check if maintenance is overdue."""
        return self.next_maintenance < datetime.now()

    @property
    def days_until_maintenance(self) -> int:
        """Calculate days until next maintenance."""
        delta = self.next_maintenance - datetime.now()
        return delta.days

    @property
    def is_end_of_life(self) -> bool:
        """Check if device has reached end of life."""
        return self.end_of_life < datetime.now()

    @property
    def days_until_eol(self) -> int:
        """Calculate days until end of life."""
        delta = self.end_of_life - datetime.now()
        return delta.days

    @property
    def maintenance_status(self) -> str:
        """Get maintenance status description."""
        if self.is_overdue_maintenance:
            return "overdue"
        elif self.days_until_maintenance <= 7:
            return "upcoming"
        return "ok"

    def schedule_next_maintenance(self) -> None:
        """Schedule the next maintenance based on the interval."""
        from datetime import timedelta
        self.next_maintenance = datetime.now() + timedelta(days=self.maintenance_interval)
        self.updated_at = datetime.now()

    def update(self, **kwargs) -> 'Device':
        """Update device fields with validation."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
        self.validate()
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, serializing datetimes to ISO strings."""
        return {
            "id": self.id,
            "name": self.name,
            "responsible_person_id": self.responsible_person_id,
            "end_of_life": self.end_of_life.isoformat(),
            "first_maintenance": self.first_maintenance.isoformat(),
            "next_maintenance": self.next_maintenance.isoformat(),
            "maintenance_interval": self.maintenance_interval,
            "maintenance_cost": self.maintenance_cost,
            "description": self.description,
            "location": self.location,
            "status": self.status,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Device':
        """Create Device from dictionary, parsing ISO strings back to datetime."""
        return Device(
            id=data["id"],
            name=data["name"],
            responsible_person_id=data["responsible_person_id"],
            end_of_life=datetime.fromisoformat(data["end_of_life"]),
            first_maintenance=datetime.fromisoformat(data["first_maintenance"]),
            next_maintenance=datetime.fromisoformat(data["next_maintenance"]),
            maintenance_interval=data["maintenance_interval"],
            maintenance_cost=data["maintenance_cost"],
            description=data.get("description", ""),
            location=data.get("location", ""),
            status=data.get("status", "active"),
            tags=data.get("tags", []),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now()
        )

    def __str__(self) -> str:
        return f"Device({self.id}: {self.name})"

    def __repr__(self) -> str:
        return self.__str__()