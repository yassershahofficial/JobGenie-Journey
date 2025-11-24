"""Path utilities for the O*NET database scraper."""

import os
import sys


def get_app_path():
    """Get the application path for both executable and script modes."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)  # For executable mode: pyinstaller exe
    else:
        # Return the onet_job_scraping directory (parent of utils/)
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # For testing before executable

