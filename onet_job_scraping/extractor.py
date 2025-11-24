"""ZIP extraction utilities for the O*NET database scraper."""

import os
import zipfile


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

