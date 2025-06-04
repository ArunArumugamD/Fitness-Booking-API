"""
Timezone utility functions for handling IST conversions.
"""
from datetime import datetime
import pytz
from ..config import IST


def datetime_to_ist(dt: datetime) -> datetime:
    """Convert any datetime to IST"""
    if dt.tzinfo is None:
        # Assume naive datetime is UTC
        dt = pytz.UTC.localize(dt)
    return dt.astimezone(IST)


def ist_to_utc(dt: datetime) -> datetime:
    """Convert IST datetime to UTC for storage"""
    if dt.tzinfo is None:
        # Localize to IST first
        dt = IST.localize(dt)
    return dt.astimezone(pytz.UTC)


def parse_ist_string(dt_string: str) -> datetime:
    """
    Parse a datetime string and return UTC datetime.
    Assumes input is in IST if no timezone specified.
    """
    dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        dt = IST.localize(dt)
    return dt.astimezone(pytz.UTC)