# JobStreet Job Scraper

A simple web scraper that extracts job listing links from JobStreet Malaysia using Selenium WebDriver.

## Overview

This module scrapes job listings from the JobStreet website (`https://my.jobstreet.com/jobs`) and extracts article links for further processing. It uses Selenium with Chrome WebDriver to navigate the website and extract job listing information.

## Features

- Automated web scraping using Selenium
- Extracts job article links from JobStreet
- Saves results to CSV format
- Headless mode support (commented out by default)
- Automatic ChromeDriver management via `webdriver-manager`

## Prerequisites

- Python 3.10+
- Google Chrome browser
- Internet connection

## Installation

Install required packages:

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies (if not already installed)
pip install selenium webdriver-manager pandas
```

**Core Dependencies:**
- `selenium` - Web automation and scraping
- `webdriver-manager` - Automatic ChromeDriver management
- `pandas` - Data processing and CSV export

**Note:** ChromeDriver is automatically downloaded and managed by `webdriver-manager`. No manual installation required.

## Usage

### Basic Usage

Run the scraper directly:

```bash
cd newest_job_scraping
python web_scrape.py
```

### Output

The scraper generates `output/all_articles.csv` with the following structure:

```csv
no,link
1,https://my.jobstreet.com/jobs/...
2,https://my.jobstreet.com/jobs/...
3,https://my.jobstreet.com/jobs/...
```

## Configuration

### Headless Mode

By default, the browser runs in visible mode. To enable headless mode (no visible browser window), uncomment the headless option in `web_scrape.py`:

```python
# In web_scrape.py, line 31:
options.add_argument("--headless=new")  # Uncomment this line
```

### Target Website

Change the target website by modifying the `website` variable:

```python
website = "https://my.jobstreet.com/jobs"  # Modify as needed
```

### Output Path

The output path is automatically set relative to the script location:

```python
app_path = get_app_path()  # Gets script directory or executable directory
output_path = os.path.join(app_path, 'output')
```

## File Structure

```
newest_job_scraping/
├── web_scrape.py           # Main scraper script
├── output/
│   └── all_articles.csv   # Generated output file
└── README.md              # This file
```

## How It Works

1. **Initialize ChromeDriver**: Sets up Selenium WebDriver with Chrome
2. **Navigate to Website**: Opens JobStreet jobs page
3. **Find Job Articles**: Locates all `<article>` elements on the page
4. **Extract Links**: Extracts href attributes from article links
5. **Save to CSV**: Writes job links to `output/all_articles.csv`

## Code Structure

### Key Functions

- `get_app_path()`: Returns the application directory path, supporting both script and PyInstaller executable modes
- `find_any_element(element, xpaths)`: Utility to find the first element matching any of the provided XPath expressions

### Main Process

```python
# Setup WebDriver
driver = webdriver.Chrome(service=service, options=options)
driver.get(website)

# Find job articles
jobs_links = driver.find_elements(by="xpath", value='//article')

# Extract links
for job_link in jobs_links:
    link = find_any_element(job_link, ['./div/a']).get_attribute("href")
    dict_jobs_links.append({'no': num+1, 'link': link})

# Save to CSV
df_jobs_links.to_csv('output/all_articles.csv', index=False)
```

## Limitations

- **Single Page**: Currently scrapes only the first page of results
- **No Pagination**: Does not automatically navigate through multiple pages
- **Basic Extraction**: Only extracts links, not full job details
- **Rate Limiting**: No built-in rate limiting or delays

## Future Enhancements

Potential improvements:

1. **Pagination Support**: Navigate through multiple pages of results
2. **Full Job Details**: Extract complete job information (title, company, description, etc.)
3. **Rate Limiting**: Add delays to avoid overwhelming the server
4. **Error Handling**: Better error handling for network issues or element not found
5. **Data Validation**: Validate extracted links before saving
6. **Resume Capability**: Resume scraping from last saved position
7. **Filtering**: Filter jobs by keywords, location, salary, etc.

## Troubleshooting

### ChromeDriver Issues

**Error**: `selenium.common.exceptions.WebDriverException`

**Solution**: Ensure Chrome browser is installed and up to date. `webdriver-manager` should automatically handle ChromeDriver, but you can manually update Chrome if needed.

### Element Not Found

**Error**: `NoSuchElementException` or empty results

**Possible Causes**:
- Website structure changed
- Network connection issues
- Website blocking automated access

**Solution**: 
- Check if the website is accessible
- Verify XPath selectors match current website structure
- Consider adding delays or using different selectors

### Output Directory Not Created

**Error**: `FileNotFoundError` when saving CSV

**Solution**: The script automatically creates the output directory, but ensure write permissions are available.

### Headless Mode Issues

**Error**: Elements not found in headless mode

**Solution**: Some websites behave differently in headless mode. Try running without headless mode first to debug, then re-enable headless once working.

## Notes

- The scraper uses XPath `'//article'` to find job listings, which may need adjustment if JobStreet changes their HTML structure
- The script includes a commented-out input prompt at the end for debugging: `# input("Press Enter Key to close the browser...")`
- There's a typo in the code (`dict_articles` instead of `dict_jobs_links` on line 47) that should be fixed

## Integration

This scraper is part of a larger job matching system. The extracted links can be used for:
- Further job detail extraction
- Job description analysis
- Integration with the Logic Engine matching system
- Real-time job market analysis

## License

Part of the Final Year Project.

