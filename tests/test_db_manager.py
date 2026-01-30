"""Unit tests for the DBManager."""
import pytest
from datetime import datetime, timedelta

from src.database.db_manager import DBManager, DatabaseError
from src.models.user import User
from src.models.device import Device
from src.models.reservation import Reservation


class TestDBManagerUsers:
    """Tests for user operations in DBManager."""
    
    def test_add_user(self, db_manager, sample_user):
        """Test adding a new user."""
        result = db_manager.add_user(sample_user)
        assert result.user_id == sample_user.user_id
        
        # Verify user was added
        users = db_manager.get_all_users()
        assert len(users) == 1
        assert users[0].user_id == sample_user.user_id
    
    def test_add_user_update_existing(self, db_manager, sample_user):
        """Test that adding user with same ID updates it."""
        db_manager.add_user(sample_user)
        
        # Update the user
        sample_user.name = "Updated Name"
        db_manager.add_user(sample_user)
        
        users = db_manager.get_all_users()
        assert len(users) == 1
        assert users[0].name == "Updated Name"
    
    def test_get_user(self, db_manager, sample_user):
        """Test getting a single user by ID."""
        db_manager.add_user(sample_user)
        
        user = db_manager.get_user(sample_user.user_id)
        assert user is not None
        assert user.user_id == sample_user.user_id
    
    def test_get_user_not_found(self, db_manager):
        """Test getting non-existent user returns None."""
        user = db_manager.get_user("NONEXISTENT")
        assert user is None
    
    def test_get_all_users(self, db_manager, sample_users):
        """Test getting all users."""
        for user in sample_users:
            db_manager.add_user(user)
        
        users = db_manager.get_all_users()
        assert len(users) == len(sample_users)
    
    def test_get_active_users(self, db_manager, sample_users):
        """Test getting only active users."""
        for user in sample_users:
            db_manager.add_user(user)
        
        # Deactivate one user
        db_manager.update_user(sample_users[0].user_id, is_active=False)
        
        active_users = db_manager.get_active_users()
        assert len(active_users) == len(sample_users) - 1
    
    def test_update_user(self, db_manager, sample_user):
        """Test updating user fields."""
        db_manager.add_user(sample_user)
        
        updated = db_manager.update_user(
            sample_user.user_id,
            name="New Name",
            department="New Department"
        )
        
        assert updated is not None
        assert updated.name == "New Name"
        assert updated.department == "New Department"
    
    def test_update_user_not_found(self, db_manager):
        """Test updating non-existent user returns None."""
        result = db_manager.update_user("NONEXISTENT", name="Test")
        assert result is None
    
    def test_delete_user(self, db_manager, sample_user):
        """Test deleting a user."""
        db_manager.add_user(sample_user)
        
        result = db_manager.delete_user(sample_user.user_id)
        assert result is True
        
        user = db_manager.get_user(sample_user.user_id)
        assert user is None
    
    def test_delete_user_removes_reservations(self, db_manager, sample_user, sample_device):
        """Test that deleting user removes associated reservations."""
        db_manager.add_user(sample_user)
        db_manager.add_device(sample_device)
        
        # Create reservation
        now = datetime.now()
        res = Reservation.create_new(
            device_id=sample_device.id,
            user_id=sample_user.user_id,
            start=now + timedelta(hours=1),
            end=now + timedelta(hours=3)
        )
        db_manager.add_reservation(res)
        
        # Delete user
        db_manager.delete_user(sample_user.user_id)
        
        # Verify reservations were removed
        reservations = db_manager.get_reservations_by_user(sample_user.user_id)
        assert len(reservations) == 0


