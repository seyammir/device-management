"""Unit tests for the Reservation model."""
import pytest
from datetime import datetime, timedelta

from src.models.reservation import Reservation, ReservationValidationError


class TestReservationModel:
    """Tests for the Reservation dataclass."""
    
    def test_reservation_creation_valid(self):
        """Test creating a valid reservation."""
        now = datetime.now()
        res = Reservation(
            id="RES001",
            device_id="DEV001",
            user_id="U001",
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=3)
        )
        assert res.id == "RES001"
        assert res.device_id == "DEV001"
        assert res.status == "confirmed"
    
    def test_reservation_creation_with_all_fields(self):
        """Test creating a reservation with all fields."""
        now = datetime.now()
        res = Reservation(
            id="RES001",
            device_id="DEV001",
            user_id="U001",
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=3),
            purpose="Project work",
            notes="Test notes",
            status="pending"
        )
        assert res.purpose == "Project work"
        assert res.notes == "Test notes"
        assert res.status == "pending"
    
    def test_reservation_create_new_factory(self):
        """Test the create_new factory method."""
        now = datetime.now()
        res = Reservation.create_new(
            device_id="DEV001",
            user_id="U001",
            start=now + timedelta(hours=1),
            end=now + timedelta(hours=3),
            purpose="Testing"
        )
        assert res.id is not None
        assert len(res.id) > 0
        assert res.purpose == "Testing"
    
    def test_reservation_invalid_empty_id(self):
        """Test that empty id raises validation error."""
        now = datetime.now()
        with pytest.raises(ReservationValidationError, match="Reservation ID cannot be empty"):
            Reservation(
                id="",
                device_id="DEV001",
                user_id="U001",
                start_time=now + timedelta(hours=1),
                end_time=now + timedelta(hours=3)
            )
    
    def test_reservation_invalid_time_order(self):
        """Test that end time before start time raises error."""
        now = datetime.now()
        with pytest.raises(ReservationValidationError, match="End time must be after start time"):
            Reservation(
                id="RES001",
                device_id="DEV001",
                user_id="U001",
                start_time=now + timedelta(hours=3),
                end_time=now + timedelta(hours=1)
            )
    
    def test_reservation_invalid_same_time(self):
        """Test that same start and end time raises error."""
        now = datetime.now()
        time = now + timedelta(hours=1)
        with pytest.raises(ReservationValidationError, match="End time must be after start time"):
            Reservation(
                id="RES001",
                device_id="DEV001",
                user_id="U001",
                start_time=time,
                end_time=time
            )
    
    def test_reservation_invalid_status(self):
        """Test that invalid status raises error."""
        now = datetime.now()
        with pytest.raises(ReservationValidationError, match="Invalid status"):
            Reservation(
                id="RES001",
                device_id="DEV001",
                user_id="U001",
                start_time=now + timedelta(hours=1),
                end_time=now + timedelta(hours=3),
                status="invalid"
            )
    
    def test_reservation_duration(self):
        """Test duration calculation."""
        now = datetime.now()
        res = Reservation(
            id="RES001",
            device_id="DEV001",
            user_id="U001",
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=4)
        )
        assert res.duration == timedelta(hours=3)
        assert res.duration_hours == 3.0
    
    def test_reservation_is_upcoming(self):
        """Test upcoming reservation detection."""
        now = datetime.now()
        res = Reservation(
            id="RES001",
            device_id="DEV001",
            user_id="U001",
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=3)
        )
        assert res.is_upcoming is True
    
    def test_reservation_is_past(self):
        """Test past reservation detection."""
        now = datetime.now()
        res = Reservation(
            id="RES001",
            device_id="DEV001",
            user_id="U001",
            start_time=now - timedelta(hours=3),
            end_time=now - timedelta(hours=1)
        )
        assert res.is_past is True
    
    def test_reservation_conflicts_with_overlap(self):
        """Test conflict detection with overlapping reservations."""
        now = datetime.now()
        res1 = Reservation(
            id="RES001",
            device_id="DEV001",
            user_id="U001",
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=4)
        )
        res2 = Reservation(
            id="RES002",
            device_id="DEV001",
            user_id="U002",
            start_time=now + timedelta(hours=2),
            end_time=now + timedelta(hours=5)
        )
        assert res1.conflicts_with(res2) is True
        assert res2.conflicts_with(res1) is True
    
    def test_reservation_conflicts_with_no_overlap(self):
        """Test no conflict with non-overlapping reservations."""
        now = datetime.now()
        res1 = Reservation(
            id="RES001",
            device_id="DEV001",
            user_id="U001",
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=3)
        )
        res2 = Reservation(
            id="RES002",
            device_id="DEV001",
            user_id="U002",
            start_time=now + timedelta(hours=5),
            end_time=now + timedelta(hours=7)
        )
        assert res1.conflicts_with(res2) is False
    
    def test_reservation_conflicts_with_different_device(self):
        """Test no conflict with different devices."""
        now = datetime.now()
        res1 = Reservation(
            id="RES001",
            device_id="DEV001",
            user_id="U001",
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=3)
        )
        res2 = Reservation(
            id="RES002",
            device_id="DEV002",
            user_id="U002",
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=3)
        )
        assert res1.conflicts_with(res2) is False
    
    def test_reservation_cancel(self):
        """Test cancelling a reservation."""
        now = datetime.now()
        res = Reservation(
            id="RES001",
            device_id="DEV001",
            user_id="U001",
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=3)
        )
        res.cancel()
        assert res.status == "cancelled"
    
    def test_reservation_confirm(self):
        """Test confirming a reservation."""
        now = datetime.now()
        res = Reservation(
            id="RES001",
            device_id="DEV001",
            user_id="U001",
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=3),
            status="pending"
        )
        res.confirm()
        assert res.status == "confirmed"
    
    def test_reservation_complete(self):
        """Test completing a reservation."""
        now = datetime.now()
        res = Reservation(
            id="RES001",
            device_id="DEV001",
            user_id="U001",
            start_time=now - timedelta(hours=3),
            end_time=now - timedelta(hours=1)
        )
        res.complete()
        assert res.status == "completed"
    
    def test_reservation_to_dict(self):
        """Test converting reservation to dictionary."""
        now = datetime.now()
        res = Reservation(
            id="RES001",
            device_id="DEV001",
            user_id="U001",
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=3),
            purpose="Testing"
        )
        data = res.to_dict()
        
        assert data["id"] == "RES001"
        assert data["purpose"] == "Testing"
        assert "created_at" in data
    
    def test_reservation_from_dict(self):
        """Test creating reservation from dictionary."""
        now = datetime.now()
        data = {
            "id": "RES001",
            "device_id": "DEV001",
            "user_id": "U001",
            "start_time": (now + timedelta(hours=1)).isoformat(),
            "end_time": (now + timedelta(hours=3)).isoformat(),
            "purpose": "Testing",
            "notes": "Test notes",
            "status": "confirmed",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }
        res = Reservation.from_dict(data)
        
        assert res.id == "RES001"
        assert res.purpose == "Testing"
    
    def test_reservation_from_dict_minimal(self):
        """Test creating reservation from minimal dictionary."""
        now = datetime.now()
        data = {
            "id": "RES001",
            "device_id": "DEV001",
            "user_id": "U001",
            "start_time": (now + timedelta(hours=1)).isoformat(),
            "end_time": (now + timedelta(hours=3)).isoformat()
        }
        res = Reservation.from_dict(data)
        
        assert res.purpose == ""
        assert res.status == "confirmed"
    
    def test_reservation_update(self):
        """Test updating reservation fields."""
        now = datetime.now()
        res = Reservation(
            id="RES001",
            device_id="DEV001",
            user_id="U001",
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=3)
        )
        original_updated = res.updated_at
        
        res.update(purpose="Updated purpose", notes="Updated notes")
        
        assert res.purpose == "Updated purpose"
        assert res.notes == "Updated notes"
        assert res.updated_at > original_updated
    
    def test_reservation_str_repr(self):
        """Test string representation."""
        now = datetime.now()
        res = Reservation(
            id="RES00001-1234-5678-9abc",
            device_id="DEV001",
            user_id="U001",
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=3)
        )
        str_repr = str(res)
        assert "RES00001" in str_repr
        assert "DEV001" in str_repr
