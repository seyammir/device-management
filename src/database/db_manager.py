import os
from typing import List, Optional, TypedDict
from datetime import datetime
from tinydb import TinyDB, Query
from tinydb.table import Table

from src.models.user import User
from src.models.device import Device
from src.models.reservation import Reservation
from src.core.config import Config
from src.core.logger import get_logger

# Configure logging
logger = get_logger("db_manager")


class DatabaseError(Exception):
    """Custom exception for database operations."""
    pass


class SystemStatistics(TypedDict):
    """Type definition for system statistics."""
    total_users: int
    active_users: int
    total_devices: int
    active_devices: int
    devices_needing_maintenance: int
    total_reservations: int
    upcoming_reservations: int
    active_reservations: int
    total_maintenance_cost: float


class DBManager:
    """Handles all interactions with the TinyDB JSON database."""

    _instance: Optional['DBManager'] = None
    _db_path: Optional[str] = None

    def __new__(cls, db_path: Optional[str] = None):
        """Implement singleton pattern to avoid multiple DB connections."""
        if db_path is None:
            db_path = Config.DB_PATH
        
        # If instance exists with different path, close it first
        if cls._instance is not None and cls._db_path != db_path:
            cls._instance.close()
            cls._instance = None
        
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
            cls._db_path = db_path
        return cls._instance

    def __init__(self, db_path: Optional[str] = None):
        if self._initialized:
            return
        if db_path is None:
            db_path = Config.DB_PATH
        self._ensure_directory(db_path)
        self.db: TinyDB = TinyDB(db_path)
        self.users_table: Table = self.db.table('users')
        self.devices_table: Table = self.db.table('devices')
        self.reservations_table: Table = self.db.table('reservations')
        self._initialized = True
        logger.info(f"Database initialized at {db_path}")

    def _ensure_directory(self, path: str) -> None:
        """Create the data directory if it doesn't exist."""
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def close(self) -> None:
        """Close the database connection."""
        self.db.close()
        DBManager._instance = None
        self._initialized = False
        logger.info("Database connection closed")

    # User Operations

    def add_user(self, user: User) -> User:
        """Add a new user or update if the user_id already exists."""
        try:
            UserQuery = Query()
            existing = self.users_table.search(UserQuery.user_id == user.user_id)
            if existing:
                self.users_table.update(user.to_dict(), UserQuery.user_id == user.user_id)
                logger.info(f"Updated user: {user.user_id}")
            else:
                self.users_table.insert(user.to_dict())
                logger.info(f"Added new user: {user.user_id}")
            return user
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            raise DatabaseError(f"Failed to add user: {e}")

    def get_user(self, user_id: str) -> Optional[User]:
        """Retrieve a single user by ID."""
        UserQuery = Query()
        result = self.users_table.search(UserQuery.user_id == user_id)
        return User.from_dict(result[0]) if result else None

    def get_all_users(self) -> List[User]:
        """Retrieve all users."""
        return [User.from_dict(doc) for doc in self.users_table.all()]

    def get_active_users(self) -> List[User]:
        """Retrieve only active users."""
        UserQuery = Query()
        results = self.users_table.search(UserQuery.is_active == True)
        return [User.from_dict(doc) for doc in results]

    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """Update specific fields of a user."""
        user = self.get_user(user_id)
        if not user:
            return None
        try:
            user.update(**kwargs)
            UserQuery = Query()
            self.users_table.update(user.to_dict(), UserQuery.user_id == user_id)
            logger.info(f"Updated user {user_id} with fields: {kwargs.keys()}")
            return user
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            raise DatabaseError(f"Failed to update user: {e}")

    def delete_user(self, user_id: str) -> bool:
        """Delete a user by ID and associated reservations."""
        UserQuery = Query()
        removed = self.users_table.remove(UserQuery.user_id == user_id)
        
        if removed:
            # Remove associated reservations
            ReservationQuery = Query()
            self.reservations_table.remove(ReservationQuery.user_id == user_id)
            logger.info(f"Deleted user: {user_id}")
            return True
        return False

    # Device Operations

    def add_device(self, device: Device) -> Device:
        """Add a new device or update existing one by ID."""
        try:
            DeviceQuery = Query()
            existing = self.devices_table.search(DeviceQuery.id == device.id)
            if existing:
                self.devices_table.update(device.to_dict(), DeviceQuery.id == device.id)
                logger.info(f"Updated device: {device.id}")
            else:
                self.devices_table.insert(device.to_dict())
                logger.info(f"Added new device: {device.id}")
            return device
        except Exception as e:
            logger.error(f"Error adding device: {e}")
            raise DatabaseError(f"Failed to add device: {e}")

    def get_device(self, device_id: str) -> Optional[Device]:
        """Retrieve a single device by ID."""
        DeviceQuery = Query()
        result = self.devices_table.search(DeviceQuery.id == device_id)
        return Device.from_dict(result[0]) if result else None

    def get_all_devices(self) -> List[Device]:
        """Retrieve all devices."""
        return [Device.from_dict(doc) for doc in self.devices_table.all()]

    def get_active_devices(self) -> List[Device]:
        """Retrieve only active devices."""
        DeviceQuery = Query()
        results = self.devices_table.search(DeviceQuery.status == "active")
        return [Device.from_dict(doc) for doc in results]

    def get_devices_needing_maintenance(self) -> List[Device]:
        """Get devices that need maintenance (overdue or upcoming in 7 days)."""
        devices = self.get_active_devices()
        now = datetime.now()
        return [d for d in devices if d.days_until_maintenance <= 7]

    def update_device(self, device_id: str, **kwargs) -> Optional[Device]:
        """Update specific fields of a device."""
        device = self.get_device(device_id)
        if not device:
            return None
        try:
            device.update(**kwargs)
            DeviceQuery = Query()
            self.devices_table.update(device.to_dict(), DeviceQuery.id == device_id)
            logger.info(f"Updated device {device_id} with fields: {kwargs.keys()}")
            return device
        except Exception as e:
            logger.error(f"Error updating device: {e}")
            raise DatabaseError(f"Failed to update device: {e}")

    def delete_device(self, device_id: str) -> bool:
        """Delete a device by ID and its associated reservations."""
        DeviceQuery = Query()
        removed = self.devices_table.remove(DeviceQuery.id == device_id)
        
        if removed:
            # Remove associated reservations
            ReservationQuery = Query()
            self.reservations_table.remove(ReservationQuery.device_id == device_id)
            logger.info(f"Deleted device: {device_id}")
            return True
        return False

    # Reservation Operations

    def add_reservation(self, reservation: Reservation) -> Reservation:
        """Store a new reservation after checking for conflicts."""
        try:
            # Check for conflicts
            if not self.is_device_available(
                reservation.device_id, 
                reservation.start_time, 
                reservation.end_time,
                exclude_id=reservation.id
            ):
                raise DatabaseError("Device is not available for the requested time slot")
            
            self.reservations_table.insert(reservation.to_dict())
            logger.info(f"Added reservation: {reservation.id}")
            return reservation
        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"Error adding reservation: {e}")
            raise DatabaseError(f"Failed to add reservation: {e}")

    def get_reservation(self, reservation_id: str) -> Optional[Reservation]:
        """Retrieve a single reservation by ID."""
        ReservationQuery = Query()
        result = self.reservations_table.search(ReservationQuery.id == reservation_id)
        return Reservation.from_dict(result[0]) if result else None

    def get_reservations_by_device(self, device_id: str) -> List[Reservation]:
        """Get all reservations for a specific device."""
        ReservationQuery = Query()
        results = self.reservations_table.search(ReservationQuery.device_id == device_id)
        return [Reservation.from_dict(doc) for doc in results]

    def get_reservations_by_user(self, user_id: str) -> List[Reservation]:
        """Get all reservations for a specific user."""
        ReservationQuery = Query()
        results = self.reservations_table.search(ReservationQuery.user_id == user_id)
        return [Reservation.from_dict(doc) for doc in results]

    def get_all_reservations(self) -> List[Reservation]:
        """Retrieve all reservations."""
        return [Reservation.from_dict(doc) for doc in self.reservations_table.all()]

    def get_upcoming_reservations(self) -> List[Reservation]:
        """Get all upcoming reservations."""
        reservations = self.get_all_reservations()
        return [r for r in reservations if r.is_upcoming]

    def get_active_reservations(self) -> List[Reservation]:
        """Get currently active reservations."""
        reservations = self.get_all_reservations()
        return [r for r in reservations if r.is_active]

    def update_reservation(self, reservation_id: str, **kwargs) -> Optional[Reservation]:
        """Update specific fields of a reservation."""
        reservation = self.get_reservation(reservation_id)
        if not reservation:
            return None
        try:
            reservation.update(**kwargs)
            ReservationQuery = Query()
            self.reservations_table.update(
                reservation.to_dict(), 
                ReservationQuery.id == reservation_id
            )
            logger.info(f"Updated reservation {reservation_id}")
            return reservation
        except Exception as e:
            logger.error(f"Error updating reservation: {e}")
            raise DatabaseError(f"Failed to update reservation: {e}")

    def delete_reservation(self, reservation_id: str) -> bool:
        """Delete a reservation by ID."""
        ReservationQuery = Query()
        removed = self.reservations_table.remove(ReservationQuery.id == reservation_id)
        if removed:
            logger.info(f"Deleted reservation: {reservation_id}")
            return True
        return False

    def cancel_reservation(self, reservation_id: str) -> Optional[Reservation]:
        """Cancel a reservation (soft delete)."""
        result = self.update_reservation(reservation_id, status="cancelled")
        if result:
            logger.info(f"Cancelled reservation: {reservation_id}")
        return result

    def is_device_available(
        self, 
        device_id: str, 
        start: datetime, 
        end: datetime,
        exclude_id: Optional[str] = None
    ) -> bool:
        """Check if a device is available for a time slot."""
        existing = self.get_reservations_by_device(device_id)
        for res in existing:
            if exclude_id and res.id == exclude_id:
                continue
            if res.status == "cancelled":
                continue
            # Overlap check
            if start < res.end_time and end > res.start_time:
                return False
        return True

    # Statistics & Reports

    def get_statistics(self) -> SystemStatistics:
        """Get overall system statistics."""
        devices = self.get_all_devices()
        users = self.get_all_users()
        reservations = self.get_all_reservations()
        
        # Calculate counts in single pass for better performance
        active_users = sum(1 for u in users if u.is_active)
        active_devices = [d for d in devices if d.status == "active"]
        maintenance_needed = sum(1 for d in active_devices if d.days_until_maintenance <= 7)
        upcoming_res = sum(1 for r in reservations if r.is_upcoming)
        active_res = sum(1 for r in reservations if r.is_active)
        
        return {
            "total_users": len(users),
            "active_users": active_users,
            "total_devices": len(devices),
            "active_devices": len(active_devices),
            "devices_needing_maintenance": maintenance_needed,
            "total_reservations": len(reservations),
            "upcoming_reservations": upcoming_res,
            "active_reservations": active_res,
            "total_maintenance_cost": sum(d.maintenance_cost for d in devices)
        }