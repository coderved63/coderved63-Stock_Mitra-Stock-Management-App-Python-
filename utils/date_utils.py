"""
Date and time utility functions for Stock Manager application.
"""

import datetime


def format_date(date_obj):
    """Format a date object as a string."""
    if not date_obj:
        return 'N/A'
    if isinstance(date_obj, datetime.date):
        return date_obj.strftime("%Y-%m-%d")
    return date_obj  # Assume it's already a string if not a date object


def parse_date(date_str):
    """Parse a date string into a date object."""
    if not date_str:
        return None
    try:
        return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None