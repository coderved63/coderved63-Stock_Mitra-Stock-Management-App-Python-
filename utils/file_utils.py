"""
File and path utility functions for Stock Manager application.
"""

import os


def get_log_file_path(company_json_file, log_type):
    """Get the log file path for a company and log type."""
    # log_type: 'sales' or 'purchase'
    base_dir = os.path.dirname(company_json_file)
    company_name = os.path.splitext(os.path.basename(company_json_file))[0]
    return os.path.join(base_dir, f"{company_name}_{log_type}_log.json")