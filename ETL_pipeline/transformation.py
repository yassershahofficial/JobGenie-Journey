"""
ETL Pipeline - Transformation Stage

This module transforms cleaned data from data_cleaning.py into structured JSON job profiles.
It performs:
1. Data fetching from data_cleaning module
2. RIASEC vector transformation (pivot and normalize)
3. Keyword aggregation (Knowledge and Technology Skills)
4. Final job profile assembly
5. JSON export to jobs_database.json
"""

import json
import pandas as pd
from pathlib import Path
from data_cleaning import main as fetch_cleaned_data


# ============================================================================
# CONFIGURATION
# ============================================================================

# Output file
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_FILE = OUTPUT_DIR / "jobs_database.json"

# RIASEC categories in order
RIASEC_CATEGORIES = [
    "Realistic",
    "Investigative",
    "Artistic",
    "Social",
    "Enterprising",
    "Conventional"
]

# Normalization constants
RIASEC_MIN_SCALE = 1.0
RIASEC_MAX_SCALE = 7.0


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_section_header(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def normalize_riasec_score(value):
    """
    Normalize RIASEC score from 1-7 scale to 0.0-1.0 scale.
    
    Args:
        value: Raw score (1-7)
        
    Returns:
        Normalized score (0.0-1.0)
    """
    if pd.isna(value):
        return 0.0
    
    # Clamp to valid range
    value = max(RIASEC_MIN_SCALE, min(RIASEC_MAX_SCALE, float(value)))
    
    # Normalize: (value - min) / (max - min)
    normalized = (value - RIASEC_MIN_SCALE) / (RIASEC_MAX_SCALE - RIASEC_MIN_SCALE)
    
    # Ensure between 0.0 and 1.0
    return max(0.0, min(1.0, normalized))


# ============================================================================
# STATION A: RIASEC VECTOR TRANSFORMATION
# ============================================================================

def transform_riasec(interests_df):
    """
    Transform RIASEC interests data from long format to normalized vectors.
    
    Args:
        interests_df: DataFrame with columns: O*NET-SOC Code, Element Name, Data Value
        
    Returns:
        DataFrame with O*NET-SOC Code and 6 RIASEC columns
    """
    print_section_header("STATION A: RIASEC Vector Transformation")
    
    if interests_df.empty:
        print("Warning: Empty interests DataFrame")
        return pd.DataFrame()
    
    print(f"Input: {len(interests_df)} interest records")
    print(f"Unique jobs: {interests_df['O*NET-SOC Code'].nunique()}")
    
    # Pivot: Transform from long to wide format
    print("\nPivoting data (6 rows per job -> 1 row with 6 columns)...")
    pivot_df = interests_df.pivot_table(
        index="O*NET-SOC Code",
        columns="Element Name",
        values="Data Value",
        aggfunc='first'  # Take first value if duplicates
    )
    
    # Reset index to make O*NET-SOC Code a column
    pivot_df = pivot_df.reset_index()
    pivot_df.columns.name = None
    
    print(f"After pivot: {len(pivot_df)} jobs")
    
    # Ensure all RIASEC columns exist (fill missing with 0.0)
    for category in RIASEC_CATEGORIES:
        if category not in pivot_df.columns:
            # Try case-insensitive match
            matching_cols = [col for col in pivot_df.columns if str(col).strip().lower() == category.lower()]
            if matching_cols:
                pivot_df[category] = pivot_df[matching_cols[0]]
            else:
                pivot_df[category] = 0.0
                print(f"  Warning: {category} not found, setting to 0.0")
    
    # Select and reorder columns
    result_df = pivot_df[["O*NET-SOC Code"] + RIASEC_CATEGORIES].copy()
    
    # Normalize all RIASEC columns
    print("\nNormalizing scores (1-7 scale -> 0.0-1.0 scale)...")
    for category in RIASEC_CATEGORIES:
        result_df[category] = result_df[category].apply(normalize_riasec_score)
    
    # Fill any remaining NaN with 0.0
    result_df[RIASEC_CATEGORIES] = result_df[RIASEC_CATEGORIES].fillna(0.0)
    
    # Ensure values are between 0.0 and 1.0
    for col in RIASEC_CATEGORIES:
        result_df[col] = result_df[col].clip(0.0, 1.0)
    
    print(f"\n[OK] Transformed {len(result_df)} RIASEC vectors")
    print(f"Sample vector (first job): {result_df[RIASEC_CATEGORIES].iloc[0].tolist()}")
    
    return result_df


# ============================================================================
# STATION B: KEYWORD AGGREGATION
# ============================================================================

def aggregate_keywords(knowledge_df, technology_skills_df):
    """
    Aggregate Knowledge and Technology Skills into keyword lists per job.
    
    Args:
        knowledge_df: DataFrame with columns: O*NET-SOC Code, Element Name, Data Value
        technology_skills_df: DataFrame with columns: O*NET-SOC Code, Example
        
    Returns:
        Tuple of (knowledge_dict, tech_skills_dict) mapping O*NET-SOC Code -> list
    """
    print_section_header("STATION B: Keyword Aggregation")
    
    # Aggregate Knowledge Domains
    print("\nAggregating Knowledge Domains...")
    knowledge_dict = {}
    
    if not knowledge_df.empty:
        for job_id, group in knowledge_df.groupby("O*NET-SOC Code"):
            # Get unique knowledge domains (Element Names)
            domains = group["Element Name"].dropna().unique().tolist()
            # Convert to strings and strip whitespace
            domains = [str(d).strip() for d in domains if str(d).strip()]
            knowledge_dict[job_id] = sorted(list(set(domains)))  # Remove duplicates and sort
    else:
        print("  Warning: Empty knowledge DataFrame")
    
    print(f"[OK] Aggregated knowledge for {len(knowledge_dict)} jobs")
    if knowledge_dict:
        sample_job = list(knowledge_dict.keys())[0]
        print(f"Sample knowledge domains ({sample_job}): {knowledge_dict[sample_job][:3]}...")
    
    # Aggregate Technology Skills
    print("\nAggregating Technology Skills...")
    tech_skills_dict = {}
    
    if not technology_skills_df.empty:
        for job_id, group in technology_skills_df.groupby("O*NET-SOC Code"):
            # Get unique technology skills (Examples)
            skills = group["Example"].dropna().unique().tolist()
            # Convert to strings, strip whitespace, remove empty strings
            skills = [str(s).strip() for s in skills if str(s).strip()]
            tech_skills_dict[job_id] = sorted(list(set(skills)))  # Remove duplicates and sort
    else:
        print("  Warning: Empty technology skills DataFrame")
    
    print(f"[OK] Aggregated tech skills for {len(tech_skills_dict)} jobs")
    if tech_skills_dict:
        sample_job = list(tech_skills_dict.keys())[0]
        print(f"Sample tech skills ({sample_job}): {tech_skills_dict[sample_job][:3]}...")
    
    return knowledge_dict, tech_skills_dict


# ============================================================================
# STATION C: FINAL ASSEMBLY
# ============================================================================

def assemble_job_profiles(whitelist, occupation_df, riasec_df, knowledge_dict, tech_skills_dict, job_zones_df):
    """
    Assemble final job profiles into JSON structure.
    
    Args:
        whitelist: List of valid O*NET-SOC codes
        occupation_df: DataFrame with O*NET-SOC Code, Title, Description
        riasec_df: DataFrame with O*NET-SOC Code and 6 RIASEC columns
        knowledge_dict: Dictionary mapping O*NET-SOC Code -> list of knowledge domains
        tech_skills_dict: Dictionary mapping O*NET-SOC Code -> list of tech skills
        job_zones_df: DataFrame with O*NET-SOC Code, Job Zone
        
    Returns:
        List of job profile dictionaries
    """
    print_section_header("STATION C: Final Assembly")
    
    # Create lookup dictionaries for faster access
    occupation_lookup = {}
    if not occupation_df.empty:
        for _, row in occupation_df.iterrows():
            occupation_lookup[row["O*NET-SOC Code"]] = {
                "title": str(row["Title"]),
                "description": str(row["Description"])
            }
    
    riasec_lookup = {}
    if not riasec_df.empty:
        for _, row in riasec_df.iterrows():
            riasec_vector = [float(row[cat]) for cat in RIASEC_CATEGORIES]
            riasec_lookup[row["O*NET-SOC Code"]] = riasec_vector
    
    job_zone_lookup = {}
    if not job_zones_df.empty:
        for _, row in job_zones_df.iterrows():
            job_zone_lookup[row["O*NET-SOC Code"]] = int(row["Job Zone"])
    
    # Assemble job profiles
    job_profiles = []
    jobs_with_missing_data = []
    
    print(f"\nAssembling profiles for {len(whitelist)} jobs...")
    
    for job_id in whitelist:
        # Get occupation data
        occupation = occupation_lookup.get(job_id, {})
        title = occupation.get("title", "Unknown Title")
        description = occupation.get("description", "No description available")
        
        # Get RIASEC vector
        riasec_vector = riasec_lookup.get(job_id, [0.0] * 6)
        
        # Get keywords
        knowledge_domains = knowledge_dict.get(job_id, [])
        tech_skills = tech_skills_dict.get(job_id, [])
        
        # Get job zone
        job_zone = job_zone_lookup.get(job_id, None)
        
        # Check for missing critical data
        if not title or title == "Unknown Title":
            jobs_with_missing_data.append(job_id)
        
        # Create job profile
        job_profile = {
            "id": str(job_id),
            "title": title,
            "description": description,
            "vectors": {
                "riasec": riasec_vector
            },
            "keywords": {
                "knowledge_domains": knowledge_domains,
                "tech_skills": tech_skills
            },
            "filters": {
                "job_zone": job_zone
            }
        }
        
        job_profiles.append(job_profile)
    
    print(f"[OK] Assembled {len(job_profiles)} job profiles")
    
    if jobs_with_missing_data:
        print(f"  Warning: {len(jobs_with_missing_data)} jobs have missing title/description")
    
    return job_profiles


# ============================================================================
# PACKAGING AND SAVING
# ============================================================================

def save_jobs_database(job_profiles, output_file):
    """
    Save job profiles to JSON file.
    
    Args:
        job_profiles: List of job profile dictionaries
        output_file: Path to output JSON file
    """
    print_section_header("PACKAGING: Saving Jobs Database")
    
    # Create output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Writing {len(job_profiles)} job profiles to: {output_file}")
    
    # Write to JSON file with proper indentation
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(job_profiles, f, indent=2, ensure_ascii=False)
    
    # Get file size
    file_size = output_file.stat().st_size / 1024  # KB
    print(f"[OK] Saved successfully")
    print(f"  File size: {file_size:.2f} KB")
    print(f"  Location: {output_file.absolute()}")


# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

def main():
    """Run the complete transformation pipeline."""
    print("\n" + "=" * 60)
    print("O*NET ETL PIPELINE - TRANSFORMATION STAGE")
    print("=" * 60)
    print("\nTransforming cleaned data into structured JSON job profiles...\n")
    
    try:
        # Step 1: Data Fetching (The Handshake)
        print_section_header("STEP 1: Data Fetching (The Handshake)")
        print("Calling data_cleaning.main() to fetch cleaned data...")
        
        data_package = fetch_cleaned_data()
        
        # Extract all DataFrames
        whitelist = data_package['whitelist']
        occupation_df = data_package['occupation_df']
        interests_df = data_package['interests_df']
        knowledge_df = data_package['knowledge_df']
        technology_skills_df = data_package['technology_skills_df']
        job_zones_df = data_package['job_zones_df']
        
        print(f"[OK] Fetched data package:")
        print(f"  - Whitelist: {len(whitelist)} jobs")
        print(f"  - Occupations: {len(occupation_df)} records")
        print(f"  - Interests: {len(interests_df)} records")
        print(f"  - Knowledge: {len(knowledge_df)} records")
        print(f"  - Technology Skills: {len(technology_skills_df)} records")
        print(f"  - Job Zones: {len(job_zones_df)} records")
        
        # Step 2: Station A - RIASEC Transformation
        riasec_df = transform_riasec(interests_df)
        
        # Step 3: Station B - Keyword Aggregation
        knowledge_dict, tech_skills_dict = aggregate_keywords(knowledge_df, technology_skills_df)
        
        # Step 4: Station C - Final Assembly
        job_profiles = assemble_job_profiles(
            whitelist,
            occupation_df,
            riasec_df,
            knowledge_dict,
            tech_skills_dict,
            job_zones_df
        )
        
        # Step 5: Packaging and Saving
        save_jobs_database(job_profiles, OUTPUT_FILE)
        
        # Final Summary
        print_section_header("TRANSFORMATION PIPELINE COMPLETED SUCCESSFULLY")
        print(f"\n[OK] Processed {len(job_profiles)} job profiles")
        print(f"[OK] Output file: {OUTPUT_FILE}")
        print(f"\nJob profiles are ready for AI matching!")
        
        return job_profiles
        
    except KeyError as e:
        print(f"\n{'='*60}")
        print("TRANSFORMATION PIPELINE FAILED - MISSING DATA")
        print(f"{'='*60}")
        print(f"Error: Missing key in data package: {e}")
        print("\nPlease ensure data_cleaning.py returns all required DataFrames.")
        raise
        
    except Exception as e:
        print(f"\n{'='*60}")
        print("TRANSFORMATION PIPELINE FAILED - UNEXPECTED ERROR")
        print(f"{'='*60}")
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()

