"""File downloading utilities for the O*NET database scraper."""

import os
import requests


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
                            downloaded_mb = downloaded / (1024 * 1024)
                            total_mb = total_size / (1024 * 1024)
                            print(f"\rDownload progress: {percent:.1f}% ({downloaded_mb:.2f}/{total_mb:.2f} MB)", end='', flush=True)
        
        print(f"\nDownload complete: {filepath}")
        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        if os.path.exists(filepath):
            os.remove(filepath)
        raise

