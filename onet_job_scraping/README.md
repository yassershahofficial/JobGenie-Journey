# O*NET Database Scraper

A Python module for automatically scraping and downloading the latest O*NET database Excel files from the official O*NET Resource Center website. The module handles version detection, file downloading, extraction, and cleanup to provide only the essential Excel files needed for analysis.

## Description

This module automates the process of fetching the latest O*NET (Occupational Information Network) database release from `https://www.onetcenter.org/database.html`. It uses Selenium for web scraping to locate the download link and Requests for efficient file downloading. The scraper automatically:

- Detects the latest database version from the O*NET website
- Downloads the complete Excel database ZIP file (~45 MB)
- Extracts all files from the archive
- Cleans up by keeping only 7 essential Excel files and removing all others
- Deletes the ZIP file after successful extraction
- Handles errors gracefully with detailed logging

**Key Features:**
- Automatic version detection and validation
- Smart caching (skips download/extraction if files already exist)
- Headless browser mode for server environments
- Progress tracking with MB display
- Robust error handling and recovery
- Support for both script and executable modes (PyInstaller compatible)
- Modular architecture for maintainability, testability, and collaboration

## Installation

### Prerequisites

- Python 3.10 or higher
- Google Chrome browser (for Selenium WebDriver)
- Internet connection

### Dependencies

Install required packages using pip:

```bash
pip install -r requirements.txt
```

**Core Dependencies:**
- `selenium==4.38.0` - Web automation and scraping
- `webdriver-manager==4.0.2` - Automatic ChromeDriver management
- `requests==2.32.5` - HTTP library for file downloads
- `pandas==2.3.3` - Data processing (optional, for future enhancements)

**Note:** ChromeDriver is automatically downloaded and managed by `webdriver-manager`. No manual installation required.

## Usage

### Method 1: Direct Script Execution (Recommended)

Run the scraper directly from the command line:

```bash
cd onet_job_scraping
python scrape_onet_database.py
```

This method maintains backward compatibility and is the simplest way to run the scraper.

### Method 2: Module Execution

Run as a Python module from the project root:

```bash
# From project root
python -m onet_job_scraping.main

# Or from onet_job_scraping directory
cd onet_job_scraping
python -m main
```

### Method 3: Programmatic Usage

Import and use in your Python code:

```python
# Option A: Import from the wrapper (backward compatible)
from onet_job_scraping.scrape_onet_database import main
main()

# Option B: Import from the main module
from onet_job_scraping.main import main
main()

# Option C: Import from package
from onet_job_scraping import main
main()
```

**Note:** All methods produce identical results. Method 1 is recommended for simplicity and backward compatibility.

### Example Output

```
Initializing Chrome driver...
Navigating to https://www.onetcenter.org/database.html...
Extracting database version...
Found O*NET Database version: 30.0
Locating Excel download link...
Found download URL: https://www.onetcenter.org/dl_files/database/db_30_0_excel.zip
Downloading from: https://www.onetcenter.org/dl_files/database/db_30_0_excel.zip
Download progress: 100.0% (45.58/45.58 MB)
Download complete: E:\...\onet_database_30.0.zip
Extracting E:\...\onet_database_30.0.zip to E:\...\extracted...
Extraction progress: 42/42 files
Extraction complete: E:\...\extracted
Deleting ZIP file: E:\...\onet_database_30.0.zip
ZIP file deleted successfully.
Keeping 7 file(s):
  - Interests.xlsx
  - Job Zones.xlsx
  - Knowledge.xlsx
  - Occupation Data.xlsx
  - Skills.xlsx
  - Technology Skills.xlsx
  - Work Values.xlsx
Deleting 34 unwanted file(s)...
Deleted 34 file(s).
Cleaning up empty directories...
Cleanup completed successfully.
```

## Configuration

### Output Paths

The module automatically creates output directories relative to the script location:

