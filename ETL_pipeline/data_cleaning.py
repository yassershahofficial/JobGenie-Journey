"""
ETL Pipeline - Data Cleaning and Filtering Stage

This module performs data cleaning and filtering on O*NET database Excel files.
It processes five files:
1. Job Zones - Creates whitelist of valid O*NET-SOC codes (zones 3, 4) - for fresh graduates and interns
2. Occupation Data - Filters and extracts Title and Description for whitelisted jobs
3. Interests - Filters RIASEC interest data for whitelisted jobs (Scale ID="OI")
4. Knowledge - Filters essential knowledge domains for degree/major matching (Scale ID="IM", Data Value > 3.0)
5. Technology Skills - Extracts hard skills keywords for resume/CV matching

All filtered data is kept in memory as DataFrames for further processing.
"""

import os
import pandas as pd
from pathlib import Path


# ============================================================================
# CONFIGURATION
# ============================================================================

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent
ONET_EXTRACTED_PATH = PROJECT_ROOT / "onet_job_scraping" / "output" / "extracted"

# File names
JOB_ZONES_FILE = "Job Zones.xlsx"
OCCUPATION_DATA_FILE = "Occupation Data.xlsx"
INTERESTS_FILE = "Interests.xlsx"
KNOWLEDGE_FILE = "Knowledge.xlsx"
TECHNOLOGY_SKILLS_FILE = "Technology Skills.xlsx"

# Filter constants
VALID_JOB_ZONES = [3, 4]  # Target fresh graduates and interns (removed zone 5)
OCCUPATIONAL_INTEREST_SCALE = "OI"  # "OI" = Occupational Interest, exclude "IH" = Highpoint
KNOWLEDGE_SCALE_ID = "IM"  # "IM" = Importance scale for Knowledge
KNOWLEDGE_IMPORTANCE_THRESHOLD = 3.0  # Threshold for essential knowledge (Data Value > 3.0)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_section_header(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def find_extraction_folder():
    """
    Find the latest extraction folder in onet_job_scraping/output/extracted/.
    Usually named like 'db_30_0_excel' or similar.
    
    Returns:
        Path to the extraction folder
        
    Raises:
        FileNotFoundError: If extraction folder or base path doesn't exist
    """
    if not ONET_EXTRACTED_PATH.exists():
        raise FileNotFoundError(
            f"O*NET extraction base path not found: {ONET_EXTRACTED_PATH}\n"
            "Please run the onet_job_scraping scraper first."
        )
    
    # Look for subdirectories (extraction folders)
    subdirs = [d for d in ONET_EXTRACTED_PATH.iterdir() if d.is_dir()]
    
    if not subdirs:
        raise FileNotFoundError(
            f"No extraction folders found in: {ONET_EXTRACTED_PATH}\n"
            "Please run the onet_job_scraping scraper first."
        )
    
    # Return the most recently modified subdirectory
    latest_folder = sorted(subdirs, key=lambda x: x.stat().st_mtime, reverse=True)[0]
    
    return latest_folder


