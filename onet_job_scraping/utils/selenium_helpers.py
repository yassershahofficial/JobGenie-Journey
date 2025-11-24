"""Selenium helper utilities for the O*NET database scraper."""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def find_any_element(element, xpaths):
    """Find the first element that matches any of the given XPath expressions."""
    for xpath in xpaths:
        elements = element.find_elements(by="xpath", value=xpath)
        if elements:
            return elements[0]
    return None


def create_driver(headless=True):
    """Create and configure Chrome WebDriver."""
    print("Initializing Chrome driver...")
    options = Options()
    if headless:
        # Run in headless mode
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

