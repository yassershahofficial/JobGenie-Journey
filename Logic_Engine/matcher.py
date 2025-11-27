"""
Matcher - Phase 4-6: The Main Matching Engine

Implements the core matching algorithm:
- Phase 4: Main loop iterating through all jobs
- Phase 5: Weighted scoring combining three similarity scores
- Phase 6: Sorting and returning top N results
"""

from typing import List, Dict, Any, Optional, Tuple, Union
from .database_loader import load_jobs_database, calculate_statistics
from .preprocessor import preprocess_user_profile
from .similarity import (
    cosine_similarity,
    weighted_jaccard_similarity,
    sigmoid_activation,
    normalize_cosine_with_baseline
)
from .config import (
    WEIGHT_PERSONALITY, WEIGHT_KNOWLEDGE, WEIGHT_SKILLS, DEFAULT_TOP_N,
    PRAGMATIC_WEIGHTS, PASSION_WEIGHTS,
    SIGMOID_CENTER, SIGMOID_STEEPNESS, FUZZY_MATCH_THRESHOLD
)


def _match_jobs_with_weights(
    user_profile: Dict[str, Any],
    jobs_database: List[Dict[str, Any]],
    weights: Dict[str, float],
    top_n: int,
    statistics: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Internal helper function to match jobs with specific weights using Advanced Statistical Hybrid Model.
    
    This function performs the actual matching algorithm with given weights.
    Used by match_jobs() to run dual-track matching.
    
    Args:
        user_profile: Preprocessed user profile dictionary
        jobs_database: List of job dictionaries
        weights: Weight configuration dict with keys: personality, knowledge, skills
        top_n: Number of top results to return
        statistics: Optional pre-calculated statistics dict with 'idf_weights' and 'cosine_baseline'
                    If None, will be calculated automatically
        
    Returns:
        List of result dictionaries sorted by final_score
    """
    w_personality = weights.get('personality', 0.0)
    w_knowledge = weights.get('knowledge', 0.0)
    w_skills = weights.get('skills', 0.0)
    
    # Validate weights sum to 1.0
    total_weight = w_personality + w_knowledge + w_skills
    if abs(total_weight - 1.0) > 0.001:  # Allow small floating point errors
        raise ValueError(
            f"Weights must sum to 1.0. Got {total_weight:.3f}"
        )
    
    # Get or calculate statistics
    if statistics is None:
        statistics = calculate_statistics(jobs_database)
    
    idf_weights = statistics['idf_weights']
    cosine_baseline = statistics['cosine_baseline']
    
    results = []
    
    for job in jobs_database:
        # Station A: Personality Check (Cosine Similarity)
        job_riasec = job.get('vectors', {}).get('riasec', [0.0] * 6)
        user_riasec = user_profile.get('riasec', [0.0] * 6)
        
        # Ensure both vectors have 6 elements
        if len(job_riasec) != 6:
            job_riasec = [0.0] * 6
        if len(user_riasec) != 6:
            user_riasec = [0.0] * 6
        
        # Station A: Personality Check (Cosine Similarity with Baseline Normalization)
        raw_cosine = cosine_similarity(user_riasec, job_riasec)
        score_personality = normalize_cosine_with_baseline(raw_cosine, cosine_baseline)
        
        # Station B: Degree Check (Weighted Jaccard + Sigmoid on Knowledge Domains)
        job_knowledge = job.get('keywords', {}).get('knowledge_domains', [])
        user_knowledge = user_profile.get('knowledge_domains', [])
        
        # Standardize job knowledge domains (should already be standardized, but be safe)
        job_knowledge = [k.lower().strip() for k in job_knowledge if k]
        user_knowledge = [k.lower().strip() for k in user_knowledge if k]
        
        raw_knowledge = weighted_jaccard_similarity(
            user_knowledge,
            job_knowledge,
            idf_weights['knowledge_domains'],
            FUZZY_MATCH_THRESHOLD
        )
        score_knowledge = sigmoid_activation(raw_knowledge, SIGMOID_CENTER, SIGMOID_STEEPNESS)
        
        # Station C: Skill Check (Weighted Jaccard + Sigmoid on Tech Skills)
        job_skills = job.get('keywords', {}).get('tech_skills', [])
        user_skills = user_profile.get('tech_skills', [])
        
        # Standardize job tech skills (should already be standardized, but be safe)
        job_skills = [s.lower().strip() for s in job_skills if s]
        user_skills = [s.lower().strip() for s in user_skills if s]
        
        raw_skills = weighted_jaccard_similarity(
            user_skills,
            job_skills,
            idf_weights['tech_skills'],
            FUZZY_MATCH_THRESHOLD
        )
        score_skills = sigmoid_activation(raw_skills, SIGMOID_CENTER, SIGMOID_STEEPNESS)
        
        # Phase 5: Weighted Scoring
        final_score = (
            (score_personality * w_personality) +
            (score_knowledge * w_knowledge) +
            (score_skills * w_skills)
        )
        
        # Create result ticket (store both processed and raw scores for debugging)
        result = {
            'job_id': job.get('id', ''),
            'title': job.get('title', 'Unknown Title'),
            'description': job.get('description', 'No description available'),
            'final_score': round(final_score, 4),
            'scores': {
                'personality': round(score_personality, 4),
                'knowledge': round(score_knowledge, 4),
                'skills': round(score_skills, 4)
            },
            'raw_scores': {
                'personality': round(raw_cosine, 4),
                'knowledge': round(raw_knowledge, 4),
                'skills': round(raw_skills, 4)
            }
        }
        
        results.append(result)
    
    # Phase 6: Final Sort - Sort by final_score (highest first)
    results.sort(key=lambda x: x['final_score'], reverse=True)
    
    # Slice to top N
    return results[:top_n]


def match_jobs(
    user_profile: Dict[str, Any],
    jobs_database: Optional[List[Dict[str, Any]]] = None,
    top_n: int = DEFAULT_TOP_N,
    track: Optional[str] = None,
    weights: Optional[Dict[str, float]] = None
) -> Union[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
    """
    Match user profile against all jobs in database using dual-track logic.
    
    This function implements Phases 4-6 of the matching pipeline with dual-track support:
    
    **Track 1: Pragmatic Match (Capability)**
    - Focus: "Can I get hired?"
    - Weights: Knowledge 50%, Skills 30%, Personality 20%
    
    **Track 2: Passion Match (Compatibility)**
    - Focus: "Will I be happy?"
    - Weights: Personality 70%, Knowledge 20%, Skills 10%
    
    Phase 4: Main Loop
    - Iterates through all jobs in database
    - Station A: Personality check (cosine similarity on RIASEC)
    - Station B: Degree check (jaccard on knowledge domains)
    - Station C: Skill check (jaccard on tech skills)
    
    Phase 5: Weighted Scoring
    - Combines three scores using track-specific weights
    
    Phase 6: Final Sort
    - Sorts by final score (highest to lowest)
    - Returns top N results
    
    Args:
        user_profile: Dictionary containing:
            - riasec: List of 6 floats (1-7 scale) - will be normalized
            - knowledge_domains: List of strings
            - tech_skills: List of strings
        jobs_database: Optional pre-loaded jobs database. If None, loads from file.
        top_n: Number of top results to return per track. Default: 10
        track: Which track to use: "pragmatic", "passion", or "both" (default: "both")
        weights: Optional custom weights dict (overrides track weights) with keys:
            - personality: Weight for personality score
            - knowledge: Weight for knowledge score
            - skills: Weight for skills score
            Must sum to 1.0
        
    Returns:
        If track="both": Dictionary with keys "pragmatic" and "passion", each containing
        a list of result dictionaries.
        
        If track="pragmatic" or track="passion": List of result dictionaries.
        
        Each result dictionary contains:
            - job_id: O*NET-SOC Code
            - title: Job title
            - description: Job description
            - final_score: Combined weighted score (0.0-1.0)
            - scores: Dictionary with individual scores:
                - personality: RIASEC similarity score
                - knowledge: Knowledge domain overlap score
                - skills: Tech skills overlap score
        Sorted by final_score (highest first), limited to top_n results
    """
    # Load database if not provided
    if jobs_database is None:
        jobs_database = load_jobs_database()
    
    # Pre-calculate statistics (IDF weights, cosine baseline)
    statistics = calculate_statistics(jobs_database)
    
    # Preprocess user profile
    processed_profile = preprocess_user_profile(user_profile)
    
    # Determine default track behavior
    # - If custom weights provided without track: default to single track (backward compatible)
    # - If no weights and no track: default to "both" (dual-track)
    # - If track explicitly provided: use it
    if track is None:
        if weights is not None:
            track = "pragmatic"  # Backward compatible: custom weights = single track
        else:
            track = "both"  # New default: dual-track when no weights specified
    
    # Determine which weights to use
    if weights is not None:
        # Custom weights override track selection
        # When custom weights provided, use single track unless explicitly "both"
        if track == "both":
            # If explicitly "both" with custom weights, use same weights for both tracks
            pragmatic_results = _match_jobs_with_weights(
                processed_profile, jobs_database, weights, top_n, statistics
            )
            passion_results = _match_jobs_with_weights(
                processed_profile, jobs_database, weights, top_n, statistics
            )
            return {"pragmatic": pragmatic_results, "passion": passion_results}
        else:
            # Single track with custom weights (backward compatible - returns list)
            return _match_jobs_with_weights(
                processed_profile, jobs_database, weights, top_n, statistics
            )
    else:
        # Use track-specific weights
        if track == "both":
            # Run both tracks
            pragmatic_results = _match_jobs_with_weights(
                processed_profile, jobs_database, PRAGMATIC_WEIGHTS, top_n, statistics
            )
            passion_results = _match_jobs_with_weights(
                processed_profile, jobs_database, PASSION_WEIGHTS, top_n, statistics
            )
            return {"pragmatic": pragmatic_results, "passion": passion_results}
        elif track == "pragmatic":
            return _match_jobs_with_weights(
                processed_profile, jobs_database, PRAGMATIC_WEIGHTS, top_n, statistics
            )
        elif track == "passion":
            return _match_jobs_with_weights(
                processed_profile, jobs_database, PASSION_WEIGHTS, top_n, statistics
            )
        else:
            raise ValueError(
                f"Invalid track value: {track}. Must be 'pragmatic', 'passion', or 'both'"
            )

