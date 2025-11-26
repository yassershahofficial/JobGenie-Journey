# Project Setup Guide

## Virtual Environment

This project uses a **shared virtual environment** located at the project root (`venv/`). Both `newest_job_scraping` and `onet_job_scraping` folders use this same environment to avoid dependency conflicts.

## Setup Instructions

### 1. Activate the Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 2. Install Dependencies

If dependencies are not already installed:
```bash
pip install -r requirements.txt
```

### 3. Running Scripts

Once the virtual environment is activated, you can run scripts from any folder:

**Run newest_job_scraping:**
```bash
cd newest_job_scraping
python web_scrape.py
```

**Run onet_job_scraping:**

The O*NET scraper has been modularized and can be run in multiple ways:

**Method 1: Direct Script Execution (Recommended)**
```bash
cd onet_job_scraping
python scrape_onet_database.py
```

**Method 2: Module Execution**
```bash
# From project root
python -m onet_job_scraping.main

# Or from onet_job_scraping directory
cd onet_job_scraping
python -m main
```

**Method 3: Programmatic Usage**
```python
from onet_job_scraping import main
main()
```

All methods produce identical results. Method 1 is recommended for simplicity and backward compatibility.

## Project Structure

```
v0.2/
├── venv/                    # Shared virtual environment
├── requirements.txt         # All project dependencies
├── SETUP.md                 # This setup guide
├── .gitignore               # Git ignore rules
├── newest_job_scraping/     # Job scraping scripts
│   ├── web_scrape.py
│   └── output/
└── onet_job_scraping/       # O*NET database scraper (modular)
    ├── __init__.py
    ├── config.py            # Configuration constants
    ├── main.py              # Main orchestration
    ├── downloader.py        # File downloading
    ├── extractor.py         # ZIP extraction
    ├── cleanup.py           # File cleanup
    ├── scrape_onet_database.py  # Backward compatibility wrapper
    ├── README.md            # Detailed module documentation
    ├── scraper/             # Scraping modules
    │   ├── __init__.py
    │   ├── version_extractor.py
    │   └── link_finder.py
    ├── utils/               # Utility modules
    │   ├── __init__.py
    │   ├── paths.py
    │   └── selenium_helpers.py
    └── output/              # Extracted Excel files
        └── extracted/
```

## Notes

- The virtual environment is shared to ensure consistent dependency versions across all scripts
- Output files are stored in each project's respective `output/` folder
- The `venv/` folder is excluded from version control (see `.gitignore`)
- The `onet_job_scraping` module uses a modular architecture for better maintainability and testability
- For detailed documentation on the O*NET scraper, see `onet_job_scraping/README.md`