def get_file_path(filename):
    """
    Get the full path to a file in the latest extraction folder.
    
    Args:
        filename: Name of the Excel file (e.g., "Job Zones.xlsx")
        
    Returns:
        Path object to the file
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    extraction_folder = find_extraction_folder()
    file_path = extraction_folder / filename
    
    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}\n"
            f"Expected in: {extraction_folder}\n"
            f"Available files: {[f.name for f in extraction_folder.iterdir() if f.is_file()]}"
        )
    
    return file_path


def detect_column(df, search_terms, description="column"):
    """
    Detect a column name in DataFrame using flexible matching.
    
    Args:
        df: pandas DataFrame
        search_terms: List of search terms (case-insensitive, partial match)
        description: Description of the column for error messages
        
    Returns:
        Column name (string) if found
        
    Raises:
        ValueError: If column cannot be found
    """
    df_columns = [str(col).strip() for col in df.columns]
    
    for term in search_terms:
        term_lower = term.lower()
        # Try exact match (case-insensitive)
        for col in df_columns:
            if col.lower() == term_lower:
                return col
        # Try partial match
        for col in df_columns:
            if term_lower in col.lower() or col.lower() in term_lower:
                return col
    
    raise ValueError(
        f"Could not find {description} column.\n"
        f"Searched for: {search_terms}\n"
        f"Available columns: {df_columns}"
    )


# ============================================================================
# STEP 1: GATEKEEPER - JOB ZONES PROCESSING
# ============================================================================

def process_job_zones():
    """
    Process Job Zones file to create whitelist of valid O*NET-SOC codes.
    
    Filters jobs where Job Zone is 3 or 4 (targeting fresh graduates and interns).
    
    Returns:
        List of valid O*NET-SOC codes (whitelist)
    """
    print_section_header("STEP 1: Processing Job Zones (Gatekeeper)")
    
    # Get file path
    file_path = get_file_path(JOB_ZONES_FILE)
    print(f"Reading: {file_path}")
    
    # Read Excel file
    df = pd.read_excel(file_path)
    
    print(f"Total rows in Job Zones: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    # Detect column names
    job_zone_col = detect_column(
        df,
        ["Job Zone", "Zone", "JobZone", "Job_Zone"],
        "Job Zone"
    )
    
    soc_code_col = detect_column(
        df,
        ["O*NET-SOC Code", "SOC Code", "Code", "ONET_SOC_CODE", "O*NET-SOC"],
        "O*NET-SOC Code"
    )
    
    print(f"Using Job Zone column: '{job_zone_col}'")
    print(f"Using SOC Code column: '{soc_code_col}'")
    
    # Show unique job zones before filtering
    unique_zones = sorted(df[job_zone_col].dropna().unique())
    print(f"Unique Job Zones found: {unique_zones}")
    
    # Filter by valid job zones
    print(f"\nFiltering for Job Zones: {VALID_JOB_ZONES}")
    filtered_df = df[df[job_zone_col].isin(VALID_JOB_ZONES)].copy()
    
    print(f"Rows before filtering: {len(df)}")
    print(f"Rows after filtering: {len(filtered_df)}")
    print(f"Rows removed: {len(df) - len(filtered_df)}")
    
    # Extract unique O*NET-SOC codes (whitelist)
    whitelist = filtered_df[soc_code_col].dropna().unique().tolist()
    whitelist = sorted([str(code).strip() for code in whitelist])
    
    # Create job_zones_df with O*NET-SOC Code and Job Zone for transformation stage
    job_zones_df = filtered_df[[soc_code_col, job_zone_col]].copy()
    job_zones_df.columns = ["O*NET-SOC Code", "Job Zone"]
    # Remove duplicates (keep first occurrence per O*NET-SOC Code)
    job_zones_df = job_zones_df.drop_duplicates(subset=["O*NET-SOC Code"], keep='first')
    
    print(f"\n[OK] Whitelist created: {len(whitelist)} valid O*NET-SOC codes")
    print(f"[OK] Job Zones DataFrame created: {len(job_zones_df)} job zone mappings")
    print(f"Sample codes (first 5): {whitelist[:5]}")
    
    return whitelist, job_zones_df


# ============================================================================
# STEP 2: IDENTITY - OCCUPATION DATA PROCESSING
# ============================================================================

def process_occupation_data(whitelist):
    """
    Process Occupation Data file to get job titles and descriptions.
    
    Filters rows where O*NET-SOC Code is in the whitelist.
    Collects Title and Description columns.
    
    Args:
        whitelist: List of valid O*NET-SOC codes
        
    Returns:
        DataFrame with O*NET-SOC Code, Title, Description columns
    """
    print_section_header("STEP 2: Processing Occupation Data (Identity)")
    
    # Get file path
    file_path = get_file_path(OCCUPATION_DATA_FILE)
    print(f"Reading: {file_path}")
    
    # Read Excel file
    df = pd.read_excel(file_path)
    
    print(f"Total rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    # Detect required columns
    soc_code_col = detect_column(
        df,
        ["O*NET-SOC Code", "SOC Code", "Code", "ONET_SOC_CODE", "O*NET-SOC"],
        "O*NET-SOC Code"
    )
    
    title_col = detect_column(
        df,
        ["Title", "Job Title", "Occupation Title", "Title Name"],
        "Title"
    )
    
    desc_col = detect_column(
        df,
        ["Description", "Desc", "Job Description", "Description Text"],
        "Description"
    )
    
    print(f"Using SOC Code column: '{soc_code_col}'")
    print(f"Using Title column: '{title_col}'")
    print(f"Using Description column: '{desc_col}'")
    
    # Filter by whitelist
    print(f"\nFiltering by whitelist ({len(whitelist)} codes)...")
    filtered_df = df[df[soc_code_col].isin(whitelist)].copy()
    
    print(f"Rows before filtering: {len(df)}")
    print(f"Rows after filtering: {len(filtered_df)}")
    print(f"Rows removed: {len(df) - len(filtered_df)}")
    
    # Select only required columns
    result_df = filtered_df[[soc_code_col, title_col, desc_col]].copy()
    result_df.columns = ["O*NET-SOC Code", "Title", "Description"]
    
    # Remove duplicates (keep first occurrence per O*NET-SOC Code)
    duplicates_before = len(result_df)
    result_df = result_df.drop_duplicates(subset=["O*NET-SOC Code"], keep='first')
    duplicates_removed = duplicates_before - len(result_df)
    
    if duplicates_removed > 0:
        print(f"Removed {duplicates_removed} duplicate entries")
    
    print(f"\n[OK] Processed {len(result_df)} unique occupations")
    
    # Show sample
    print(f"\nSample occupations (first 3):")
    for idx, row in result_df.head(3).iterrows():
        desc_preview = row['Description'][:60] + "..." if len(str(row['Description'])) > 60 else row['Description']
        print(f"  - {row['Title']}: {desc_preview}")
    
    return result_df


# ============================================================================
# STEP 3: PERSONALITY - INTERESTS PROCESSING
# ============================================================================

def process_interests(whitelist):
    """
    Process Interests file to extract RIASEC interest data.
    
    Filters rows where:
    - O*NET-SOC Code is in whitelist
    - Scale ID = "OI" (Occupational Interest, exclude "IH" = Highpoint)
    
    Args:
        whitelist: List of valid O*NET-SOC codes
        
    Returns:
        DataFrame with O*NET-SOC Code, Element Name, Data Value columns
    """
    print_section_header("STEP 3: Processing Interests (Personality - RIASEC)")
    
    # Get file path
    file_path = get_file_path(INTERESTS_FILE)
    print(f"Reading: {file_path}")
    
    # Read Excel file
    df = pd.read_excel(file_path)
    
    print(f"Total rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    # Detect required columns
    soc_code_col = detect_column(
        df,
        ["O*NET-SOC Code", "SOC Code", "Code", "ONET_SOC_CODE", "O*NET-SOC"],
        "O*NET-SOC Code"
    )
    
    scale_id_col = detect_column(
        df,
        ["Scale ID", "ScaleID", "Scale", "Scale_ID"],
        "Scale ID"
    )
    
    element_name_col = detect_column(
        df,
        ["Element Name", "ElementName", "Element", "Element_Name", "Interest"],
        "Element Name"
    )
    
    data_value_col = detect_column(
        df,
        ["Data Value", "DataValue", "Value", "Data_Value", "Score"],
        "Data Value"
    )
    
    print(f"Using SOC Code column: '{soc_code_col}'")
    print(f"Using Scale ID column: '{scale_id_col}'")
    print(f"Using Element Name column: '{element_name_col}'")
    print(f"Using Data Value column: '{data_value_col}'")
    
    # Filter by whitelist
    print(f"\nFiltering by whitelist ({len(whitelist)} codes)...")
    filtered_df = df[df[soc_code_col].isin(whitelist)].copy()
    
    print(f"Rows before whitelist filter: {len(df)}")
    print(f"Rows after whitelist filter: {len(filtered_df)}")
    print(f"Rows removed by whitelist: {len(df) - len(filtered_df)}")
    
    # Show unique Scale IDs before filtering
    unique_scale_ids = sorted(filtered_df[scale_id_col].dropna().unique())
    print(f"\nUnique Scale IDs found: {unique_scale_ids}")
    
    # Filter by Scale ID = "OI"
    print(f"Filtering by Scale ID = '{OCCUPATIONAL_INTEREST_SCALE}'...")
    filtered_df = filtered_df[filtered_df[scale_id_col] == OCCUPATIONAL_INTEREST_SCALE].copy()
    
    print(f"Rows after Scale ID filter: {len(filtered_df)}")
    print(f"Rows removed by Scale ID filter: {len(df[df[soc_code_col].isin(whitelist)]) - len(filtered_df)}")
    
    # Show unique interest elements (should be RIASEC categories)
    unique_elements = sorted(filtered_df[element_name_col].dropna().unique())
    print(f"\nUnique interest elements found: {unique_elements}")
    
    # Select required columns
    result_df = filtered_df[[soc_code_col, element_name_col, data_value_col]].copy()
    result_df.columns = ["O*NET-SOC Code", "Element Name", "Data Value"]
    
    # Show statistics about data values
    print(f"\nData Value statistics:")
    print(f"  Min: {result_df['Data Value'].min()}")
    print(f"  Max: {result_df['Data Value'].max()}")
    print(f"  Mean: {result_df['Data Value'].mean():.2f}")
    
    # Count unique jobs in filtered data
    unique_jobs = result_df["O*NET-SOC Code"].nunique()
    print(f"\n[OK] Processed interests for {unique_jobs} unique occupations")
    print(f"[OK] Total interest records: {len(result_df)}")
    
    # Show sample
    print(f"\nSample interest data (first 5 rows):")
    for idx, row in result_df.head(5).iterrows():
        print(f"  {row['O*NET-SOC Code']}: {row['Element Name']} = {row['Data Value']}")
    
    return result_df


# ============================================================================
# STEP 4: DEGREE MATCHER - KNOWLEDGE PROCESSING
# ============================================================================

def process_knowledge(whitelist):
    """
    Process Knowledge file to extract essential knowledge domains (Degree Matcher).
    
    Filters rows where:
    - O*NET-SOC Code is in whitelist
    - Scale ID == "IM" (Importance)
    - Data Value > KNOWLEDGE_IMPORTANCE_THRESHOLD (default 3.0)
    
    Args:
        whitelist: List of valid O*NET-SOC codes
        
    Returns:
        DataFrame with O*NET-SOC Code, Element Name, Data Value columns
    """
    print_section_header("STEP 4: Processing Knowledge (Degree Matcher)")
    
    # Get file path
    file_path = get_file_path(KNOWLEDGE_FILE)
    print(f"Reading: {file_path}")
    
    # Read Excel file
    df = pd.read_excel(file_path)
    
    print(f"Total rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    # Detect required columns
    soc_code_col = detect_column(
        df,
        ["O*NET-SOC Code", "SOC Code", "Code", "ONET_SOC_CODE", "O*NET-SOC"],
        "O*NET-SOC Code"
    )
    
    scale_id_col = detect_column(
        df,
        ["Scale ID", "ScaleID", "Scale", "Scale_ID"],
        "Scale ID"
    )
    
    element_name_col = detect_column(
        df,
        ["Element Name", "ElementName", "Element", "Element_Name", "Knowledge"],
        "Element Name"
    )
    
    data_value_col = detect_column(
        df,
        ["Data Value", "DataValue", "Value", "Data_Value", "Score"],
        "Data Value"
    )
    
    print(f"Using SOC Code column: '{soc_code_col}'")
    print(f"Using Scale ID column: '{scale_id_col}'")
    print(f"Using Element Name column: '{element_name_col}'")
    print(f"Using Data Value column: '{data_value_col}'")
    
    # Filter by whitelist
    print(f"\nFiltering by whitelist ({len(whitelist)} codes)...")
    filtered_df = df[df[soc_code_col].isin(whitelist)].copy()
    
    print(f"Rows before whitelist filter: {len(df)}")
    print(f"Rows after whitelist filter: {len(filtered_df)}")
    print(f"Rows removed by whitelist: {len(df) - len(filtered_df)}")
    
    # Show unique Scale IDs before filtering
    unique_scale_ids = sorted(filtered_df[scale_id_col].dropna().unique())
    print(f"\nUnique Scale IDs found: {unique_scale_ids}")
    
    # Filter by Scale ID = "IM"
    print(f"Filtering by Scale ID = '{KNOWLEDGE_SCALE_ID}' (Importance)...")
    filtered_df = filtered_df[filtered_df[scale_id_col] == KNOWLEDGE_SCALE_ID].copy()
    
    print(f"Rows after Scale ID filter: {len(filtered_df)}")
    print(f"Rows removed by Scale ID filter: {len(df[df[soc_code_col].isin(whitelist)]) - len(filtered_df)}")
    
    # Filter by Data Value threshold
    print(f"\nFiltering by Data Value > {KNOWLEDGE_IMPORTANCE_THRESHOLD} (essential knowledge only)...")
    rows_before_threshold = len(filtered_df)
    filtered_df = filtered_df[filtered_df[data_value_col] > KNOWLEDGE_IMPORTANCE_THRESHOLD].copy()
    
    print(f"Rows after threshold filter: {len(filtered_df)}")
    print(f"Rows removed by threshold filter: {rows_before_threshold - len(filtered_df)}")
    
    # Show unique knowledge domains (Element Names)
    unique_knowledge = sorted(filtered_df[element_name_col].dropna().unique())
    print(f"\nUnique knowledge domains found: {len(unique_knowledge)}")
    print(f"Sample knowledge domains (first 5): {unique_knowledge[:5]}")
    
    # Select required columns
    result_df = filtered_df[[soc_code_col, element_name_col, data_value_col]].copy()
    result_df.columns = ["O*NET-SOC Code", "Element Name", "Data Value"]
    
    # Show statistics about data values
    print(f"\nData Value statistics:")
    print(f"  Min: {result_df['Data Value'].min()}")
    print(f"  Max: {result_df['Data Value'].max()}")
    print(f"  Mean: {result_df['Data Value'].mean():.2f}")
    
    # Count unique jobs in filtered data
    unique_jobs = result_df["O*NET-SOC Code"].nunique()
    print(f"\n[OK] Processed knowledge requirements for {unique_jobs} unique occupations")
    print(f"[OK] Total knowledge domain records: {len(result_df)}")
    
    # Show sample
    print(f"\nSample knowledge data (first 5 rows):")
    for idx, row in result_df.head(5).iterrows():
        print(f"  {row['O*NET-SOC Code']}: {row['Element Name']} (Importance: {row['Data Value']:.2f})")
    
    return result_df


# ============================================================================
# STEP 5: RESUME MATCHER - TECHNOLOGY SKILLS PROCESSING
# ============================================================================

def process_technology_skills(whitelist):
    """
    Process Technology Skills file to extract hard skills keywords (Resume Matcher).
    
    Filters rows where O*NET-SOC Code is in whitelist.
    Collects Example column which contains specific tool names like "Python", "React", "Adobe Photoshop".
    
    Args:
        whitelist: List of valid O*NET-SOC codes
        
    Returns:
        DataFrame with O*NET-SOC Code, Example columns (multiple rows per job - one row per tool)
    """
    print_section_header("STEP 5: Processing Technology Skills (Resume Matcher)")
    
    # Get file path
    file_path = get_file_path(TECHNOLOGY_SKILLS_FILE)
    print(f"Reading: {file_path}")
    
    # Read Excel file
    df = pd.read_excel(file_path)
    
    print(f"Total rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    # Detect required columns
    soc_code_col = detect_column(
        df,
        ["O*NET-SOC Code", "SOC Code", "Code", "ONET_SOC_CODE", "O*NET-SOC"],
        "O*NET-SOC Code"
    )
    
    example_col = detect_column(
        df,
        ["Example", "Examples", "Tool", "Technology", "Tool Name"],
        "Example"
    )
    
    print(f"Using SOC Code column: '{soc_code_col}'")
    print(f"Using Example column: '{example_col}'")
    
    # Filter by whitelist
    print(f"\nFiltering by whitelist ({len(whitelist)} codes)...")
    filtered_df = df[df[soc_code_col].isin(whitelist)].copy()
    
    print(f"Rows before filtering: {len(df)}")
    print(f"Rows after filtering: {len(filtered_df)}")
    print(f"Rows removed: {len(df) - len(filtered_df)}")
    
    # Select required columns
    result_df = filtered_df[[soc_code_col, example_col]].copy()
    result_df.columns = ["O*NET-SOC Code", "Example"]
    
    # Remove rows with missing Examples
    rows_before = len(result_df)
    result_df = result_df[result_df["Example"].notna()].copy()
    rows_removed = rows_before - len(result_df)
    
    if rows_removed > 0:
        print(f"Removed {rows_removed} rows with missing Examples")
    
    # Clean up Example values (strip whitespace, convert to string)
    result_df["Example"] = result_df["Example"].astype(str).str.strip()
    
    # Remove empty strings
    result_df = result_df[result_df["Example"] != ""].copy()
    
    # Statistics
    unique_jobs = result_df["O*NET-SOC Code"].nunique()
    total_tools = len(result_df)
    unique_tools = result_df["Example"].nunique()
    avg_tools_per_job = total_tools / unique_jobs if unique_jobs > 0 else 0
    
    print(f"\n[OK] Processed technology skills for {unique_jobs} unique occupations")
    print(f"[OK] Total tool/technology records: {total_tools}")
    print(f"[OK] Unique tools/technologies: {unique_tools}")
    print(f"[OK] Average tools per job: {avg_tools_per_job:.2f}")
    
    # Show sample
    print(f"\nSample technology skills (first 5 rows):")
    for idx, row in result_df.head(5).iterrows():
        print(f"  {row['O*NET-SOC Code']}: {row['Example']}")
    
    # Show most common tools
    if len(result_df) > 0:
        top_tools = result_df["Example"].value_counts().head(5)
        print(f"\nMost common tools/technologies (top 5):")
        for tool, count in top_tools.items():
            print(f"  - {tool}: {count} jobs")
    
    return result_df


# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

def main():
    """Run the complete ETL data cleaning and filtering pipeline."""
    print("\n" + "=" * 60)
    print("O*NET ETL PIPELINE - DATA CLEANING AND FILTERING")
    print("=" * 60)
    print(f"\nSource: {ONET_EXTRACTED_PATH}")
    print("Mode: Data cleaning and filtering (in-memory only)\n")
    
    try:
        # Step 1: Create whitelist from Job Zones
        whitelist, job_zones_df = process_job_zones()
        
        if not whitelist:
            raise ValueError("No valid jobs found in Job Zones. Cannot proceed.")
        
        # Step 2: Process Occupation Data
        occupation_df = process_occupation_data(whitelist)
        
        # Step 3: Process Interests
        interests_df = process_interests(whitelist)
        
        # Step 4: Process Knowledge
        knowledge_df = process_knowledge(whitelist)
        
        # Step 5: Process Technology Skills
        technology_skills_df = process_technology_skills(whitelist)
        
        # Summary
        print_section_header("ETL PIPELINE COMPLETED SUCCESSFULLY")
        print(f"\n[OK] Whitelist: {len(whitelist)} valid O*NET-SOC codes")
        print(f"[OK] Occupations: {len(occupation_df)} job profiles")
        print(f"[OK] Interests: {len(interests_df)} interest records for {interests_df['O*NET-SOC Code'].nunique()} occupations")
        print(f"[OK] Knowledge: {len(knowledge_df)} knowledge domain records for {knowledge_df['O*NET-SOC Code'].nunique()} occupations")
        print(f"[OK] Technology Skills: {len(technology_skills_df)} tool records for {technology_skills_df['O*NET-SOC Code'].nunique()} occupations")
        
        print("\n" + "-" * 60)
        print("Filtered data is available in memory:")
        print("  - whitelist: List of O*NET-SOC codes")
        print("  - occupation_df: DataFrame with Title and Description")
        print("  - interests_df: DataFrame with Element Name and Data Value")
        print(f"  - knowledge_df: DataFrame with essential knowledge domains (Data Value > {KNOWLEDGE_IMPORTANCE_THRESHOLD})")
        print("  - technology_skills_df: DataFrame with technology/tool keywords")
        print("-" * 60)
        
        # Return data for potential programmatic use
        return {
            'whitelist': whitelist,
            'occupation_df': occupation_df,
            'interests_df': interests_df,
            'knowledge_df': knowledge_df,
            'technology_skills_df': technology_skills_df,
            'job_zones_df': job_zones_df
        }
        
    except FileNotFoundError as e:
        print(f"\n{'='*60}")
        print("ETL PIPELINE FAILED - FILE NOT FOUND")
        print(f"{'='*60}")
        print(f"Error: {e}")
        print("\nPlease ensure you have run the onet_job_scraping scraper first.")
        raise
        
    except ValueError as e:
        print(f"\n{'='*60}")
        print("ETL PIPELINE FAILED - DATA STRUCTURE ERROR")
        print(f"{'='*60}")
        print(f"Error: {e}")
        raise
        
    except Exception as e:
        print(f"\n{'='*60}")
        print("ETL PIPELINE FAILED - UNEXPECTED ERROR")
        print(f"{'='*60}")
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()

