"""Main orchestration module for the O*NET database scraper."""

import os
import re
import sys
import time
from datetime import datetime

# Handle both relative imports (when used as module) and absolute imports (when run directly)
try:
    from .config import FILES_TO_KEEP, ONET_DATABASE_URL, OUTPUT_DIR_NAME, EXTRACTED_DIR_NAME
    from .utils.paths import get_app_path
    from .utils.selenium_helpers import create_driver
    from .scraper.version_extractor import get_latest_version
    from .scraper.link_finder import find_excel_download_link
    from .downloader import download_file
    from .extractor import extract_zip
    from .cleanup import cleanup_files
except ImportError:
    # When run directly, add parent directory to path
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from onet_job_scraping.config import FILES_TO_KEEP, ONET_DATABASE_URL, OUTPUT_DIR_NAME, EXTRACTED_DIR_NAME
    from onet_job_scraping.utils.paths import get_app_path
    from onet_job_scraping.utils.selenium_helpers import create_driver
    from onet_job_scraping.scraper.version_extractor import get_latest_version
    from onet_job_scraping.scraper.link_finder import find_excel_download_link
    from onet_job_scraping.downloader import download_file
    from onet_job_scraping.extractor import extract_zip
    from onet_job_scraping.cleanup import cleanup_files


def main():
    """Main function to orchestrate the O*NET database scraping process."""
    # Setup paths
    app_path = get_app_path()
    output_path = os.path.join(app_path, OUTPUT_DIR_NAME)
    extracted_path = os.path.join(output_path, EXTRACTED_DIR_NAME)
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    website = ONET_DATABASE_URL
    
    # Create driver
    driver = create_driver(headless=True)
    
    try:
        print(f"Navigating to {website}...")
        driver.get(website)
        
        # Wait for page to load
        time.sleep(2)
        
        # Get the latest version
        print("Extracting database version...")
        version = get_latest_version(driver)
        print(f"Found O*NET Database version: {version}")
        
        # Validate version format (should be like "30.0")
        if not re.match(r'^\d+\.\d+$', version):
            print(f"Warning: Invalid version format '{version}'. Using timestamp as fallback.")
            version = datetime.now().strftime("%Y%m%d_%H%M%S")
            print(f"Using fallback version: {version}")
        
        # Find the Excel download link
        print("Locating Excel download link...")
        download_url = find_excel_download_link(driver)
        print(f"Found download URL: {download_url}")
        
        # Determine filename
        filename = f"onet_database_{version}.zip"
        zip_path = os.path.join(output_path, filename)
        
        # Download the file (will skip if already exists)
        download_file(download_url, zip_path)
        
        # Extract the ZIP file (will skip if already extracted)
        extraction_success = False
        try:
            extract_zip(zip_path, extracted_path)
            extraction_success = True
        except Exception as e:
            print(f"Extraction failed: {e}")
            raise
        
        # Cleanup: Delete ZIP and keep only specified files (only if extraction succeeded)
        if extraction_success:
            cleanup_files(zip_path, extracted_path, FILES_TO_KEEP)
        
        print("\n" + "="*50)
        print("O*NET Database scraping completed successfully!")
        print(f"Extracted to: {extracted_path}")
        print(f"Kept {len(FILES_TO_KEEP)} essential Excel files")
        print("="*50)
        
    except Exception as e:
        print(f"\nError during scraping: {e}")
        raise
    finally:
        print("\nClosing browser...")
        try:
            driver.quit()
        except Exception as e:
            print(f"Warning: Error closing browser: {e}")
            # Try to close anyway - some errors are non-critical
            try:
                driver.close()
            except Exception:
                pass


if __name__ == "__main__":
    main()