- **Script mode**: `onet_job_scraping/output/`
- **Executable mode**: `{executable_directory}/output/`

Output structure:
```
onet_job_scraping/
├── output/
│   └── extracted/
│       ├── Occupation Data.xlsx
│       ├── Interests.xlsx
│       ├── Skills.xlsx
│       ├── Technology Skills.xlsx
│       ├── Knowledge.xlsx
│       ├── Job Zones.xlsx
│       └── Work Values.xlsx
```

### Browser Mode

The scraper runs in **headless mode** by default (no visible browser window). To disable headless mode for debugging, modify `utils/selenium_helpers.py` in the `create_driver()` function:

```python
# In utils/selenium_helpers.py, modify create_driver():
def create_driver(headless=True):
    # ...
    if headless:
        # Comment out this line to see the browser:
        # options.add_argument("--headless=new")
```

### Force Options

The module supports force flags for re-downloading or re-extracting:

**Force Download:**
```python
download_file(url, filepath, force_download=True)
```

**Force Extract:**
```python
extract_zip(zip_path, extract_to, force_extract=True)
```

By default, the module skips download/extraction if files already exist to save time and bandwidth.

## Output

### Retained Files

After extraction and cleanup, only the following 7 essential Excel files are retained:

1. **Occupation Data.xlsx** - Core occupation information and metadata
2. **Interests.xlsx** - Occupational interest profiles (RIASEC)
3. **Skills.xlsx** - Required skills for each occupation
4. **Technology Skills.xlsx** - Technology and software skills
5. **Knowledge.xlsx** - Knowledge requirements by domain
6. **Job Zones.xlsx** - Education and experience requirements
7. **Work Values.xlsx** - Work value preferences

All other files (reference tables, crosswalks, metadata files, etc.) are automatically deleted to keep the output minimal and focused.

### File Naming

Downloaded ZIP files are named with the detected version:
- Format: `onet_database_{version}.zip`
- Example: `onet_database_30.0.zip`

If version detection fails, a timestamp fallback is used:
- Format: `onet_database_{YYYYMMDD_HHMMSS}.zip`

## Error Handling & Logging

### Exception Handling

The module implements comprehensive error handling:

- **Network errors**: Connection timeouts are handled with unlimited read timeout for large file downloads
- **Version detection failures**: Falls back to timestamp-based naming
- **Download failures**: Partial downloads are automatically cleaned up
- **Extraction failures**: Errors are logged and raised, preventing cleanup of ZIP file
- **Browser cleanup**: Wrapped in try-except to ensure cleanup completes even if browser crashes

### Logging

All operations print progress and status messages to stdout:

- **Progress indicators**: Download progress shown in MB with percentage
- **Status messages**: Each major step (download, extraction, cleanup) reports completion
- **Error messages**: Detailed error information with context
- **Warnings**: Non-critical issues (e.g., version detection fallback)

### Error Recovery

- Failed downloads remove partial files automatically
- Extraction failures preserve the ZIP file for manual recovery
- Cleanup errors don't fail the entire process (logged but non-fatal)
- Browser cleanup always attempts to close, even after errors

## Module Structure

The scraper is organized into a modular architecture for better maintainability and testability:

```
onet_job_scraping/
├── __init__.py                 # Package exports
├── config.py                   # Configuration constants
├── utils/
│   ├── __init__.py
│   ├── paths.py                # Path utilities
│   └── selenium_helpers.py     # Selenium utilities
├── scraper/
│   ├── __init__.py
│   ├── version_extractor.py    # Version detection
│   └── link_finder.py          # Download link finding
├── downloader.py               # File downloading
├── extractor.py                 # ZIP extraction
├── cleanup.py                   # File cleanup
├── main.py                      # Main orchestration
└── scrape_onet_database.py     # Backward compatibility wrapper
```

## Functions Overview

### Core Functions

