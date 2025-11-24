from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
import zipfile
import os
import sys
import re
import time
from urllib.parse import urljoin
from datetime import datetime

def get_app_path():
    """Get the application path for both executable and script modes."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)  # For executable mode: pyinstaller exe
    else:
        return os.path.dirname(os.path.abspath(__file__))  # For testing before executable

def find_any_element(element, xpaths):
    """Find the first element that matches any of the given XPath expressions."""
    for xpath in xpaths:
        elements = element.find_elements(by="xpath", value=xpath)
        if elements:
            return elements[0]
    return None

def get_latest_version(driver):
    """Extract the latest O*NET database version number from the page."""
    try:
        # Look for version text like "O*NET 30.0 Database" or "O*NET® 30.0 Database"
        version_patterns = [
            "//h1[contains(text(), 'O*NET')]",
            "//h2[contains(text(), 'O*NET')]",
            "//*[contains(text(), 'O*NET') and contains(text(), 'Database')]"
        ]
        
        for pattern in version_patterns:
            elements = driver.find_elements(by="xpath", value=pattern)
            for element in elements:
                text = element.text
                # Extract version number (e.g., "30.0" from "O*NET 30.0 Database")
                match = re.search(r'O\*NET[®\s]+(\d+\.\d+)', text)
                if match:
                    return match.group(1)
        
        # Fallback: look for any version number pattern
        page_text = driver.find_element(by="tag_name", value="body").text
        match = re.search(r'(\d+\.\d+)\s+Database', page_text)
        if match:
            return match.group(1)
        
        return "latest"  # Default if version cannot be determined
    except Exception as e:
        print(f"Warning: Could not extract version number: {e}")
        return "latest"

def find_excel_download_link(driver):
    """Locate the Excel download link in the 'All Files' section."""
    try:
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Look for the "All Files" section and Excel download link
        # The link should be in a section with "All Files" and contain "Excel"
        xpath_patterns = [
            "//a[contains(text(), 'Excel') and contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'excel')]",
            "//a[contains(@href, '.xlsx') or contains(@href, '.zip')][contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'excel')]",
            "//*[contains(text(), 'All Files')]/following::a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'excel')]",
            "//*[contains(text(), 'Download all')]/following::a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'excel')]",
            "//a[contains(@href, 'Excel')]",
        ]
        
        for xpath in xpath_patterns:
            try:
                elements = driver.find_elements(by="xpath", value=xpath)
                for element in elements:
                    href = element.get_attribute("href")
                    text = element.text.lower()
                    # Check if it's the Excel download link
                    if href and ('excel' in text or 'excel' in href.lower() or '.xlsx' in href.lower() or '.zip' in href.lower()):
                        # Make sure it's a full URL
                        if href.startswith('http'):
                            return href
                        elif href.startswith('/'):
                            # Relative URL, make it absolute using proper URL joining
                            return urljoin(driver.current_url, href)
            except Exception as e:
                continue
        
        # If not found, try to find any link in the "All Files" section
        try:
            all_files_section = driver.find_element(by="xpath", value="//*[contains(text(), 'All Files')]")
            # Find the parent container
            container = all_files_section.find_element(by="xpath", value="./ancestor::*[contains(@class, 'section') or contains(@id, 'section') or name()='section' or name()='div'][1]")
            # Look for Excel link in this container
            excel_links = container.find_elements(by="xpath", value=".//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'excel')]")
            if excel_links:
                href = excel_links[0].get_attribute("href")
                if href:
                    if href.startswith('http'):
                        return href
                    elif href.startswith('/'):
                        # Relative URL, make it absolute using proper URL joining
                        return urljoin(driver.current_url, href)
        except Exception as e:
            pass
        
        raise Exception("Could not find Excel download link")
    except Exception as e:
        print(f"Error finding Excel download link: {e}")
        raise

def download_file(url, filepath, force_download=False):
    """Download a file from the given URL to the specified filepath."""
    # Check if file already exists
    if os.path.exists(filepath) and not force_download:
        file_size = os.path.getsize(filepath)
        print(f"File already exists: {filepath} ({file_size:,} bytes)")
        print("Skipping download. Use force_download=True to re-download.")
        return True
    
    try:
        print(f"Downloading from: {url}")
        # Use tuple timeout: (connect_timeout, read_timeout)
        # connect_timeout: 30s to establish connection
        # read_timeout: None = no timeout for streaming (allows long downloads)
        response = requests.get(url, stream=True, timeout=(30, None))
        response.raise_for_status()
        
        # Get file size if available (with safe parsing)
        try:
            content_length = response.headers.get('content-length', '0')
            total_size = int(content_length) if content_length else 0
        except (ValueError, TypeError):
            total_size = 0
        
        with open(filepath, 'wb') as f:
            if total_size == 0:
                f.write(response.content)
            else:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\rDownload progress: {percent:.1f}% ({downloaded:,}/{total_size:,} bytes)", end='', flush=True)
        
        print(f"\nDownload complete: {filepath}")
        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        if os.path.exists(filepath):
            os.remove(filepath)
        raise

def extract_zip(zip_path, extract_to, force_extract=False):
    """Extract a ZIP file to the specified directory."""
    # Check if extraction directory already has files
    if os.path.exists(extract_to) and not force_extract:
        # Verify it's a directory, not a file
        if os.path.isdir(extract_to):
            existing_files = [f for f in os.listdir(extract_to) if os.path.isfile(os.path.join(extract_to, f))]
            if existing_files:
                print(f"Extraction directory already contains {len(existing_files)} files: {extract_to}")
                print("Skipping extraction. Use force_extract=True to re-extract.")
                return True
        else:
            # If it's a file, remove it and create directory
            print(f"Warning: {extract_to} exists but is a file. Removing and creating directory.")
            os.remove(extract_to)
    
    try:
        print(f"Extracting {zip_path} to {extract_to}...")
        if not os.path.exists(extract_to):
            os.makedirs(extract_to)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Get list of files
            file_list = zip_ref.namelist()
            total_files = len(file_list)
            
            # Extract all files
            for i, member in enumerate(file_list):
                zip_ref.extract(member, extract_to)
                if (i + 1) % 10 == 0 or (i + 1) == total_files:
                    print(f"\rExtraction progress: {i + 1}/{total_files} files", end='', flush=True)
        
        print(f"\nExtraction complete: {extract_to}")
        return True
    except Exception as e:
        print(f"Error extracting ZIP file: {e}")
        raise

def cleanup_files(zip_path, extracted_path, files_to_keep):
    """Delete ZIP file and keep only specified Excel files, deleting all others."""
    try:
        # Delete the ZIP file
        if os.path.exists(zip_path):
            print(f"\nDeleting ZIP file: {zip_path}")
            os.remove(zip_path)
            print("ZIP file deleted successfully.")
        else:
            print(f"\nZIP file not found (may have been deleted already): {zip_path}")
        
        # Find all files in extracted directory (handle nested structure)
        files_to_delete = []
        files_found = []
        
        # Normalize files_to_keep list (case-insensitive comparison)
        files_to_keep_normalized = [f.lower() for f in files_to_keep]
        
        # Walk through extracted directory
        for root, dirs, files in os.walk(extracted_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_name_lower = file.lower()
                
                # Check if this file should be kept
                if file_name_lower in files_to_keep_normalized:
                    files_found.append(file_path)
                else:
                    files_to_delete.append(file_path)
        
        # Report what will be kept
        if files_found:
            print(f"\nKeeping {len(files_found)} file(s):")
            for f in files_found:
                print(f"  - {os.path.basename(f)}")
        
        # Delete unwanted files
        if files_to_delete:
            print(f"\nDeleting {len(files_to_delete)} unwanted file(s)...")
            deleted_count = 0
            for file_path in files_to_delete:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception as e:
                    print(f"  Warning: Could not delete {file_path}: {e}")
            print(f"Deleted {deleted_count} file(s).")
        else:
            print("\nNo files to delete.")
        
        # Clean up empty directories
        print("\nCleaning up empty directories...")
        for root, dirs, files in os.walk(extracted_path, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):  # Directory is empty
                        os.rmdir(dir_path)
                except Exception:
                    pass  # Ignore errors when removing directories
        
        print("Cleanup completed successfully.")
        return True
        
    except Exception as e:
        print(f"Error during cleanup: {e}")
        # Don't raise - cleanup errors shouldn't fail the whole process
        return False

def main():
    """Main function to orchestrate the O*NET database scraping process."""
    # Setup paths
    app_path = get_app_path()
    output_path = os.path.join(app_path, 'output')
    extracted_path = os.path.join(output_path, 'extracted')
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    website = "https://www.onetcenter.org/database.html"
    
    print("Initializing Chrome driver...")
    # Chrome driver setup
    options = Options()
    # Uncomment the line below to run in headless mode
    # options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
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
            files_to_keep = [
                "Occupation Data.xlsx",
                "Interests.xlsx",
                "Skills.xlsx",
                "Technology Skills.xlsx",
                "Knowledge.xlsx",
                "Job Zones.xlsx",
                "Work Values.xlsx"
            ]
            cleanup_files(zip_path, extracted_path, files_to_keep)
        
        print("\n" + "="*50)
        print("O*NET Database scraping completed successfully!")
        print(f"Extracted to: {extracted_path}")
        print(f"Kept {len(files_to_keep)} essential Excel files")
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

