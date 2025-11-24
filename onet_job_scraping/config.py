"""Configuration constants for the O*NET database scraper."""

# List of Excel files to retain after extraction
FILES_TO_KEEP = [
    "Occupation Data.xlsx",
    "Interests.xlsx",
    "Skills.xlsx",
    "Technology Skills.xlsx",
    "Knowledge.xlsx",
    "Job Zones.xlsx",
    "Work Values.xlsx"
]

# O*NET database URL
ONET_DATABASE_URL = "https://www.onetcenter.org/database.html"

# Output directory names
OUTPUT_DIR_NAME = "output"
EXTRACTED_DIR_NAME = "extracted"