class TestDBManagerDevices:
    """Tests for device operations in DBManager."""
    
    def test_add_device(self, db_manager, sample_device):
        """Test adding a new device."""
        result = db_manager.add_device(sample_device)
        assert result.id == sample_device.id
        
        devices = db_manager.get_all_devices()
        assert len(devices) == 1
    
    def test_get_device(self, db_manager, sample_device):
        """Test getting a single device by ID."""
        db_manager.add_device(sample_device)
        
        device = db_manager.get_device(sample_device.id)
        assert device is not None
        assert device.id == sample_device.id
    
    def test_get_active_devices(self, db_manager, sample_devices):
        """Test getting only active devices."""
        for device in sample_devices:
            db_manager.add_device(device)
        
        active = db_manager.get_active_devices()
        # Two devices should be active by default
        assert len(active) == 2
    
    def test_get_devices_needing_maintenance(self, db_manager, sample_devices):
        """Test getting devices needing maintenance."""
        for device in sample_devices:
            db_manager.add_device(device)
        
        # One device is overdue, one is upcoming (within 7 days)
        needing_maint = db_manager.get_devices_needing_maintenance()
        assert len(needing_maint) >= 1
    
    def test_update_device(self, db_manager, sample_device):
        """Test updating device fields."""
        db_manager.add_device(sample_device)
        
        updated = db_manager.update_device(
            sample_device.id,
            name="Updated Device",
            location="Lab B"
        )
        
        assert updated is not None
        assert updated.name == "Updated Device"
        assert updated.location == "Lab B"
    
    def test_delete_device(self, db_manager, sample_device):
        """Test deleting a device."""
        db_manager.add_device(sample_device)
        
        result = db_manager.delete_device(sample_device.id)
        assert result is True
        
        device = db_manager.get_device(sample_device.id)
        assert device is None
    
    def test_delete_device_removes_reservations(self, db_manager, sample_user, sample_device):
        """Test that deleting device removes associated reservations."""
        db_manager.add_user(sample_user)
        db_manager.add_device(sample_device)
        
        # Create reservation
        now = datetime.now()
        res = Reservation.create_new(
            device_id=sample_device.id,
            user_id=sample_user.user_id,
            start=now + timedelta(hours=1),
            end=now + timedelta(hours=3)
        )
        db_manager.add_reservation(res)
        
        # Delete device
        db_manager.delete_device(sample_device.id)
        
        # Verify reservations were removed
        reservations = db_manager.get_reservations_by_device(sample_device.id)
        assert len(reservations) == 0


