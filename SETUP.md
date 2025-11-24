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
```bash
cd onet_job_scraping
python scrape_onet_database.py
```

## Project Structure

```
v0.2/
├── venv/                    # Shared virtual environment
├── requirements.txt         # All project dependencies
├── newest_job_scraping/     # Job scraping scripts
│   ├── web_scrape.py
│   └── output/
└── onet_job_scraping/       # O*NET database scraper
    ├── scrape_onet_database.py
    └── output/
```

## Notes

- The virtual environment is shared to ensure consistent dependency versions across all scripts
- Output files are stored in each project's respective `output/` folder
- The `venv/` folder is excluded from version control (see `.gitignore`)

