"""
Advanced Similarity Calculators - Phase 2: The Advanced Toolset

Implements advanced similarity metrics with statistical normalization:
- Cosine Similarity: For comparing RIASEC vectors (with baseline normalization)
- Weighted Jaccard Similarity: TF-IDF weighted with fuzzy matching
- Sigmoid Activation: S-curve normalization for keyword scores
- Fuzzy Matching: Handles typos and variations
"""

import math
import random
from typing import List, Dict, Any, Set, Optional
from collections import Counter


def cosine_similarity(vector_a: List[float], vector_b: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Tool A: Vector Calculator (Cosine Similarity)
    - Multiplies matching positions, sums them up
    - Divides by the magnitude (size) of the vectors
    - Returns value between 0.0 (opposite) and 1.0 (identical)
    
    Formula: cos(θ) = (A · B) / (||A|| × ||B||)
    
    Args:
        vector_a: First vector (list of floats, typically 6 RIASEC values)
        vector_b: Second vector (list of floats, typically 6 RIASEC values)
        
    Returns:
        Cosine similarity score between 0.0 and 1.0
        
    Raises:
        ValueError: If vectors have different lengths or are empty
    """
    if len(vector_a) != len(vector_b):
        raise ValueError(
            f"Vectors must have same length. Got {len(vector_a)} and {len(vector_b)}"
        )
    
    if len(vector_a) == 0:
        raise ValueError("Vectors cannot be empty")
    
    # Calculate dot product
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    
    # Calculate magnitudes
    magnitude_a = math.sqrt(sum(a * a for a in vector_a))
    magnitude_b = math.sqrt(sum(b * b for b in vector_b))
    
    # Avoid division by zero
    if magnitude_a == 0.0 or magnitude_b == 0.0:
        return 0.0
    
    # Calculate cosine similarity
    similarity = dot_product / (magnitude_a * magnitude_b)
    
    # Ensure result is between 0.0 and 1.0 (cosine similarity can be -1 to 1)
    # For normalized vectors (0-1 scale), this should already be 0-1, but clamp to be safe
    return max(0.0, min(1.0, similarity))


def jaccard_similarity(list_a: List[str], list_b: List[str]) -> float:
    """
    Calculate basic Jaccard similarity between two lists of strings.
    
    Tool B: Overlap Calculator (Basic Jaccard Similarity)
    - Counts unique words in both lists (Intersection)
    - Counts total unique words across both lists (Union)
    - Divides Intersection by Union
    
    Formula: J(A, B) = |A ∩ B| / |A ∪ B|
    
    Args:
        list_a: First list of strings (knowledge domains or tech skills)
        list_b: Second list of strings (knowledge domains or tech skills)
        
    Returns:
        Jaccard similarity score between 0.0 (no match) and 1.0 (perfect match)
        
    Note:
        Returns 0.0 if both lists are empty (no overlap possible)
        Returns 1.0 if both lists are empty (edge case: both empty = perfect match)
    """
    # Convert to sets for efficient intersection/union operations
    set_a = set(list_a)
    set_b = set(list_b)
    
    # Handle empty sets
    if len(set_a) == 0 and len(set_b) == 0:
        return 1.0  # Both empty = perfect match
    
    if len(set_a) == 0 or len(set_b) == 0:
        return 0.0  # One empty = no overlap
    
    # Calculate intersection and union
    intersection = set_a & set_b
    union = set_a | set_b
    
    # Jaccard similarity
    if len(union) == 0:
        return 0.0
    
    similarity = len(intersection) / len(union)
    
    return similarity


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate Levenshtein distance between two strings.
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        Levenshtein distance (number of edits needed)
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def fuzzy_match(word_a: str, word_b: str, threshold: float = 0.85) -> bool:
    """
    Check if two words are similar enough to be considered a match.
    
    Uses Levenshtein distance normalized by max string length.
    
    Args:
        word_a: First word
        word_b: Second word
        threshold: Minimum similarity required (default: 0.85)
        
    Returns:
        True if words are similar enough, False otherwise
    """
    if word_a == word_b:
        return True
    
    max_len = max(len(word_a), len(word_b))
    if max_len == 0:
        return True
    
    distance = levenshtein_distance(word_a, word_b)
    similarity = 1.0 - (distance / max_len)
    
    return similarity >= threshold


def find_fuzzy_matches(user_list: List[str], job_list: List[str], threshold: float = 0.85) -> Set[str]:
    """
    Find all fuzzy matches between user and job keywords.
    
    Args:
        user_list: List of user keywords
        job_list: List of job keywords
        threshold: Minimum similarity required for fuzzy match
        
    Returns:
        Set of matched keywords (from job_list)
    """
    matches = set()
    user_lower = [w.lower().strip() for w in user_list]
    job_lower = [w.lower().strip() for w in job_list]
    
    for user_word in user_lower:
        for job_word in job_lower:
            if fuzzy_match(user_word, job_word, threshold):
                matches.add(job_word)
    
    return matches


def calculate_idf_weights(jobs_database: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """
    Pre-calculate IDF weights for all keywords in the database.
    
    IDF (Inverse Document Frequency) gives higher weight to rare/technical keywords
    and lower weight to common/generic keywords.
    
    Formula: IDF(term) = log(total_jobs / document_frequency(term))
    Normalized: IDF / max_IDF (to get 0-1 range)
    
    Args:
        jobs_database: List of job dictionaries
        
    Returns:
        Dictionary with 'knowledge_domains' and 'tech_skills' keys,
        each containing a dict mapping keyword -> IDF weight
    """
    total_jobs = len(jobs_database)
    
    if total_jobs == 0:
        return {'knowledge_domains': {}, 'tech_skills': {}}
    
    # Count document frequencies for knowledge domains
    knowledge_df = Counter()
    skills_df = Counter()
    
    for job in jobs_database:
        knowledge = job.get('keywords', {}).get('knowledge_domains', [])
        skills = job.get('keywords', {}).get('tech_skills', [])
        
        # Count unique keywords per job
        knowledge_set = set(k.lower().strip() for k in knowledge if k)
        skills_set = set(s.lower().strip() for s in skills if s)
        
        for kw in knowledge_set:
            knowledge_df[kw] += 1
        for skill in skills_set:
            skills_df[skill] += 1
    
    # Calculate IDF weights: log(total_jobs / document_frequency)
    knowledge_idf = {}
    skills_idf = {}
    
    # Calculate max IDF for normalization
    max_knowledge_idf = 0.0
    max_skills_idf = 0.0
    
    for kw, df in knowledge_df.items():
        if df > 0:
            idf = math.log(total_jobs / df)
            knowledge_idf[kw] = idf
            max_knowledge_idf = max(max_knowledge_idf, idf)
    
    for skill, df in skills_df.items():
        if df > 0:
            idf = math.log(total_jobs / df)
            skills_idf[skill] = idf
            max_skills_idf = max(max_skills_idf, idf)
    
    # Normalize to 0-1 range
    if max_knowledge_idf > 0:
        knowledge_idf = {kw: idf / max_knowledge_idf for kw, idf in knowledge_idf.items()}
    else:
        knowledge_idf = {kw: 0.0 for kw in knowledge_idf.keys()}
    
    if max_skills_idf > 0:
        skills_idf = {skill: idf / max_skills_idf for skill, idf in skills_idf.items()}
    else:
        skills_idf = {skill: 0.0 for skill in skills_idf.keys()}
    
    return {
        'knowledge_domains': knowledge_idf,
        'tech_skills': skills_idf
    }


def weighted_jaccard_similarity(
    user_list: List[str],
    job_list: List[str],
    idf_weights: Dict[str, float],
    fuzzy_threshold: float = 0.85
) -> float:
    """
    Calculate weighted Jaccard similarity using IDF weights and fuzzy matching.
    
    Formula: sum(IDF weights of matched keywords) / sum(IDF weights of all keywords)
    
    Args:
        user_list: List of user keywords
        job_list: List of job keywords
        idf_weights: Dictionary mapping keyword -> IDF weight
        fuzzy_threshold: Minimum similarity for fuzzy matching
        
    Returns:
        Weighted Jaccard similarity score between 0.0 and 1.0
    """
    if not user_list and not job_list:
        return 1.0
    
    if not user_list or not job_list:
        return 0.0
    
    # Standardize keywords
    user_lower = [w.lower().strip() for w in user_list if w]
    job_lower = [w.lower().strip() for w in job_list if w]
    
    # Find fuzzy matches
    matched_keywords = find_fuzzy_matches(user_lower, job_lower, fuzzy_threshold)
    
    # Also check exact matches
    user_set = set(user_lower)
    job_set = set(job_lower)
    exact_matches = user_set & job_set
    matched_keywords.update(exact_matches)
    
    # Get all unique keywords (union)
    all_keywords = user_set | job_set
    
    # Calculate weighted intersection (sum of IDF weights of matched keywords)
    weighted_intersection = sum(idf_weights.get(kw, 0.1) for kw in matched_keywords)
    
    # Calculate weighted union (sum of IDF weights of all keywords)
    weighted_union = sum(idf_weights.get(kw, 0.1) for kw in all_keywords)
    
    if weighted_union == 0:
        return 0.0
    
    return weighted_intersection / weighted_union


def sigmoid_activation(x: float, center: float = 0.15, steepness: float = 20.0) -> float:
    """
    Apply sigmoid (S-curve) activation function.
    
    Maps input scores to an S-shaped curve that preserves differentiation
    between good and perfect matches without hitting a hard ceiling.
    
    Formula: f(x) = 1 / (1 + e^(-k(x - x0)))
    
    Args:
        x: Input value (0.0-1.0)
        center: Center point (x0) - the "average" expectation
        steepness: Steepness parameter (k) - how strictly to punish bad matches
    
    Returns:
        Normalized score between 0.0 and 1.0
    """
    if x <= 0:
        return 0.0
    
    # Sigmoid formula
    exponent = -steepness * (x - center)
    sigmoid = 1.0 / (1.0 + math.exp(exponent))
    
    # Normalize to ensure output is in [0, 1] range
    return max(0.0, min(1.0, sigmoid))


def calculate_cosine_baseline(jobs_database: List[Dict[str, Any]], sample_size: int = 100) -> float:
    """
    Calculate average cosine similarity baseline by sampling random job pairs.
    
    This baseline represents the "average" cosine similarity between random jobs,
    which will be used to shift scores so that average matches become 0.
    
    Args:
        jobs_database: List of job dictionaries
        sample_size: Number of random pairs to sample
        
    Returns:
        Average cosine similarity baseline (float between 0.0 and 1.0)
    """
    if len(jobs_database) < 2:
        return 0.75  # Default baseline if not enough jobs
    
    # Calculate maximum possible pairs
    max_pairs = len(jobs_database) * (len(jobs_database) - 1) // 2
    sample_pairs = min(sample_size, max_pairs)
    
    similarities = []
    
    # Sample random pairs
    for _ in range(sample_pairs):
        job1, job2 = random.sample(jobs_database, 2)
        riasec1 = job1.get('vectors', {}).get('riasec', [0.0] * 6)
        riasec2 = job2.get('vectors', {}).get('riasec', [0.0] * 6)
        
        if len(riasec1) == 6 and len(riasec2) == 6:
            sim = cosine_similarity(riasec1, riasec2)
            similarities.append(sim)
    
    if not similarities:
        return 0.75  # Default if no valid pairs found
    
    return sum(similarities) / len(similarities)


def normalize_cosine_with_baseline(
    cosine_score: float,
    baseline: float,
    min_score: float = 0.0,
    max_score: float = 1.0
) -> float:
    """
    Normalize cosine similarity by shifting baseline to 0.
    
    Maps the range [baseline, max_score] to [0.0, 1.0].
    Scores below baseline become 0.0 (clamped).
    
    Formula: normalized = (cosine_score - baseline) / (max_score - baseline)
    
    Args:
        cosine_score: Raw cosine similarity score
        baseline: Average cosine similarity baseline
        min_score: Minimum possible cosine score (default: 0.0)
        max_score: Maximum possible cosine score (default: 1.0)
        
    Returns:
        Normalized score between 0.0 and 1.0
    """
    if cosine_score < baseline:
        return 0.0
    
    # Min-max normalization: (score - baseline) / (max - baseline)
    if max_score <= baseline:
        return 1.0  # Edge case: baseline is at max
    
    normalized = (cosine_score - baseline) / (max_score - baseline)
    
    return max(0.0, min(1.0, normalized))
