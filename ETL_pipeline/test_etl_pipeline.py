"""
Test script for ETL Pipeline

This script tests both data_cleaning.py and transformation.py modules
to ensure they work correctly and produce valid output.
"""

import json
import sys
from pathlib import Path
import pandas as pd

# Import modules from same directory
import data_cleaning
import transformation


# ============================================================================
# TEST CONFIGURATION
# ============================================================================

OUTPUT_FILE = Path(__file__).parent / "output" / "jobs_database.json"
RIASEC_CATEGORIES = [
    "Realistic",
    "Investigative",
    "Artistic",
    "Social",
    "Enterprising",
    "Conventional"
]


# ============================================================================
# TEST HELPERS
# ============================================================================

def print_test_header(test_name):
    """Print a formatted test header."""
    print("\n" + "=" * 70)
    print(f"TEST: {test_name}")
    print("=" * 70)


def print_test_result(passed, message):
    """Print test result."""
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status}: {message}")


def assert_condition(condition, message):
    """Assert a condition and print result."""
    if not condition:
        print_test_result(False, message)
        return False
    print_test_result(True, message)
    return True


# ============================================================================
# TEST 1: DATA CLEANING MODULE
# ============================================================================

def test_data_cleaning():
    """Test the data_cleaning module."""
    print_test_header("Data Cleaning Module")
    
    all_passed = True
    
    try:
        # Run data cleaning
        print("\nRunning data_cleaning.main()...")
        data_package = data_cleaning.main()
        
        # Test 1.1: Check return structure
        print("\n--- Test 1.1: Return Structure ---")
        required_keys = ['whitelist', 'occupation_df', 'interests_df', 
                        'knowledge_df', 'technology_skills_df', 'job_zones_df']
        for key in required_keys:
            if not assert_condition(key in data_package, f"Data package contains '{key}'"):
                all_passed = False
        
        # Test 1.2: Whitelist validation
        print("\n--- Test 1.2: Whitelist Validation ---")
        whitelist = data_package['whitelist']
        if not assert_condition(isinstance(whitelist, list), "Whitelist is a list"):
            all_passed = False
        if not assert_condition(len(whitelist) > 0, f"Whitelist contains {len(whitelist)} jobs"):
            all_passed = False
        if not assert_condition(all(isinstance(code, str) for code in whitelist), 
                                "All whitelist codes are strings"):
            all_passed = False
        
        # Test 1.3: Occupation DataFrame validation
        print("\n--- Test 1.3: Occupation DataFrame ---")
        occupation_df = data_package['occupation_df']
        if not assert_condition(isinstance(occupation_df, pd.DataFrame), 
                               "Occupation data is a DataFrame"):
            all_passed = False
        if not occupation_df.empty:
            required_cols = ["O*NET-SOC Code", "Title", "Description"]
            for col in required_cols:
                if not assert_condition(col in occupation_df.columns, 
                                       f"Occupation DataFrame has '{col}' column"):
                    all_passed = False
            if not assert_condition(len(occupation_df) > 0, 
                                   f"Occupation DataFrame has {len(occupation_df)} rows"):
                all_passed = False
        
        # Test 1.4: Interests DataFrame validation
        print("\n--- Test 1.4: Interests DataFrame ---")
        interests_df = data_package['interests_df']
        if not assert_condition(isinstance(interests_df, pd.DataFrame), 
                               "Interests data is a DataFrame"):
            all_passed = False
        if not interests_df.empty:
            required_cols = ["O*NET-SOC Code", "Element Name", "Data Value"]
            for col in required_cols:
                if not assert_condition(col in interests_df.columns, 
                                       f"Interests DataFrame has '{col}' column"):
                    all_passed = False
        
        # Test 1.5: Knowledge DataFrame validation
        print("\n--- Test 1.5: Knowledge DataFrame ---")
        knowledge_df = data_package['knowledge_df']
        if not assert_condition(isinstance(knowledge_df, pd.DataFrame), 
                               "Knowledge data is a DataFrame"):
            all_passed = False
        if not knowledge_df.empty:
            required_cols = ["O*NET-SOC Code", "Element Name", "Data Value"]
            for col in required_cols:
                if not assert_condition(col in knowledge_df.columns, 
                                       f"Knowledge DataFrame has '{col}' column"):
                    all_passed = False
            # Check threshold filter
            if 'Data Value' in knowledge_df.columns:
                min_value = knowledge_df['Data Value'].min()
                if not assert_condition(min_value > 3.0, 
                                       f"Knowledge threshold filter works (min: {min_value:.2f} > 3.0)"):
                    all_passed = False
        
        # Test 1.6: Technology Skills DataFrame validation
        print("\n--- Test 1.6: Technology Skills DataFrame ---")
        tech_skills_df = data_package['technology_skills_df']
        if not assert_condition(isinstance(tech_skills_df, pd.DataFrame), 
                               "Technology skills data is a DataFrame"):
            all_passed = False
        if not tech_skills_df.empty:
            required_cols = ["O*NET-SOC Code", "Example"]
            for col in required_cols:
                if not assert_condition(col in tech_skills_df.columns, 
                                       f"Technology Skills DataFrame has '{col}' column"):
                    all_passed = False
        
        # Test 1.7: Job Zones DataFrame validation
        print("\n--- Test 1.7: Job Zones DataFrame ---")
        job_zones_df = data_package['job_zones_df']
        if not assert_condition(isinstance(job_zones_df, pd.DataFrame), 
                               "Job Zones data is a DataFrame"):
            all_passed = False
        if not job_zones_df.empty:
            required_cols = ["O*NET-SOC Code", "Job Zone"]
            for col in required_cols:
                if not assert_condition(col in job_zones_df.columns, 
                                       f"Job Zones DataFrame has '{col}' column"):
                    all_passed = False
            # Check job zone values
            if 'Job Zone' in job_zones_df.columns:
                unique_zones = job_zones_df['Job Zone'].unique()
                valid_zones = [3, 4]
                if not assert_condition(all(zone in valid_zones for zone in unique_zones), 
                                      f"Job Zones are valid (zones: {unique_zones})"):
                    all_passed = False
        
        # Test 1.8: Data consistency
        print("\n--- Test 1.8: Data Consistency ---")
        if not occupation_df.empty and len(whitelist) > 0:
            occupation_codes = set(occupation_df["O*NET-SOC Code"].unique())
            whitelist_set = set(whitelist)
            if not assert_condition(occupation_codes.issubset(whitelist_set), 
                                   "All occupation codes are in whitelist"):
                all_passed = False
        
        return all_passed, data_package
        
    except Exception as e:
        print_test_result(False, f"Data cleaning failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False, None


# ============================================================================
# TEST 2: TRANSFORMATION MODULE
# ============================================================================

def test_transformation():
    """Test the transformation module."""
    print_test_header("Transformation Module")
    
    all_passed = True
    
    try:
        # Run transformation
        print("\nRunning transformation.main()...")
        job_profiles = transformation.main()
        
        # Test 2.1: Return type
        print("\n--- Test 2.1: Return Type ---")
        if not assert_condition(isinstance(job_profiles, list), 
                               "Transformation returns a list"):
            all_passed = False
        if not assert_condition(len(job_profiles) > 0, 
                               f"Transformation returned {len(job_profiles)} job profiles"):
            all_passed = False
        
        # Test 2.2: Job profile structure
        print("\n--- Test 2.2: Job Profile Structure ---")
        if job_profiles:
            sample_profile = job_profiles[0]
            required_keys = ['id', 'title', 'description', 'vectors', 'keywords', 'filters']
            for key in required_keys:
                if not assert_condition(key in sample_profile, 
                                       f"Job profile has '{key}' field"):
                    all_passed = False
            
            # Test vectors structure
            if 'vectors' in sample_profile:
                if not assert_condition('riasec' in sample_profile['vectors'], 
                                       "Profile has 'riasec' vector"):
                    all_passed = False
                if 'riasec' in sample_profile['vectors']:
                    riasec = sample_profile['vectors']['riasec']
                    if not assert_condition(isinstance(riasec, list), 
                                           "RIASEC is a list"):
                        all_passed = False
                    if not assert_condition(len(riasec) == 6, 
                                           f"RIASEC has 6 values (got {len(riasec)})"):
                        all_passed = False
                    if not assert_condition(all(0.0 <= v <= 1.0 for v in riasec), 
                                           "All RIASEC values are between 0.0 and 1.0"):
                        all_passed = False
            
            # Test keywords structure
            if 'keywords' in sample_profile:
                if not assert_condition('knowledge_domains' in sample_profile['keywords'], 
                                      "Profile has 'knowledge_domains'"):
                    all_passed = False
                if not assert_condition('tech_skills' in sample_profile['keywords'], 
                                      "Profile has 'tech_skills'"):
                    all_passed = False
                if 'knowledge_domains' in sample_profile['keywords']:
                    kd = sample_profile['keywords']['knowledge_domains']
                    if not assert_condition(isinstance(kd, list), 
                                           "Knowledge domains is a list"):
                        all_passed = False
                if 'tech_skills' in sample_profile['keywords']:
                    ts = sample_profile['keywords']['tech_skills']
                    if not assert_condition(isinstance(ts, list), 
                                           "Tech skills is a list"):
                        all_passed = False
            
            # Test filters structure
            if 'filters' in sample_profile:
                if not assert_condition('job_zone' in sample_profile['filters'], 
                                      "Profile has 'job_zone' filter"):
                    all_passed = False
        
        # Test 2.3: All profiles have required fields
        print("\n--- Test 2.3: All Profiles Valid ---")
        required_keys = ['id', 'title', 'description', 'vectors', 'keywords', 'filters']
        invalid_profiles = []
        for i, profile in enumerate(job_profiles):
            missing_keys = [key for key in required_keys if key not in profile]
            if missing_keys:
                invalid_profiles.append((i, missing_keys))
        
        if not assert_condition(len(invalid_profiles) == 0, 
                               f"All {len(job_profiles)} profiles have required fields"):
            all_passed = False
            for idx, missing in invalid_profiles[:5]:  # Show first 5
                print(f"  Profile {idx} missing: {missing}")
        
        # Test 2.4: RIASEC vector validation for all profiles
        print("\n--- Test 2.4: RIASEC Vector Validation ---")
        invalid_riasec = []
        for i, profile in enumerate(job_profiles):
            if 'vectors' in profile and 'riasec' in profile['vectors']:
                riasec = profile['vectors']['riasec']
                if not isinstance(riasec, list) or len(riasec) != 6:
                    invalid_riasec.append((i, "wrong length or type"))
                elif not all(0.0 <= v <= 1.0 for v in riasec):
                    invalid_riasec.append((i, "values out of range"))
        
        if not assert_condition(len(invalid_riasec) == 0, 
                               f"All {len(job_profiles)} profiles have valid RIASEC vectors"):
            all_passed = False
            for idx, reason in invalid_riasec[:5]:  # Show first 5
                print(f"  Profile {idx} invalid: {reason}")
        
        # Test 2.5: Unique IDs
        print("\n--- Test 2.5: Unique Job IDs ---")
        job_ids = [profile['id'] for profile in job_profiles]
        unique_ids = set(job_ids)
        if not assert_condition(len(unique_ids) == len(job_ids), 
                               f"All {len(job_ids)} job IDs are unique"):
            all_passed = False
            duplicates = len(job_ids) - len(unique_ids)
            if duplicates > 0:
                print(f"  Found {duplicates} duplicate IDs")
        
        return all_passed, job_profiles
        
    except Exception as e:
        print_test_result(False, f"Transformation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False, None


# ============================================================================
# TEST 3: OUTPUT FILE VALIDATION
# ============================================================================

def test_output_file():
    """Test the output JSON file."""
    print_test_header("Output File Validation")
    
    all_passed = True
    
    try:
        # Test 3.1: File exists
        print("\n--- Test 3.1: File Exists ---")
        if not assert_condition(OUTPUT_FILE.exists(), 
                               f"Output file exists: {OUTPUT_FILE}"):
            all_passed = False
            return all_passed
        
        # Test 3.2: Valid JSON
        print("\n--- Test 3.2: Valid JSON ---")
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                job_profiles = json.load(f)
            if not assert_condition(isinstance(job_profiles, list), 
                                   "JSON file contains a list"):
                all_passed = False
            if not assert_condition(len(job_profiles) > 0, 
                                   f"JSON file contains {len(job_profiles)} profiles"):
                all_passed = False
        except json.JSONDecodeError as e:
            print_test_result(False, f"JSON decode error: {e}")
            all_passed = False
            return all_passed
        
        # Test 3.3: File size
        print("\n--- Test 3.3: File Size ---")
        file_size_kb = OUTPUT_FILE.stat().st_size / 1024
        if not assert_condition(file_size_kb > 0, 
                              f"File size: {file_size_kb:.2f} KB"):
            all_passed = False
        
        # Test 3.4: Sample profile validation
        print("\n--- Test 3.4: Sample Profile from File ---")
        if job_profiles:
            sample = job_profiles[0]
            required_keys = ['id', 'title', 'description', 'vectors', 'keywords', 'filters']
            for key in required_keys:
                if not assert_condition(key in sample, 
                                       f"Sample profile has '{key}' field"):
                    all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_test_result(False, f"Output file validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# TEST 4: DATA INTEGRITY CHECKS
# ============================================================================

def test_data_integrity(data_package, job_profiles):
    """Test data integrity across the pipeline."""
    print_test_header("Data Integrity Checks")
    
    all_passed = True
    
    if data_package is None or job_profiles is None:
        print_test_result(False, "Cannot run integrity checks - missing data")
        return False
    
    try:
        # Test 4.1: Whitelist matches job profiles
        print("\n--- Test 4.1: Whitelist Matches Profiles ---")
        whitelist = set(data_package['whitelist'])
        profile_ids = set(profile['id'] for profile in job_profiles)
        
        if not assert_condition(whitelist == profile_ids, 
                               "Whitelist matches all job profile IDs"):
            all_passed = False
            missing_in_profiles = whitelist - profile_ids
            missing_in_whitelist = profile_ids - whitelist
            if missing_in_profiles:
                print(f"  IDs in whitelist but not in profiles: {len(missing_in_profiles)}")
            if missing_in_whitelist:
                print(f"  IDs in profiles but not in whitelist: {len(missing_in_whitelist)}")
        
        # Test 4.2: Occupation data matches profiles
        print("\n--- Test 4.2: Occupation Data Matches Profiles ---")
        occupation_df = data_package['occupation_df']
        if not occupation_df.empty:
            occupation_codes = set(occupation_df["O*NET-SOC Code"].unique())
            profile_ids = set(profile['id'] for profile in job_profiles)
            
            if not assert_condition(occupation_codes == profile_ids, 
                                   "Occupation codes match profile IDs"):
                all_passed = False
        
        # Test 4.3: Job zones match
        print("\n--- Test 4.3: Job Zones Match ---")
        job_zones_df = data_package['job_zones_df']
        if not job_zones_df.empty:
            job_zone_dict = dict(zip(
                job_zones_df["O*NET-SOC Code"], 
                job_zones_df["Job Zone"]
            ))
            
            mismatches = 0
            for profile in job_profiles:
                profile_id = profile['id']
                profile_zone = profile.get('filters', {}).get('job_zone')
                expected_zone = job_zone_dict.get(profile_id)
                if profile_zone != expected_zone:
                    mismatches += 1
            
            if not assert_condition(mismatches == 0, 
                                   f"All {len(job_profiles)} profiles have matching job zones"):
                all_passed = False
                if mismatches > 0:
                    print(f"  Found {mismatches} mismatches")
        
        return all_passed
        
    except Exception as e:
        print_test_result(False, f"Data integrity check failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("ETL PIPELINE TEST SUITE")
    print("=" * 70)
    
    results = {}
    
    # Test 1: Data Cleaning
    data_cleaning_passed, data_package = test_data_cleaning()
    results['data_cleaning'] = data_cleaning_passed
    
    # Test 2: Transformation
    transformation_passed, job_profiles = test_transformation()
    results['transformation'] = transformation_passed
    
    # Test 3: Output File
    output_file_passed = test_output_file()
    results['output_file'] = output_file_passed
    
    # Test 4: Data Integrity (only if previous tests passed)
    if data_cleaning_passed and transformation_passed:
        integrity_passed = test_data_integrity(data_package, job_profiles)
        results['data_integrity'] = integrity_passed
    else:
        print("\n" + "=" * 70)
        print("Skipping data integrity tests (previous tests failed)")
        print("=" * 70)
        results['data_integrity'] = False
    
    # Final Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    total_tests = len(results)
    passed_tests = sum(1 for passed in results.values() if passed)
    
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {test_name}")
    
    print("\n" + "-" * 70)
    print(f"Total: {passed_tests}/{total_tests} tests passed")
    print("-" * 70)
    
    if passed_tests == total_tests:
        print("\n[SUCCESS] All tests passed! ETL pipeline is working correctly.")
        return 0
    else:
        print("\n[WARNING] Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

