"""Link finding utilities for the O*NET database scraper."""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin


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

