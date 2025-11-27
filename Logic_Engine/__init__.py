"""
Logic Engine - Job Matching System

This module provides job matching functionality based on:
- Personality (RIASEC) similarity using cosine similarity with baseline normalization
- Knowledge domain overlap using TF-IDF weighted Jaccard similarity with fuzzy matching
- Technical skills overlap using TF-IDF weighted Jaccard similarity with fuzzy matching
- Advanced Statistical Hybrid Model with sigmoid activation
"""

from .database_loader import load_jobs_database, calculate_statistics
from .matcher import match_jobs
from .preprocessor import normalize_riasec, standardize_text, preprocess_user_profile
from .similarity import (
    cosine_similarity,
    jaccard_similarity,
    weighted_jaccard_similarity,
    sigmoid_activation,
    normalize_cosine_with_baseline,
    calculate_idf_weights,
    calculate_cosine_baseline
)
from .config import PRAGMATIC_WEIGHTS, PASSION_WEIGHTS

__all__ = [
    'load_jobs_database',
    'calculate_statistics',
    'match_jobs',
    'normalize_riasec',
    'standardize_text',
    'preprocess_user_profile',
    'cosine_similarity',
    'jaccard_similarity',
    'weighted_jaccard_similarity',
    'sigmoid_activation',
    'normalize_cosine_with_baseline',
    'calculate_idf_weights',
    'calculate_cosine_baseline',
    'PRAGMATIC_WEIGHTS',
    'PASSION_WEIGHTS',
]

