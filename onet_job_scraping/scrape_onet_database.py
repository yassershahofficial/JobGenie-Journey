"""
Backward compatibility wrapper for the O*NET database scraper.

This module maintains compatibility with existing code that imports or runs
scrape_onet_database.py directly. It delegates to the modular main.py.
"""

import sys
import os

# Add parent directory to path for direct execution
if __name__ == "__main__":
    # When run directly, add parent directory to path to allow imports
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

# Import the main function from the modular structure
# Try relative import first (when used as a module)
try:
    from .main import main
except (ImportError, ValueError):
    # Fall back to absolute import (when run directly)
    # ValueError can occur when relative import is attempted in non-package context
    from onet_job_scraping.main import main

# Re-export main for backward compatibility
__all__ = ['main']

# Allow running this file directly
if __name__ == "__main__":
    main()
