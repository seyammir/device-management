"""Application configuration settings."""
import os
from typing import List


class Config:
    """Central configuration for the Device Management System."""
    
    # Database settings
    DB_PATH: str = "data/db.json"
    
    # Application settings
    APP_NAME: str = "Device Management System"
    APP_VERSION: str = "1.0.0"
    
    # Date/Time formats
    DATE_FORMAT: str = "%Y-%m-%d"
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M"
    TIME_FORMAT: str = "%H:%M"
    
    # Currency
    CURRENCY_SYMBOL: str = "€"
    
    # Maintenance settings
    MAINTENANCE_WARNING_DAYS: int = 7
    
    # Device statuses
    DEVICE_STATUSES: List[str] = ["active", "maintenance", "retired"]
    
    # Reservation statuses
    RESERVATION_STATUSES: List[str] = ["pending", "confirmed", "cancelled", "completed"]
    
    # Logging
    LOG_DIR: str = "logs"
    LOG_FILE: str = "app.log"
    LOG_LEVEL: str = "INFO"
    
    # Export settings
    EXPORT_DIR: str = "exports"
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure all required directories exist."""
        directories = [
            os.path.dirname(cls.DB_PATH),
            cls.LOG_DIR,
            cls.EXPORT_DIR
        ]
        for directory in directories:
            if directory:
                os.makedirs(directory, exist_ok=True)
