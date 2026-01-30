"""Shared test fixtures and configuration."""
import pytest
import os
import tempfile
from datetime import datetime, timedelta

from src.database.db_manager import DBManager
from src.models.user import User
from src.models.device import Device
from src.models.reservation import Reservation


@pytest.fixture
def temp_db_path():
    """Create a temporary database file for testing."""
    fd, path = tempfile.mkstemp(suffix='.json')
    os.close(fd)
    yield path
    # Cleanup
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def db_manager(temp_db_path):
    """Create a DBManager instance with a temporary database."""
    # Reset singleton for testing
    DBManager._instance = None
    DBManager._db_path = None
    manager = DBManager(db_path=temp_db_path)
    yield manager
    manager.close()
    DBManager._instance = None
    DBManager._db_path = None


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return User(
        user_id="U001",
        name="John Doe",
        email="john.doe@example.com",
        phone="+1234567890",
        department="Engineering"
    )


@pytest.fixture
def sample_users():
    """Create multiple sample users for testing."""
    return [
        User(
            user_id="U001",
            name="John Doe",
            email="john.doe@example.com",
            department="Engineering"
        ),
        User(
            user_id="U002",
            name="Jane Smith",
            email="jane.smith@example.com",
            department="Design"
        ),
        User(
            user_id="U003",
            name="Bob Wilson",
            email="bob.wilson@example.com",
            department="IT"
        )
    ]


@pytest.fixture
def sample_device():
    """Create a sample device for testing."""
    now = datetime.now()
    return Device(
        id="DEV001",
        name="3D Printer MK3S+",
        responsible_person_id="U001",
        end_of_life=now + timedelta(days=1825),  # 5 years
        first_maintenance=now + timedelta(days=30),
        next_maintenance=now + timedelta(days=30),
        maintenance_interval=90,
        maintenance_cost=150.0,
        location="Lab A",
        description="High-quality 3D printer"
    )


@pytest.fixture
def sample_devices():
    """Create multiple sample devices for testing."""
    now = datetime.now()
    return [
        Device(
            id="DEV001",
            name="3D Printer MK3S+",
            responsible_person_id="U001",
            end_of_life=now + timedelta(days=1825),
            first_maintenance=now + timedelta(days=30),
            next_maintenance=now + timedelta(days=30),
            maintenance_interval=90,
            maintenance_cost=150.0,
            location="Lab A"
        ),
        Device(
            id="DEV002",
            name="CNC Machine",
            responsible_person_id="U002",
            end_of_life=now + timedelta(days=365),
            first_maintenance=now - timedelta(days=5),  # Overdue
            next_maintenance=now - timedelta(days=5),
            maintenance_interval=60,
            maintenance_cost=200.0,
            location="Workshop"
        ),
        Device(
            id="DEV003",
            name="Laser Cutter",
            responsible_person_id="U001",
            end_of_life=now + timedelta(days=730),
            first_maintenance=now + timedelta(days=3),  # Upcoming
            next_maintenance=now + timedelta(days=3),
            maintenance_interval=120,
            maintenance_cost=100.0,
            status="maintenance"
        )
    ]


@pytest.fixture
def sample_reservation(sample_device, sample_user):
    """Create a sample reservation for testing."""
    now = datetime.now()
    return Reservation.create_new(
        device_id=sample_device.id,
        user_id=sample_user.user_id,
        start=now + timedelta(hours=1),
        end=now + timedelta(hours=3),
        purpose="Test project",
        notes="Testing reservation"
    )


@pytest.fixture
def sample_reservations():
    """Create multiple sample reservations for testing."""
    now = datetime.now()
    return [
        Reservation.create_new(
            device_id="DEV001",
            user_id="U001",
            start=now + timedelta(hours=1),
            end=now + timedelta(hours=3),
            purpose="Project A"
        ),
        Reservation.create_new(
            device_id="DEV001",
            user_id="U002",
            start=now + timedelta(hours=5),
            end=now + timedelta(hours=7),
            purpose="Project B"
        ),
        Reservation.create_new(
            device_id="DEV002",
            user_id="U001",
            start=now + timedelta(days=1),
            end=now + timedelta(days=1, hours=2),
            purpose="Project C"
        )
    ]
