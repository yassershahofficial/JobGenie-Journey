"""File cleanup utilities for the O*NET database scraper."""

import os


def cleanup_files(zip_path, extracted_path, files_to_keep):
    """Delete ZIP file and keep only specified Excel files, deleting all others."""
    try:
        # Delete the ZIP file
        if os.path.exists(zip_path):
            print(f"\nDeleting ZIP file: {zip_path}")
            os.remove(zip_path)
            print("ZIP file deleted successfully.")
        else:
            print(f"\nZIP file not found (may have been deleted already): {zip_path}")
        
        # Find all files in extracted directory (handle nested structure)
        files_to_delete = []
        files_found = []
        
        # Normalize files_to_keep list (case-insensitive comparison)
        files_to_keep_normalized = [f.lower() for f in files_to_keep]
        
        # Walk through extracted directory
        for root, dirs, files in os.walk(extracted_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_name_lower = file.lower()
                
                # Check if this file should be kept
                if file_name_lower in files_to_keep_normalized:
                    files_found.append(file_path)
                else:
                    files_to_delete.append(file_path)
        
        # Report what will be kept
        if files_found:
            print(f"\nKeeping {len(files_found)} file(s):")
            for f in files_found:
                print(f"  - {os.path.basename(f)}")
        
        # Delete unwanted files
        if files_to_delete:
            print(f"\nDeleting {len(files_to_delete)} unwanted file(s)...")
            deleted_count = 0
            for file_path in files_to_delete:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception as e:
                    print(f"  Warning: Could not delete {file_path}: {e}")
            print(f"Deleted {deleted_count} file(s).")
        else:
            print("\nNo files to delete.")
        
        # Clean up empty directories
        print("\nCleaning up empty directories...")
        for root, dirs, files in os.walk(extracted_path, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):  # Directory is empty
                        os.rmdir(dir_path)
                except Exception:
                    pass  # Ignore errors when removing directories
        
        print("Cleanup completed successfully.")
        return True
        
    except Exception as e:
        print(f"Error during cleanup: {e}")
        # Don't raise - cleanup errors shouldn't fail the whole process
        return False