| Function | Module | Description |
|----------|--------|-------------|
| `get_app_path()` | `utils/paths.py` | Returns the application directory path, supporting both script and PyInstaller executable modes |
| `get_latest_version(driver)` | `scraper/version_extractor.py` | Extracts the O*NET database version number from the webpage using regex pattern matching |
| `find_excel_download_link(driver)` | `scraper/link_finder.py` | Locates the Excel download link in the "All Files" section using multiple XPath fallback strategies |
| `download_file(url, filepath, force_download=False)` | `downloader.py` | Downloads a file with progress tracking (MB display), skips if exists unless `force_download=True` |
| `extract_zip(zip_path, extract_to, force_extract=False)` | `extractor.py` | Extracts ZIP archive with progress tracking, skips if already extracted unless `force_extract=True` |
| `cleanup_files(zip_path, extracted_path, files_to_keep)` | `cleanup.py` | Deletes ZIP file and removes all extracted files except those in `files_to_keep` list |
| `main()` | `main.py` | Orchestrates the complete scraping workflow: navigation, version detection, download, extraction, and cleanup |

### Helper Functions

| Function | Module | Description |
|----------|--------|-------------|
| `find_any_element(element, xpaths)` | `utils/selenium_helpers.py` | Utility to find the first element matching any of the provided XPath expressions |
| `create_driver(headless=True)` | `utils/selenium_helpers.py` | Creates and configures Chrome WebDriver with appropriate options |

## Technical Details

### Version Detection

The module uses multiple strategies to detect the database version:

1. Searches for version text in H1/H2 headings containing "O*NET"
2. Searches page body for version pattern: `(\d+\.\d+)\s+Database`
3. Falls back to timestamp if no version found

Version format validation ensures only valid versions (e.g., "30.0") are used in filenames.

### Download Strategy

- **Streaming download**: Uses `requests` with `stream=True` for memory efficiency
- **Timeout handling**: 30-second connection timeout, unlimited read timeout for large files
- **Progress tracking**: Real-time MB progress with percentage completion
- **Resume capability**: Not currently implemented (would require Range header support)

### URL Resolution

Relative URLs are properly resolved using `urllib.parse.urljoin()` to handle edge cases in URL construction.

## Contributing / Notes

### For Developers

**Extending the Module:**

1. **Adding more files to keep**: Modify the `FILES_TO_KEEP` list in `config.py`
2. **Changing output location**: Modify `OUTPUT_DIR_NAME` and `EXTRACTED_DIR_NAME` in `config.py`, or update path logic in `main.py`
3. **Custom cleanup logic**: Extend `cleanup_files()` function in `cleanup.py` with additional filtering criteria
4. **Adding retry logic**: Wrap `download_file()` calls in `downloader.py` with retry decorator for network resilience
5. **Modifying browser behavior**: Update `create_driver()` in `utils/selenium_helpers.py`
6. **Changing version detection**: Modify `get_latest_version()` in `scraper/version_extractor.py`

**Code Structure:**
- Modular architecture with clear separation of concerns
- Each module has a single responsibility
- Functions can be imported individually from their respective modules
- Error handling is consistent across all functions
- Path handling supports both development and production (executable) modes
- Backward compatibility maintained through `scrape_onet_database.py` wrapper

**Testing Considerations:**
- Test with slow network connections (timeout handling)
- Test with missing Chrome browser (WebDriver errors)
- Test with invalid version formats (fallback behavior)
- Test cleanup with locked files (permission errors)

**Performance Notes:**
- Headless mode reduces resource usage
- File existence checks prevent redundant downloads
- Streaming downloads prevent memory issues with large files
- Case-insensitive file matching ensures cross-platform compatibility

## License

[Add your license information here]

---

**Data Source:** [O*NET Resource Center](https://www.onetcenter.org/) - U.S. Department of Labor, Employment and Training Administration

**Note:** This module is for educational and research purposes. Ensure compliance with O*NET's [license terms](https://www.onetcenter.org/database.html) when using the scraped data.

