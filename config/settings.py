"""
Application configuration and settings for Stock Manager.
"""

import os

# --- Configuration ---
DATA_DIR = "data"

# Configuration file path
COMPANY_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'company_config.json')

# Stock alert thresholds
LOW_STOCK_THRESHOLD = 10
EXPIRY_SOON_DAYS = 60

# Font configurations
FONTS = {
    'base': ('Segoe UI', 14),
    'heading': ('Segoe UI', 22, 'bold'),
    'subheading': ('Segoe UI', 18, 'bold'),
    'label': ('Segoe UI', 15),
    'button': ('Segoe UI', 15, 'bold'),
    'entry': ('Segoe UI', 15),
    'tree': ('Segoe UI', 15),
    'tree_heading': ('Segoe UI', 17, 'bold')
}

# Window configuration
WINDOW_GEOMETRY = "1100x750"
APP_TITLE = "Stock Mitra"

# Ensure data directory exists
def ensure_data_directory():
    """Ensure the data directory exists."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)