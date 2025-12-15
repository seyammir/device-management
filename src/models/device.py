from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

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
            "maintenance_cost": self.maintenance_cost
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
            maintenance_cost=data["maintenance_cost"]
        )