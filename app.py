#!/usr/bin/env python3
"""
Stock Manager Application Launcher
This script properly sets up the Python path and launches the application.
"""

import sys
import os

# Add the current directory to Python path for absolute imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Now import and run the main application
from main import main

if __name__ == "__main__":
    main()