import os
from typing import List, Optional
from tinydb import TinyDB, Query
from tinydb.table import Table

from src.models.user import User
from src.models.device import Device
from src.models.reservation import Reservation

class DBManager:
    """Handles all interactions with the TinyDB JSON database."""

    def __init__(self, db_path: str = 'data/db.json'):
        self._ensure_directory(db_path)
        self.db: TinyDB = TinyDB(db_path)
        self.users_table: Table = self.db.table('users')
        self.devices_table: Table = self.db.table('devices')
        self.reservations_table: Table = self.db.table('reservations')

    def _ensure_directory(self, path: str) -> None:
        """Create the data directory if it doesn't exist."""
        os.makedirs(os.path.dirname(path), exist_ok=True)

    # User Operations
    def add_user(self, user: User) -> None:
        """Add a new user or update if the user_id already exists."""
        UserQuery = Query()
        if self.users_table.search(UserQuery.user_id == user.user_id):
            self.users_table.update(user.to_dict(), UserQuery.user_id == user.user_id)
        else:
            self.users_table.insert(user.to_dict())

    def get_all_users(self) -> List[User]:
        """Retrieve all users."""
        return [User.from_dict(doc) for doc in self.users_table.all()]

    def delete_user(self, user_id: str) -> None:
        """Delete a user by ID."""
        UserQuery = Query()
        self.users_table.remove(UserQuery.user_id == user_id)

        # Remove associated reservations
        ReservationQuery = Query()
        self.reservations_table.remove(ReservationQuery.user_id == user_id)

    # Device Operations
    def add_device(self, device: Device) -> None:
        """Add a new device or update existing one by ID."""
        DeviceQuery = Query()
        if self.devices_table.search(DeviceQuery.id == device.id):
            self.devices_table.update(device.to_dict(), DeviceQuery.id == device.id)
        else:
            self.devices_table.insert(device.to_dict())

    def get_all_devices(self) -> List[Device]:
        """Retrieve all devices."""
        return [Device.from_dict(doc) for doc in self.devices_table.all()]
    
    def get_device(self, device_id: str) -> Optional[Device]:
        """Retrieve a single device by ID."""
        DeviceQuery = Query()
        result = self.devices_table.search(DeviceQuery.id == device_id)
        return Device.from_dict(result[0]) if result else None

    def delete_device(self, device_id: str) -> None:
        """Delete a device by ID and its associated reservations."""
        DeviceQuery = Query()
        self.devices_table.remove(DeviceQuery.id == device_id)
        
        # Remove associated reservations
        ReservationQuery = Query()
        self.reservations_table.remove(ReservationQuery.device_id == device_id)

    # Reservation Operations
    def add_reservation(self, reservation: Reservation) -> None:
        """Store a new reservation."""
        self.reservations_table.insert(reservation.to_dict())

    def get_reservations_by_device(self, device_id: str) -> List[Reservation]:
        """Get all reservations for a specific device."""
        ReservationQuery = Query()
        results = self.reservations_table.search(ReservationQuery.device_id == device_id)
        return [Reservation.from_dict(doc) for doc in results]

    def get_all_reservations(self) -> List[Reservation]:
        """Retrieve all reservations."""
        return [Reservation.from_dict(doc) for doc in self.reservations_table.all()]

    def delete_reservation(self, reservation_id: str) -> None:
        """Delete a reservation by ID."""
        ReservationQuery = Query()
        self.reservations_table.remove(ReservationQuery.id == reservation_id)