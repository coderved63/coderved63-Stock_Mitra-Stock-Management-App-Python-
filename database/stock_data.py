"""
Stock data management and persistence layer.
"""

import json
import os
from tkinter import messagebox


def load_stock_data(filepath):
    """Loads stock data from a JSON file."""
    if not os.path.exists(filepath):
        with open(filepath, 'w') as f:
            json.dump([], f)
        return []
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_stock_data(data, filepath):
    """Saves stock data to a JSON file."""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        messagebox.showerror("Save Error", f"Error saving data to {filepath}: {e}")


def load_company_configs():
    """Load company configurations from the config file."""
    from config.settings import COMPANY_CONFIG_FILE
    if not os.path.exists(COMPANY_CONFIG_FILE):
        return {}
    try:
        with open(COMPANY_CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}


def save_company_configs(configs):
    """Save company configurations to the config file."""
    from config.settings import COMPANY_CONFIG_FILE
    try:
        with open(COMPANY_CONFIG_FILE, 'w') as f:
            json.dump(configs, f, indent=4)
    except Exception as e:
        messagebox.showerror("Save Error", f"Error saving company configs: {e}")


def load_log(log_file):
    """Load log entries from a log file."""
    if not os.path.exists(log_file):
        with open(log_file, 'w') as f:
            json.dump([], f)
        return []
    try:
        with open(log_file, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def append_log_entry(log_file, entry):
    """Append an entry to a log file."""
    log = load_log(log_file)
    log.append(entry)
    with open(log_file, 'w') as f:
        json.dump(log, f, indent=4)