class TestDBManagerReservations:
    """Tests for reservation operations in DBManager."""
    
    def test_add_reservation(self, db_manager, sample_user, sample_device):
        """Test adding a new reservation."""
        db_manager.add_user(sample_user)
        db_manager.add_device(sample_device)
        
        now = datetime.now()
        res = Reservation.create_new(
            device_id=sample_device.id,
            user_id=sample_user.user_id,
            start=now + timedelta(hours=1),
            end=now + timedelta(hours=3)
        )
        result = db_manager.add_reservation(res)
        
        assert result.id == res.id
    
    def test_add_reservation_conflict(self, db_manager, sample_user, sample_device):
        """Test that conflicting reservation raises error."""
        db_manager.add_user(sample_user)
        db_manager.add_device(sample_device)
        
        now = datetime.now()
        res1 = Reservation.create_new(
            device_id=sample_device.id,
            user_id=sample_user.user_id,
            start=now + timedelta(hours=1),
            end=now + timedelta(hours=3)
        )
        db_manager.add_reservation(res1)
        
        # Try to add overlapping reservation
        res2 = Reservation.create_new(
            device_id=sample_device.id,
            user_id=sample_user.user_id,
            start=now + timedelta(hours=2),
            end=now + timedelta(hours=4)
        )
        
        with pytest.raises(DatabaseError, match="not available"):
            db_manager.add_reservation(res2)
    
    def test_get_reservation(self, db_manager, sample_user, sample_device):
        """Test getting a single reservation."""
        db_manager.add_user(sample_user)
        db_manager.add_device(sample_device)
        
        now = datetime.now()
        res = Reservation.create_new(
            device_id=sample_device.id,
            user_id=sample_user.user_id,
            start=now + timedelta(hours=1),
            end=now + timedelta(hours=3)
        )
        db_manager.add_reservation(res)
        
        fetched = db_manager.get_reservation(res.id)
        assert fetched is not None
        assert fetched.id == res.id
    
    def test_get_reservations_by_device(self, db_manager, sample_user, sample_device):
        """Test getting reservations by device."""
        db_manager.add_user(sample_user)
        db_manager.add_device(sample_device)
        
        now = datetime.now()
        res = Reservation.create_new(
            device_id=sample_device.id,
            user_id=sample_user.user_id,
            start=now + timedelta(hours=1),
            end=now + timedelta(hours=3)
        )
        db_manager.add_reservation(res)
        
        reservations = db_manager.get_reservations_by_device(sample_device.id)
        assert len(reservations) == 1
    
    def test_get_reservations_by_user(self, db_manager, sample_user, sample_device):
        """Test getting reservations by user."""
        db_manager.add_user(sample_user)
        db_manager.add_device(sample_device)
        
        now = datetime.now()
        res = Reservation.create_new(
            device_id=sample_device.id,
            user_id=sample_user.user_id,
            start=now + timedelta(hours=1),
            end=now + timedelta(hours=3)
        )
        db_manager.add_reservation(res)
        
        reservations = db_manager.get_reservations_by_user(sample_user.user_id)
        assert len(reservations) == 1
    
    def test_is_device_available(self, db_manager, sample_user, sample_device):
        """Test device availability check."""
        db_manager.add_user(sample_user)
        db_manager.add_device(sample_device)
        
        now = datetime.now()
        res = Reservation.create_new(
            device_id=sample_device.id,
            user_id=sample_user.user_id,
            start=now + timedelta(hours=1),
            end=now + timedelta(hours=3)
        )
        db_manager.add_reservation(res)
        
        # Check availability during booked time
        is_available = db_manager.is_device_available(
            sample_device.id,
            now + timedelta(hours=2),
            now + timedelta(hours=4)
        )
        assert is_available is False
        
        # Check availability for non-overlapping time
        is_available = db_manager.is_device_available(
            sample_device.id,
            now + timedelta(hours=5),
            now + timedelta(hours=7)
        )
        assert is_available is True
    
    def test_cancel_reservation(self, db_manager, sample_user, sample_device):
        """Test cancelling a reservation."""
        db_manager.add_user(sample_user)
        db_manager.add_device(sample_device)
        
        now = datetime.now()
        res = Reservation.create_new(
            device_id=sample_device.id,
            user_id=sample_user.user_id,
            start=now + timedelta(hours=1),
            end=now + timedelta(hours=3)
        )
        db_manager.add_reservation(res)
        
        result = db_manager.cancel_reservation(res.id)
        assert result is not None
        assert result.status == "cancelled"
    
    def test_delete_reservation(self, db_manager, sample_user, sample_device):
        """Test deleting a reservation."""
        db_manager.add_user(sample_user)
        db_manager.add_device(sample_device)
        
        now = datetime.now()
        res = Reservation.create_new(
            device_id=sample_device.id,
            user_id=sample_user.user_id,
            start=now + timedelta(hours=1),
            end=now + timedelta(hours=3)
        )
        db_manager.add_reservation(res)
        
        result = db_manager.delete_reservation(res.id)
        assert result is True
        
        fetched = db_manager.get_reservation(res.id)
        assert fetched is None


class TestDBManagerStatistics:
    """Tests for statistics and reporting."""
    
    def test_get_statistics(self, db_manager, sample_users, sample_devices):
        """Test getting system statistics."""
        for user in sample_users:
            db_manager.add_user(user)
        for device in sample_devices:
            db_manager.add_device(device)
        
        stats = db_manager.get_statistics()
        
        assert stats["total_users"] == len(sample_users)
        assert stats["total_devices"] == len(sample_devices)
        assert "total_maintenance_cost" in stats
