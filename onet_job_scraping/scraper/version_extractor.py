"""Version extraction utilities for the O*NET database scraper."""

import re


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

