"""Utility functions for the Device Management System."""
import re
from datetime import datetime, date, time, timedelta
from typing import Dict, List, TYPE_CHECKING

from src.core.config import Config

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.device import Device


def format_currency(amount: float, symbol: str = Config.CURRENCY_SYMBOL) -> str:
    """Format a number as currency."""
    return f"{symbol}{amount:,.2f}"


def format_date(dt: datetime | date, fmt: str = Config.DATE_FORMAT) -> str:
    """Format a datetime or date object as string."""
    return dt.strftime(fmt)


def date_to_datetime(d: date, t: time | None = None) -> datetime:
    """Convert a date object to datetime, optionally with a specific time.
    
    Args:
        d: The date to convert
        t: Optional time component (defaults to midnight)
    
    Returns:
        A datetime object combining date and time
    """
    if t is None:
        t = time.min
    return datetime.combine(d, t)


def format_datetime(dt: datetime, fmt: str = Config.DATETIME_FORMAT) -> str:
    """Format a datetime object as string with time."""
    return dt.strftime(fmt)


def format_time(t: datetime | time, fmt: str = Config.TIME_FORMAT) -> str:
    """Format a time object as string."""
    return t.strftime(fmt)


def is_valid_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def get_status_emoji(status: str) -> str:
    """Get an emoji for a status value (for UI use)."""
    status_emojis = {
        # Device statuses
        "active": "✅",
        "maintenance": "🔧",
        "retired": "❌",
        # Reservation statuses
        "pending": "⏳",
        "confirmed": "✅",
        "cancelled": "🚫",
        "completed": "✔️",
        # Maintenance statuses
        "ok": "✅",
        "upcoming": "⚠️",
        "overdue": "🚨"
    }
    return status_emojis.get(status.lower(), "❓")


def create_user_map(users: List['User']) -> Dict[str, str]:
    """Create a mapping of display names to user IDs.
    
    Args:
        users: List of User objects
    
    Returns:
        Dict mapping "Name (ID)" to user_id
    """
    return {f"{u.name} ({u.user_id})": u.user_id for u in users}


def create_user_id_to_name_map(users: List['User']) -> Dict[str, str]:
    """Create a mapping of user IDs to display names.
    
    Args:
        users: List of User objects
    
    Returns:
        Dict mapping user_id to "Name (ID)"
    """
    return {u.user_id: f"{u.name} ({u.user_id})" for u in users}


def create_device_map(devices: List['Device']) -> Dict[str, str]:
    """Create a mapping of display names to device IDs.
    
    Args:
        devices: List of Device objects
    
    Returns:
        Dict mapping "Name (ID)" to device id
    """
    return {f"{d.name} ({d.id})": d.id for d in devices}


def create_device_id_to_name_map(devices: List['Device']) -> Dict[str, str]:
    """Create a mapping of device IDs to names.
    
    Args:
        devices: List of Device objects
    
    Returns:
        Dict mapping device id to name
    """
    return {d.id: d.name for d in devices}
