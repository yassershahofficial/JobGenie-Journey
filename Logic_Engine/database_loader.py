"""
Database Loader - Phase 1: Loading the Blueprint

Loads the jobs_database.json file into memory for fast access during matching.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from .config import DATABASE_PATH, COSINE_BASELINE_SAMPLE_SIZE


# Cache for loaded database
_jobs_cache: List[Dict[str, Any]] = None

# Cache for pre-calculated statistics
_idf_weights_cache: Dict[str, Dict[str, float]] = None
_cosine_baseline_cache: float = None


def load_jobs_database(force_reload: bool = False) -> List[Dict[str, Any]]:
    """
    Load jobs database from JSON file into memory.
    
    This function implements Phase 1 of the matching pipeline:
    - Locates jobs_database.json file
    - Loads it into RAM for fast access
    - Caches the result to avoid repeated file reads
    
    Args:
        force_reload: If True, reload from file even if cached. Default: False
        
    Returns:
        List of job dictionaries, each containing:
        - id: O*NET-SOC Code
        - title: Job title
        - description: Job description
        - vectors: Dictionary with 'riasec' vector (6 floats, 0.0-1.0)
        - keywords: Dictionary with 'knowledge_domains' and 'tech_skills' lists
        - filters: Dictionary with 'job_zone'
        
    Raises:
        FileNotFoundError: If jobs_database.json file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    global _jobs_cache
    
    # Return cached data if available and not forcing reload
    if _jobs_cache is not None and not force_reload:
        return _jobs_cache
    
    # Check if file exists
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Jobs database not found at: {DATABASE_PATH}\n"
            "Please ensure the ETL pipeline has been run to generate jobs_database.json"
        )
    
    # Load JSON file
    try:
        with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
            _jobs_cache = json.load(f)
        
        print(f"[OK] Loaded {len(_jobs_cache)} jobs from database")
        print(f"     Location: {DATABASE_PATH}")
        
        return _jobs_cache
        
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in jobs database: {e.msg}",
            e.doc,
            e.pos
        )


def clear_cache():
    """Clear the cached jobs database. Useful for testing or forced reloads."""
    global _jobs_cache
    _jobs_cache = None


def calculate_statistics(jobs_database: List[Dict[str, Any]], force_recalculate: bool = False) -> Dict[str, Any]:
    """
    Pre-calculate statistics needed for advanced matching.
    
    Calculates:
    - IDF weights for all keywords (knowledge domains and tech skills)
    - Cosine similarity baseline (average cosine similarity between random job pairs)
    
    Args:
        jobs_database: List of job dictionaries
        force_recalculate: If True, recalculate even if cached. Default: False
        
    Returns:
        Dictionary with:
        - 'idf_weights': Dict with 'knowledge_domains' and 'tech_skills' IDF weights
        - 'cosine_baseline': Average cosine similarity baseline (float)
    """
    global _idf_weights_cache, _cosine_baseline_cache
    
    # Return cached data if available and not forcing recalculation
    if _idf_weights_cache is not None and _cosine_baseline_cache is not None and not force_recalculate:
        return {
            'idf_weights': _idf_weights_cache,
            'cosine_baseline': _cosine_baseline_cache
        }
    
    from .similarity import calculate_idf_weights, calculate_cosine_baseline
    
    print("[CALC] Computing IDF weights...")
    _idf_weights_cache = calculate_idf_weights(jobs_database)
    
    print("[CALC] Computing cosine similarity baseline...")
    _cosine_baseline_cache = calculate_cosine_baseline(jobs_database, COSINE_BASELINE_SAMPLE_SIZE)
    
    print(f"[OK] Statistics calculated:")
    print(f"     - Knowledge domains: {len(_idf_weights_cache['knowledge_domains'])} unique keywords")
    print(f"     - Tech skills: {len(_idf_weights_cache['tech_skills'])} unique keywords")
    print(f"     - Cosine baseline: {_cosine_baseline_cache:.4f}")
    
    return {
        'idf_weights': _idf_weights_cache,
        'cosine_baseline': _cosine_baseline_cache
    }


def clear_statistics_cache():
    """Clear cached statistics. Useful for testing or forced recalculations."""
    global _idf_weights_cache, _cosine_baseline_cache
    _idf_weights_cache = None
    _cosine_baseline_cache = None

