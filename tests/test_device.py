"""Unit tests for the Device model."""
import pytest
from datetime import datetime, timedelta

from src.models.device import Device, DeviceValidationError


class TestDeviceModel:
    """Tests for the Device dataclass."""
    
    def test_device_creation_valid(self):
        """Test creating a valid device."""
        now = datetime.now()
        device = Device(
            id="DEV001",
            name="3D Printer",
            responsible_person_id="U001",
            end_of_life=now + timedelta(days=365),
            first_maintenance=now + timedelta(days=30),
            next_maintenance=now + timedelta(days=30),
            maintenance_interval=90,
            maintenance_cost=150.0
        )
        assert device.id == "DEV001"
        assert device.name == "3D Printer"
        assert device.status == "active"
    
    def test_device_creation_with_all_fields(self):
        """Test creating a device with all fields."""
        now = datetime.now()
        device = Device(
            id="DEV001",
            name="3D Printer",
            responsible_person_id="U001",
            end_of_life=now + timedelta(days=365),
            first_maintenance=now + timedelta(days=30),
            next_maintenance=now + timedelta(days=30),
            maintenance_interval=90,
            maintenance_cost=150.0,
            description="High-quality 3D printer",
            location="Lab A",
            status="active",
            tags=["3d", "printing"]
        )
        assert device.description == "High-quality 3D printer"
        assert device.location == "Lab A"
        assert device.tags == ["3d", "printing"]
    
    def test_device_invalid_empty_id(self):
        """Test that empty id raises validation error."""
        now = datetime.now()
        with pytest.raises(DeviceValidationError, match="Device ID cannot be empty"):
            Device(
                id="",
                name="Test",
                responsible_person_id="U001",
                end_of_life=now + timedelta(days=365),
                first_maintenance=now + timedelta(days=30),
                next_maintenance=now + timedelta(days=30),
                maintenance_interval=90,
                maintenance_cost=150.0
            )
    
    def test_device_invalid_maintenance_interval(self):
        """Test that invalid maintenance interval raises error."""
        now = datetime.now()
        with pytest.raises(DeviceValidationError, match="Maintenance interval must be at least 1 day"):
            Device(
                id="DEV001",
                name="Test",
                responsible_person_id="U001",
                end_of_life=now + timedelta(days=365),
                first_maintenance=now + timedelta(days=30),
                next_maintenance=now + timedelta(days=30),
                maintenance_interval=0,
                maintenance_cost=150.0
            )
    
    def test_device_invalid_negative_cost(self):
        """Test that negative cost raises error."""
        now = datetime.now()
        with pytest.raises(DeviceValidationError, match="Maintenance cost cannot be negative"):
            Device(
                id="DEV001",
                name="Test",
                responsible_person_id="U001",
                end_of_life=now + timedelta(days=365),
                first_maintenance=now + timedelta(days=30),
                next_maintenance=now + timedelta(days=30),
                maintenance_interval=90,
                maintenance_cost=-50.0
            )
    
    def test_device_invalid_status(self):
        """Test that invalid status raises error."""
        now = datetime.now()
        with pytest.raises(DeviceValidationError, match="Invalid status"):
            Device(
                id="DEV001",
                name="Test",
                responsible_person_id="U001",
                end_of_life=now + timedelta(days=365),
                first_maintenance=now + timedelta(days=30),
                next_maintenance=now + timedelta(days=30),
                maintenance_interval=90,
                maintenance_cost=150.0,
                status="unknown"
            )
    
    def test_device_maintenance_overdue(self):
        """Test overdue maintenance detection."""
        now = datetime.now()
        device = Device(
            id="DEV001",
            name="Test",
            responsible_person_id="U001",
            end_of_life=now + timedelta(days=365),
            first_maintenance=now - timedelta(days=10),
            next_maintenance=now - timedelta(days=10),
            maintenance_interval=90,
            maintenance_cost=150.0
        )
        assert device.is_overdue_maintenance is True
        assert device.maintenance_status == "overdue"
    
    def test_device_maintenance_upcoming(self):
        """Test upcoming maintenance detection."""
        now = datetime.now()
        device = Device(
            id="DEV001",
            name="Test",
            responsible_person_id="U001",
            end_of_life=now + timedelta(days=365),
            first_maintenance=now + timedelta(days=5),
            next_maintenance=now + timedelta(days=5),
            maintenance_interval=90,
            maintenance_cost=150.0
        )
        assert device.is_overdue_maintenance is False
        assert device.maintenance_status == "upcoming"
    
    def test_device_maintenance_ok(self):
        """Test ok maintenance status."""
        now = datetime.now()
        device = Device(
            id="DEV001",
            name="Test",
            responsible_person_id="U001",
            end_of_life=now + timedelta(days=365),
            first_maintenance=now + timedelta(days=30),
            next_maintenance=now + timedelta(days=30),
            maintenance_interval=90,
            maintenance_cost=150.0
        )
        assert device.maintenance_status == "ok"
    
    def test_device_days_until_maintenance(self):
        """Test days until maintenance calculation."""
        now = datetime.now()
        device = Device(
            id="DEV001",
            name="Test",
            responsible_person_id="U001",
            end_of_life=now + timedelta(days=365),
            first_maintenance=now + timedelta(days=30),
            next_maintenance=now + timedelta(days=30),
            maintenance_interval=90,
            maintenance_cost=150.0
        )
        # Allow for 1 day tolerance due to time differences
        assert 29 <= device.days_until_maintenance <= 30
    
    def test_device_end_of_life(self):
        """Test end of life detection."""
        now = datetime.now()
        device = Device(
            id="DEV001",
            name="Test",
            responsible_person_id="U001",
            end_of_life=now - timedelta(days=10),
            first_maintenance=now + timedelta(days=30),
            next_maintenance=now + timedelta(days=30),
            maintenance_interval=90,
            maintenance_cost=150.0
        )
        assert device.is_end_of_life is True
    
    def test_device_schedule_next_maintenance(self):
        """Test scheduling next maintenance."""
        now = datetime.now()
        device = Device(
            id="DEV001",
            name="Test",
            responsible_person_id="U001",
            end_of_life=now + timedelta(days=365),
            first_maintenance=now - timedelta(days=30),
            next_maintenance=now - timedelta(days=30),
            maintenance_interval=90,
            maintenance_cost=150.0
        )
        old_maintenance = device.next_maintenance
        device.schedule_next_maintenance()
        assert device.next_maintenance > old_maintenance
    
    def test_device_to_dict(self):
        """Test converting device to dictionary."""
        now = datetime.now()
        device = Device(
            id="DEV001",
            name="3D Printer",
            responsible_person_id="U001",
            end_of_life=now + timedelta(days=365),
            first_maintenance=now + timedelta(days=30),
            next_maintenance=now + timedelta(days=30),
            maintenance_interval=90,
            maintenance_cost=150.0,
            location="Lab A"
        )
        data = device.to_dict()
        
        assert data["id"] == "DEV001"
        assert data["name"] == "3D Printer"
        assert data["location"] == "Lab A"
        assert "created_at" in data
    
    def test_device_from_dict(self):
        """Test creating device from dictionary."""
        now = datetime.now()
        data = {
            "id": "DEV001",
            "name": "3D Printer",
            "responsible_person_id": "U001",
            "end_of_life": (now + timedelta(days=365)).isoformat(),
            "first_maintenance": (now + timedelta(days=30)).isoformat(),
            "next_maintenance": (now + timedelta(days=30)).isoformat(),
            "maintenance_interval": 90,
            "maintenance_cost": 150.0,
            "description": "Test printer",
            "location": "Lab A",
            "status": "active",
            "tags": ["3d"],
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }
        device = Device.from_dict(data)
        
        assert device.id == "DEV001"
        assert device.location == "Lab A"
    
    def test_device_from_dict_minimal(self):
        """Test creating device from minimal dictionary (backward compatibility)."""
        now = datetime.now()
        data = {
            "id": "DEV001",
            "name": "3D Printer",
            "responsible_person_id": "U001",
            "end_of_life": (now + timedelta(days=365)).isoformat(),
            "first_maintenance": (now + timedelta(days=30)).isoformat(),
            "next_maintenance": (now + timedelta(days=30)).isoformat(),
            "maintenance_interval": 90,
            "maintenance_cost": 150.0
        }
        device = Device.from_dict(data)
        
        assert device.description == ""
        assert device.status == "active"
    
    def test_device_update(self):
        """Test updating device fields."""
        now = datetime.now()
        device = Device(
            id="DEV001",
            name="3D Printer",
            responsible_person_id="U001",
            end_of_life=now + timedelta(days=365),
            first_maintenance=now + timedelta(days=30),
            next_maintenance=now + timedelta(days=30),
            maintenance_interval=90,
            maintenance_cost=150.0
        )
        original_updated = device.updated_at
        
        device.update(name="Updated Printer", location="Lab B")
        
        assert device.name == "Updated Printer"
        assert device.location == "Lab B"
        assert device.updated_at > original_updated
    
    def test_device_str_repr(self):
        """Test string representation."""
        now = datetime.now()
        device = Device(
            id="DEV001",
            name="3D Printer",
            responsible_person_id="U001",
            end_of_life=now + timedelta(days=365),
            first_maintenance=now + timedelta(days=30),
            next_maintenance=now + timedelta(days=30),
            maintenance_interval=90,
            maintenance_cost=150.0
        )
        assert str(device) == "Device(DEV001: 3D Printer)"
