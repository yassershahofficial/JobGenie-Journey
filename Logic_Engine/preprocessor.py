"""
Preprocessor - Phase 3: Standardizing the Input

Normalizes and standardizes user input to match database format:
- RIASEC scores: 1-7 scale → 0.0-1.0 scale
- Text fields: Convert to lowercase for matching
"""

from typing import List, Dict, Any
from .config import RIASEC_MIN_SCALE, RIASEC_MAX_SCALE


def normalize_riasec(user_riasec: List[float]) -> List[float]:
    """
    Normalize RIASEC scores from 1-7 scale to 0.0-1.0 scale.
    
    Applies Min-Max normalization formula:
    normalized = (value - min) / (max - min)
    
    Args:
        user_riasec: List of 6 floats representing RIASEC scores (1-7 scale)
                    Order: [Realistic, Investigative, Artistic, Social, Enterprising, Conventional]
        
    Returns:
        List of 6 floats normalized to 0.0-1.0 scale
        
    Raises:
        ValueError: If input doesn't have exactly 6 values
    """
    if len(user_riasec) != 6:
        raise ValueError(
            f"RIASEC vector must have exactly 6 values. Got {len(user_riasec)}"
        )
    
    normalized = []
    for value in user_riasec:
        # Clamp to valid range
        value = max(RIASEC_MIN_SCALE, min(RIASEC_MAX_SCALE, float(value)))
        
        # Min-Max normalization: (value - min) / (max - min)
        normalized_value = (value - RIASEC_MIN_SCALE) / (RIASEC_MAX_SCALE - RIASEC_MIN_SCALE)
        
        # Ensure between 0.0 and 1.0
        normalized_value = max(0.0, min(1.0, normalized_value))
        normalized.append(normalized_value)
    
    return normalized


def standardize_text(text_list: List[str]) -> List[str]:
    """
    Standardize text by converting to lowercase.
    
    Converts all strings in the list to lowercase to ensure case-insensitive matching.
    Also strips whitespace and filters out empty strings.
    
    Args:
        text_list: List of strings (knowledge domains or tech skills)
        
    Returns:
        List of lowercase strings with no empty values
    """
    if not text_list:
        return []
    
    standardized = []
    for text in text_list:
        if text and isinstance(text, str):
            cleaned = text.strip().lower()
            if cleaned:  # Only add non-empty strings
                standardized.append(cleaned)
    
    return standardized


def preprocess_user_profile(user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Preprocess user profile to match database format.
    
    This function handles all preprocessing steps:
    - Normalizes RIASEC scores from 1-7 to 0.0-1.0
    - Standardizes knowledge domains (lowercase)
    - Standardizes tech skills (lowercase)
    
    Args:
        user_profile: Dictionary containing:
            - riasec: List of 6 floats (1-7 scale)
            - knowledge_domains: List of strings
            - tech_skills: List of strings
            
    Returns:
        Preprocessed user profile with normalized values
        
    Raises:
        KeyError: If required keys are missing
        ValueError: If RIASEC vector is invalid
    """
    # Create a copy to avoid modifying original
    processed = user_profile.copy()
    
    # Normalize RIASEC scores
    if 'riasec' in processed:
        processed['riasec'] = normalize_riasec(processed['riasec'])
    
    # Standardize knowledge domains
    if 'knowledge_domains' in processed:
        processed['knowledge_domains'] = standardize_text(processed['knowledge_domains'])
    else:
        processed['knowledge_domains'] = []
    
    # Standardize tech skills
    if 'tech_skills' in processed:
        processed['tech_skills'] = standardize_text(processed['tech_skills'])
    else:
        processed['tech_skills'] = []
    
    return processed

